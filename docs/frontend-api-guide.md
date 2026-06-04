# 프론트엔드 API 연동 가이드

## 1. 문서 목적

이 문서는 프론트엔드 개발자가 로컬 API와 연동할 때 필요한 호출 기준만 정리한다.

- 대상:
  - 로컬 MVP 화면 개발
  - 처리 데이터 확인 화면 개발
  - API 응답 구조 확인
- 제외:
  - DB 테이블 상세
  - Worker 내부 구현
  - Redis lock 처리
  - 운영 배포 절차
- 정본 기준:
  - request/response schema: `http://127.0.0.1:8000/openapi.json`
  - API 동작 확인: `http://127.0.0.1:8000/docs`
  - 처리 흐름 상세: `docs/processing-flow.md`

## 2. API 스펙 확인

FastAPI가 현재 실행 중인 API 스펙을 자동으로 제공한다.

| 용도 | URL |
|---|---|
| OpenAPI JSON | `http://127.0.0.1:8000/openapi.json` |
| Swagger UI | `http://127.0.0.1:8000/docs` |
| ReDoc | `http://127.0.0.1:8000/redoc` |

- 기준:
  - `openapi.json`은 프론트 타입 생성과 request/response schema 확인에 사용한다.
  - `/docs`는 API를 직접 실행하며 확인할 때 사용한다.
  - `127.0.0.1`은 API 서버가 실행 중인 PC 안에서만 유효하다.
- 외부 접근:
  - 다른 PC에서 접근하려면 API 서버를 외부 접근 가능한 host로 실행해야 한다.
  - 브라우저에서 다른 origin으로 직접 호출하면 CORS 설정이 필요하다.

## 3. 공통 호출 기준

프론트 요청은 로컬 사용자 헤더를 함께 보낸다.

- Base URL:
  - `http://127.0.0.1:8000`
- 공통 헤더:
  - `X-Local-User: local-user`
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

## 4. 처리 데이터 확인 화면

처리 데이터 확인 화면은 기록을 선택한 뒤 관련 조회 API를 함께 호출한다.

- 로컬 화면:
  - `GET /ui/upload`
- 화면 진입:
  - `GET /records`
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

## 5. 업로드와 처리 상태

업로드 후 처리는 작업 상태를 polling해서 확인한다.

| 순서 | Method | URL | 용도 |
|---:|---:|---|---|
| 1 | POST | `/records` | 기록을 생성한다. |
| 2 | POST | `/records/{record_id}/assets` | 파일을 업로드한다. |
| 3 | GET | `/jobs/records/{record_id}` | 작업 상태를 1초 주기로 조회한다. |
| 4 | GET | `/records/{record_id}/storage-json` | 완료 후 저장 결과를 확인한다. |

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

## 6. 상태 처리 기준

프론트는 기록 상태와 작업 상태를 분리해서 표시한다.

| 구분 | 값 | 표시 기준 |
|---|---|---|
| 기록 상태 | `processing` | 분석 대기 또는 처리 중 |
| 기록 상태 | `ready` | 처리 완료 |
| 기록 상태 | `failed` | 재시도 필요 |
| 작업 상태 | `queued` | 대기 중 |
| 작업 상태 | `running` | 실행 중 |
| 작업 상태 | `retrying` | 자동 재시도 대기 |
| 작업 상태 | `succeeded` | 작업 성공 |
| 작업 상태 | `failed` | 작업 실패 |

- polling 기준:
  - 대상 API: `GET /jobs/records/{record_id}`
  - 주기: 1초
  - 종료 조건: 최신 작업이 `succeeded` 또는 `failed`
- 완료 후 갱신:
  - `GET /records`
  - `GET /records/{record_id}`
  - `GET /records/{record_id}/ai-analysis`
  - `GET /records/{record_id}/relations`
  - `GET /records/{record_id}/timeline-candidates`
  - `GET /records/{record_id}/storage-json`

## 7. 재처리 호출

재처리는 사용자가 명시적으로 실행할 때만 호출한다.

| 용도 | Method | URL |
|---|---:|---|
| 실패한 AI 해석 재시도 | POST | `/records/{record_id}/ai-analysis/retry` |
| 기존 AI 해석 기준 임베딩 재생성 | POST | `/records/{record_id}/embedding` |

- AI 해석 재시도:
  - 실패한 기록에서 사용한다.
  - 호출 후 `GET /jobs/records/{record_id}` polling을 다시 시작한다.
- 임베딩 재생성:
  - 기존 AI 해석이 있는 기록에서 사용한다.
  - 응답에는 새 임베딩, 연관 기록 후보, 타임라인 후보가 포함된다.

## 8. 주요 조회 API

프론트 화면에서 자주 쓰는 조회 API는 다음이다.

| Method | URL | 용도 |
|---:|---|---|
| GET | `/records` | 기록 목록 |
| GET | `/records/{record_id}` | 기록 상세 |
| PATCH | `/records/{record_id}` | 메모, 감정, 만족도, 발생 시각 수정 |
| DELETE | `/records/{record_id}` | 기록 삭제 |
| GET | `/records/{record_id}/assets` | 업로드 파일 목록 |
| GET | `/records/{record_id}/assets/{asset_id}/file` | 원본 파일 또는 썸네일 표시 |
| GET | `/records/{record_id}/ai-analysis` | AI 해석 데이터 |
| GET | `/records/{record_id}/relations` | 연관 기록 후보 |
| GET | `/records/{record_id}/timeline-candidates` | 타임라인 후보 |
| GET | `/records/{record_id}/storage-json` | 저장 처리 데이터 전체 |
| GET | `/jobs/records/{record_id}` | 작업 상태 목록 |

## 9. 구현 체크리스트

프론트 구현 전 아래 항목만 확인한다.

- API 서버:
  - `http://127.0.0.1:8000/health` 응답 확인
  - `http://127.0.0.1:8000/openapi.json` 접근 확인
- 공통 요청:
  - `X-Local-User` 헤더 적용
  - JSON 요청의 `Content-Type` 적용
  - 파일 업로드는 `FormData` 사용
- 화면 처리:
  - 선택 기록 조회 API는 병렬 호출
  - AI 해석과 저장 JSON의 `404`는 빈 상태로 처리
  - 작업 상태는 1초 polling
  - 완료 또는 실패 후 화면 데이터 재조회
- 브라우저 분리 실행:
  - 프론트 dev server와 API origin이 다르면 CORS 설정 확인

## 이력관리

- 2026-06-03: 프론트엔드 API 연동 가이드 문서 생성
