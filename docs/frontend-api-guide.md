# 프론트엔드 API 연동 가이드

## 1. 문서 목적

이 문서는 프론트엔드가 로컬 MVP 화면과 같은 기능을 구현할 때 필요한 API 계약과 화면 구현 항목을 정리한다.

- 대상:
  - 로컬 MVP 업로드 화면 구현
  - 기록 목록, 상세, 처리 데이터 확인 화면 구현
  - API 응답 구조 확인
  - `/ui/upload` 화면에 이미 구현된 기능을 별도 프론트로 옮기는 작업
- 제외:
  - DB 테이블 상세
  - Worker 내부 구현
  - Redis lock 처리
  - 운영 배포 절차
- 정본 기준:
  - request/response schema: `http://127.0.0.1:8000/openapi.json`
  - API 동작 확인: `http://127.0.0.1:8000/docs`
  - 현재 로컬 검증 화면: `http://127.0.0.1:8000/ui/upload`
  - 처리 흐름 상세: `docs/processing-flow.md`

## 2. API 스펙 확인

FastAPI가 현재 실행 중인 API 스펙을 자동으로 제공한다.

| 용도 | URL |
|---|---|
| OpenAPI JSON | `http://127.0.0.1:8000/openapi.json` |
| Swagger UI | `http://127.0.0.1:8000/docs` |
| ReDoc | `http://127.0.0.1:8000/redoc` |
| 로컬 MVP 화면 | `http://127.0.0.1:8000/ui/upload` |

- 기준:
  - `openapi.json`은 프론트 타입 생성과 request/response schema 확인에 사용한다.
  - `/docs`는 API를 직접 실행하며 확인할 때 사용한다.
  - `/ui/upload`는 프론트 구현 항목과 표시 방식을 확인할 때 사용한다.
  - `127.0.0.1`은 API 서버가 실행 중인 PC 안에서만 유효하다.
- 외부 접근:
  - 다른 PC에서 접근하려면 API 서버를 외부 접근 가능한 host로 실행해야 한다.
  - 브라우저에서 다른 origin으로 직접 호출하면 CORS 설정이 필요하다.

## 3. 공통 호출 기준

프론트 요청은 로컬 사용자 헤더를 함께 보낸다.

- Base URL:
  - `http://127.0.0.1:8000`
- 공통 헤더 이름:
  - `X-Local-User`
- 로컬 MVP 기본 사용자:
  - `/ui/upload` 기본값은 `local-mvp`다.
  - 별도 프론트에서도 사용자 입력값이 비어 있으면 기본 사용자 값을 사용한다.
- 사용자 구분:
  - `X-Local-User` 값이 같으면 같은 로컬 사용자로 처리한다.
  - 헤더를 생략하면 서버가 `local-user`로 처리한다.
  - 빈 문자열은 허용하지 않는다.
- JSON 요청:
  - `Content-Type: application/json`
- 파일 업로드:
  - `multipart/form-data`
  - form field 이름: `file`
  - 브라우저 `FormData` 사용 시 `Content-Type`은 직접 지정하지 않는다.

## 4. 화면 구성 기준

프론트는 현재 `/ui/upload` 화면의 사용자 화면과 처리 데이터 확인 화면을 모두 구현 대상으로 본다.

- 사용자 화면:
  - 업로드 화면
  - 목록
  - 상세
- 처리 데이터 확인 화면:
  - 처리 상태 화면
  - AI 해석 데이터
  - 임베딩/연관 데이터
  - 타임라인 후보 데이터
  - 저장 JSON 데이터
- 화면 진입 시 호출:
  - `GET /records`
  - 각 기록별 `GET /records/{record_id}/ai-analysis`
  - 각 기록별 `GET /records/{record_id}/assets`
- 기록 선택 후 병렬 조회:
  - `GET /records/{record_id}`
  - `GET /records/{record_id}/assets`
  - `GET /records/{record_id}/ai-analysis`
  - `GET /records/{record_id}/relations`
  - `GET /records/{record_id}/timeline-candidates`
  - `GET /records/{record_id}/storage-json`
- 없는 상태 허용:
  - `GET /records/{record_id}/ai-analysis`는 AI 해석이 없으면 `404`가 날 수 있다.
  - `GET /records/{record_id}/storage-json`도 저장 데이터가 없으면 `404`가 날 수 있다.
  - 프론트는 위 두 API의 `404`를 빈 상태로 표시한다.

## 5. 업로드 입력 항목

업로드 화면은 기록 생성 값과 업로드 파일을 함께 입력받는다.

| 항목 | 프론트 입력 | API 필드 | 기본값 | 구현 기준 |
|---|---|---|---|---|
| 로컬 사용자 | text input | header `X-Local-User` | `local-mvp` | 모든 API 요청에 같은 값을 보낸다. |
| 메모 | textarea | `memo` | `null` | 빈 문자열은 `null`로 보낸다. |
| 감정 | radio | `emotion` | `joy` | 아래 감정 선택지를 그대로 제공한다. |
| 만족도 | radio | `satisfaction_score` | `5` | `1`부터 `5`까지 숫자로 보낸다. |
| 방문 사진 | file input | form field `file` | 없음 | 여러 파일을 선택할 수 있다. |
| 대표사진 | image picker | 업로드 순서 | 첫 이미지 | 대표로 선택한 이미지를 가장 먼저 업로드한다. |

- 파일 허용 형식:
  - `image/jpeg`
  - `image/png`
  - `image/webp`
  - `video/mp4`
  - `video/quicktime`
- 대표사진 선택:
  - 이미지 파일이 1개 이상이면 대표사진 선택 UI를 표시한다.
  - 이미지 파일이 없으면 대표사진 선택 UI를 표시하지 않는다.
  - 대표사진은 서버 별도 필드로 전달하지 않는다.
  - 대표사진은 업로드 순서를 조정해서 첫 번째 파일로 보낸다.
- 업로드 전 검증:
  - 파일은 1개 이상 필요하다.
  - 서버가 허용하지 않는 파일 형식은 `415`로 실패할 수 있다.
  - 서버 파일 크기 제한을 넘으면 `413`으로 실패할 수 있다.

## 6. 감정 이모지 선택지

감정은 API 값과 화면 이모지를 분리해서 관리한다.

| API 값 | 화면 이모지 | 라벨 |
|---|---:|---|
| `joy` | 😊 | 기쁨 |
| `calm` | 😐 | 평온 |
| `sad` | 😢 | 슬픔 |
| `angry` | 😠 | 화남 |
| `tired` | 😴 | 피곤 |

- 입력 기준:
  - `POST /records`와 `PATCH /records/{record_id}`에는 이모지가 아니라 API 값을 보낸다.
  - 기본 선택값은 `joy`다.
- 표시 기준:
  - 목록과 상세 태그에는 API 값을 이모지로 변환해서 표시한다.
  - 알 수 없는 값은 표시하지 않는다.
  - 접근성 라벨에는 라벨 텍스트를 함께 제공한다.

## 7. 업로드와 처리 상태

업로드 후 처리는 작업 상태를 polling해서 확인한다.

| 순서 | Method | URL | 용도 |
|---:|---:|---|---|
| 1 | POST | `/records` | 기록을 생성하고 AI 해석 작업을 등록한다. |
| 2 | POST | `/records/{record_id}/assets` | 파일을 1개씩 업로드한다. |
| 3 | GET | `/jobs/records/{record_id}` | 작업 상태를 1초 주기로 조회한다. |
| 4 | GET | `/records/{record_id}/ai-analysis` | 완료 후 AI 해석 결과를 조회한다. |
| 5 | GET | `/records/{record_id}/storage-json` | 저장 결과 전체를 확인한다. |

- `POST /records` 요청 예시:

```json
{
  "memo": "카페에서 작업한 기록",
  "emotion": "calm",
  "satisfaction_score": 4,
  "happened_at": null
}
```

- `satisfaction_score`:
  - 허용 범위: `1`부터 `5`
  - 값이 없으면 `null`
- 파일 업로드:
  - 파일마다 `POST /records/{record_id}/assets`를 1회 호출한다.
  - 사진 파일이면 서버가 업로드 처리 중 썸네일을 함께 만든다.
  - 썸네일 생성은 별도 API를 호출하지 않는다.
- 처리 상태 화면:
  - 원본 기록 저장
  - 원본 파일 업로드
  - AI 해석 저장
  - 썸네일 저장
  - 임베딩 저장
  - 연관 기록 저장
  - 타임라인 후보 저장
  - 저장 JSON 조회
- 상태 보조 표시:
  - 호출한 API의 `curl` 예시
  - 단계별 처리 시간
  - AI 응답의 토큰 사용량과 남은 토큰

## 8. 목록 화면 구현

목록은 기록을 선택하고 상태를 빠르게 확인할 수 있게 표시한다.

- 호출 기준:
  - `GET /records`
  - 목록의 각 기록에 대해 `GET /records/{record_id}/ai-analysis`
  - 목록의 각 기록에 대해 `GET /records/{record_id}/assets`
- 표시 항목:
  - 대표 썸네일
  - 제목
  - 메모 또는 활동 요약
  - 생성 또는 발생 시각
  - 상태 태그
  - 감정 이모지
  - 만족도 점수
  - 대표 메뉴명
  - 삭제 버튼
- 제목 우선순위:
  - 장소명과 방문 회차
  - 장소명
  - `scene_type`
  - 활동 후보
  - 메모
  - `새 기록`
- 부제 우선순위:
  - 메모가 있으면 `📝 {memo}` 형식으로 표시한다.
  - 메모가 없으면 대표 활동 또는 AI 요약을 표시한다.
  - 둘 다 없으면 `요약 없음`을 표시한다.
- 대표 썸네일:
  - 이미지 asset 중 `asset_type`이 `thumbnail`인 항목을 우선 사용한다.
  - 썸네일이 없으면 첫 이미지 asset을 사용한다.
  - 이미지 asset이 없으면 썸네일을 표시하지 않는다.
- 삭제:
  - `DELETE /records/{record_id}`를 호출한다.
  - 사용자 확인 후 삭제한다.
  - 선택 중인 기록이 삭제되면 상세와 처리 데이터 영역을 비운다.

## 9. 상세 화면 구현

상세는 선택한 기록의 사용자 입력, AI 해석, 파일, 연관 기록을 함께 표시한다.

- 호출 기준:
  - `GET /records/{record_id}`
  - `GET /records/{record_id}/assets`
  - `GET /records/{record_id}/ai-analysis`
  - `GET /records/{record_id}/relations`
  - `GET /records/{record_id}/timeline-candidates`
  - `GET /records/{record_id}/storage-json`
- 상단 표시:
  - 목록과 같은 제목 규칙
  - 감정 이모지
  - 만족도 점수
  - 대표 메뉴명
  - 기록 상태
- 상세 정보:
  - 메모
  - 시간
  - 메뉴
  - 태그
  - 활동내역
  - AI 요약
- 메모 수정:
  - 수정 버튼은 ✏️ 아이콘으로 표시한다.
  - 저장은 `PATCH /records/{record_id}`로 호출한다.
  - 요청 body는 `{ "memo": "수정 메모" }` 형식을 사용한다.
  - 빈 메모는 `null`로 보낸다.
- 업로드 파일:
  - 원본 파일을 기준으로 카드 목록을 표시한다.
  - 이미지 원본은 같은 순서의 썸네일을 미리보기로 사용한다.
  - 비이미지 파일은 미리보기를 표시하지 않는다.
  - 파일 클릭 시 `GET /records/{record_id}/assets/{asset_id}/file`로 원본을 새 창에서 연다.
  - 파일 크기는 KB 단위로 표시한다.
- 연관 기록:
  - `GET /records/{target_record_id}`로 대상 기록을 추가 조회한다.
  - 표시 개수는 최대 3건이다.
  - 관계 유형과 유사도 점수를 태그로 표시한다.

## 10. AI 해석 데이터 화면 구현

AI 해석 데이터 화면은 원본 AI 응답 필드를 확인할 수 있게 표시한다.

- 호출 기준:
  - 조회: `GET /records/{record_id}/ai-analysis`
  - 수동 생성: `POST /records/{record_id}/ai-analysis`
- 버튼:
  - `AI 생성`
  - 선택 기록이 없으면 실행하지 않는다.
  - 호출 성공 후 목록, 상세, 처리 데이터 영역을 다시 조회한다.
- 메타 표시:
  - `model`
  - `scene_type`
- 데이터 행:
  - `place_candidates`
  - `visit_time_candidates`
  - `menu_candidates`
  - `amount_candidates`
  - `activity_candidates`
  - `similar_record_candidates`
  - `revisit_candidates`
  - `timeline_candidates`
  - `tags`
  - `raw_response_ref`
- 도움말:
  - 각 데이터 행에는 `❓` 도움말 아이콘을 표시한다.
  - 도움말에는 필드 의미를 짧게 설명한다.
- 빈 상태:
  - AI 해석이 없으면 `AI 해석 데이터가 없습니다.`를 표시한다.

## 11. 임베딩/연관 데이터 화면 구현

임베딩/연관 데이터 화면은 기존 AI 해석을 기반으로 만든 관계 데이터를 표시한다.

- 호출 기준:
  - 조회: `GET /records/{record_id}/relations`
  - 생성: `POST /records/{record_id}/embedding`
  - 저장 JSON 보조 조회: `GET /records/{record_id}/storage-json`
- 버튼:
  - `기존 AI로 생성`
  - 선택 기록이 없으면 실행하지 않는다.
  - 호출 성공 후 목록, 상세, 처리 데이터 영역을 다시 조회한다.
- 메타 표시:
  - 임베딩 모델
  - 임베딩 차원
  - 연관 데이터 건수
- 데이터 행:
  - `relation_type`
  - `target_record_id`
  - `similarity_score`
  - `decision_status`
  - `created_at`
  - `reasons`
- 빈 상태:
  - 연관 데이터가 없으면 `연관 데이터가 없습니다.`를 표시한다.

## 12. 타임라인 후보 데이터 화면 구현

타임라인 후보 데이터 화면은 임베딩 생성 시 함께 만들어진 후보를 표시한다.

- 호출 기준:
  - 조회: `GET /records/{record_id}/timeline-candidates`
  - 생성: `POST /records/{record_id}/embedding`
- 표시 기준:
  - 임베딩 모델을 메타 태그로 표시한다.
  - 별도 생성 버튼은 두지 않는다.
  - 화면에는 `임베딩 생성 시 함께 생성` 안내를 표시한다.
- 데이터 행:
  - `timeline_type`
  - `grouping_key`
  - `confidence_score`
  - `reason`
  - `created_at`
- 빈 상태:
  - 타임라인 후보가 없으면 `타임라인 후보 데이터가 없습니다.`를 표시한다.

## 13. 저장 JSON 화면 구현

저장 JSON 화면은 현재 기록의 저장 데이터를 원문에 가깝게 표시한다.

- 호출 기준:
  - `GET /records/{record_id}/storage-json`
- 표시 기준:
  - 응답 전체를 pretty JSON으로 표시한다.
  - 저장 JSON이 없으면 `storage-json 없음`을 표시한다.
  - 업로드 처리 중에는 `처리 중`을 표시한다.
  - 삭제 후에는 `기록이 삭제되었습니다.`를 표시한다.
- 완료 후 계산:
  - `record_embeddings` 중 `deleted_at`이 없는 항목을 활성 임베딩으로 본다.
  - `record_relations` 중 `decision_status`가 `hidden`이 아닌 항목을 활성 연관 기록으로 본다.
  - `timeline_candidates` 개수를 타임라인 후보 저장 결과로 표시한다.

## 14. 상태 처리 기준

프론트는 기록 상태와 작업 상태를 분리해서 표시한다.

| 구분 | 값 | 표시 기준 |
|---|---|---|
| 기록 상태 | `processing` | 분석 대기 |
| 기록 상태 | `ready` | 준비완료 |
| 기록 상태 | `failed` | 재시도 필요 |
| 기록 상태 | `draft` | 초안 |
| 작업 상태 | `queued` | 대기 중 |
| 작업 상태 | `running` | 실행 중 |
| 작업 상태 | `retrying` | 자동 재시도 대기 |
| 작업 상태 | `succeeded` | 작업 성공 |
| 작업 상태 | `failed` | 작업 실패 |

- polling 기준:
  - 대상 API: `GET /jobs/records/{record_id}`
  - 대상 작업: `job_type`이 `extract_ai_interpretation`인 작업
  - 주기: 1초
  - 종료 조건: 최신 작업이 `succeeded` 또는 `failed`
- `retrying` 표시:
  - `available_at`이 있으면 다음 시도까지 남은 초를 표시한다.
- 실패 표시:
  - 작업 실패 시 `last_error_code`와 `last_error_message`를 사용한다.
  - 처리 중이던 단계는 실패 상태로 표시한다.
- 완료 후 갱신:
  - `GET /records`
  - `GET /records/{record_id}`
  - `GET /records/{record_id}/assets`
  - `GET /records/{record_id}/ai-analysis`
  - `GET /records/{record_id}/relations`
  - `GET /records/{record_id}/timeline-candidates`
  - `GET /records/{record_id}/storage-json`

## 15. 재처리 호출

재처리는 사용자가 명시적으로 실행할 때만 호출한다.

| 용도 | Method | URL |
|---|---:|---|
| AI 해석 수동 생성 | POST | `/records/{record_id}/ai-analysis` |
| 실패한 AI 해석 재시도 | POST | `/records/{record_id}/ai-analysis/retry` |
| 기존 AI 해석 기준 임베딩 재생성 | POST | `/records/{record_id}/embedding` |

- AI 해석 수동 생성:
  - 선택한 기록에서 사용한다.
  - 호출 성공 후 AI 해석 데이터와 화면 데이터를 다시 조회한다.
- AI 해석 재시도:
  - `failed` 상태 기록에서 사용한다.
  - 호출 후 `GET /jobs/records/{record_id}` polling을 다시 시작한다.
- 임베딩 재생성:
  - 기존 AI 해석이 있는 기록에서 사용한다.
  - 응답에는 새 임베딩, 연관 기록 후보, 타임라인 후보가 포함된다.

## 16. 주요 조회 API

프론트 화면에서 자주 쓰는 API는 다음이다.

| Method | URL | 용도 |
|---:|---|---|
| POST | `/records` | 기록 생성 |
| GET | `/records` | 기록 목록 |
| GET | `/records/{record_id}` | 기록 상세 |
| PATCH | `/records/{record_id}` | 메모, 감정, 만족도, 발생 시각 수정 |
| DELETE | `/records/{record_id}` | 기록 삭제 |
| POST | `/records/{record_id}/assets` | 원본 파일 업로드 |
| GET | `/records/{record_id}/assets` | 업로드 파일 목록 |
| GET | `/records/{record_id}/assets/{asset_id}/file` | 원본 파일 또는 썸네일 표시 |
| GET | `/records/{record_id}/ai-analysis` | AI 해석 데이터 조회 |
| POST | `/records/{record_id}/ai-analysis` | AI 해석 수동 생성 |
| POST | `/records/{record_id}/ai-analysis/retry` | AI 해석 재시도 |
| POST | `/records/{record_id}/embedding` | 임베딩, 연관 기록, 타임라인 후보 생성 |
| GET | `/records/{record_id}/relations` | 연관 기록 후보 |
| GET | `/records/{record_id}/timeline-candidates` | 타임라인 후보 |
| GET | `/records/{record_id}/storage-json` | 저장 처리 데이터 전체 |
| GET | `/jobs/records/{record_id}` | 작업 상태 목록 |

## 17. 구현 체크리스트

프론트 구현 전 아래 항목만 확인한다.

- API 서버:
  - `http://127.0.0.1:8000/health` 응답 확인
  - `http://127.0.0.1:8000/openapi.json` 접근 확인
  - `http://127.0.0.1:8000/ui/upload` 화면 동작 확인
- 공통 요청:
  - `X-Local-User` 헤더 적용
  - JSON 요청의 `Content-Type` 적용
  - 파일 업로드는 `FormData` 사용
- 업로드 화면:
  - 로컬 사용자 입력 구현
  - 메모 입력 구현
  - 감정 이모지 선택지 구현
  - 만족도 `1`부터 `5`까지 구현
  - 허용 파일 형식 적용
  - 대표사진 선택과 업로드 순서 조정 구현
- 목록 화면:
  - 대표 썸네일 표시
  - 제목, 부제, 날짜, 태그 표시
  - 삭제 버튼 구현
  - 기록 선택 시 상세 조회
- 상세 화면:
  - 메모 수정 구현
  - 업로드 파일 미리보기와 원본 열기 구현
  - 연관 기록 최대 3건 표시
- 처리 데이터 화면:
  - 선택 기록 조회 API는 병렬 호출
  - AI 해석과 저장 JSON의 `404`는 빈 상태로 처리
  - 작업 상태는 1초 polling
  - 수동 AI 생성, 재시도, 임베딩 생성 버튼 구현
  - 완료 또는 실패 후 화면 데이터 재조회
- 브라우저 분리 실행:
  - 프론트 dev server와 API origin이 다르면 CORS 설정 확인

## 이력관리

- 2026-06-03: 프론트엔드 API 연동 가이드 문서 생성
- 2026-06-04: `/ui/upload` 화면 기준으로 감정 이모지, 업로드 입력, 목록, 상세, 처리 데이터 화면 구현 항목 추가
