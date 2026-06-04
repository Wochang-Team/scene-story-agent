# 처리 흐름

## 1. 문서 목적

이 문서는 `scene-story-agent`의 프로젝트 고유 처리 흐름을 정리한다.

- 포함 범위:
  - 기록 생성 후 처리 흐름
  - 파일 업로드와 썸네일 생성 위치
  - AI 비동기 작업 등록과 Worker 처리
  - 재시도 기준
  - UI 상태 조회와 화면 갱신
  - 처리 데이터 확인 화면의 API 호출 흐름
- 제외 범위:
  - 인프라 구성 선택 이유
  - 테이블, 컬럼, 제약 상세
  - 로컬 실행 명령
  - 제품 목표와 사용자 문제
- 참조:
  - 인프라 구성 기준: `docs/development-infra.md`
  - 상태값과 SQL 정본 기준: `docs/database-design.md`
  - 로컬 실행 기준: `docs/fastapi-quickstart.md`
  - 사용자 경험 기준: `docs/product-spec.md`

## 2. 전체 흐름

사진 기록 1건은 API 서버와 Worker가 나누어 처리한다.

1. 사용자가 사진과 메모를 등록한다.
2. API 서버가 원본 기록을 `processing` 상태로 저장한다.
3. API 서버가 원본 파일을 저장한다.
4. 업로드 파일이 사진이면 API 서버가 썸네일을 생성한다.
5. API 서버가 `processing_jobs`에 `extract_ai_interpretation` 작업을 등록한다.
6. 클라이언트가 `GET /jobs/records/{record_id}`를 1초 주기로 조회한다.
7. Worker가 실행 가능한 작업을 조회한다.
8. Worker가 Redis lock을 잡고 작업을 `running`으로 바꾼다.
9. Worker가 AI 해석, 임베딩, 연관 기록 후보, 타임라인 후보를 순차 처리한다.
10. 성공하면 Worker가 작업을 `succeeded`, 기록을 `ready`로 바꾼다.
11. 실패하면 재시도 기준에 따라 `retrying` 또는 `failed`로 바꾼다.
12. 클라이언트는 완료 상태를 확인한 뒤 최신 기록과 파생 데이터를 다시 조회한다.

## 3. API 서버 책임

API 서버는 사용자 요청을 받고 오래 걸리는 처리는 작업으로 넘긴다.

- 기록 생성:
  - 사용자 입력값을 검증한다.
  - `records.status`를 `processing`으로 저장한다.
  - `extract_ai_interpretation` 작업을 등록한다.
- 파일 업로드:
  - 파일 크기와 MIME type을 검증한다.
  - 원본 파일을 저장소에 저장한다.
  - 사진 파일이면 업로드 단계에서 썸네일을 생성한다.
  - `record_assets`에 원본과 썸네일 메타데이터를 저장한다.
- 상태 조회:
  - 기록 목록과 상세를 반환한다.
  - 작업 상태를 반환한다.
  - AI 해석, 연관 기록, 타임라인 후보 조회를 제공한다.
- 재시도:
  - 실패 기록의 재시도 요청을 받는다.
  - 기록 상태를 `processing`으로 되돌린다.
  - 새 작업 또는 기존 활성 작업을 반환한다.

## 4. Worker 책임

Worker는 `processing_jobs`를 기준으로 비동기 작업을 처리한다.

- 조회 기준:
  - 대상 작업: `extract_ai_interpretation`
  - 대상 상태: `queued`, `retrying`
  - 실행 가능 시각: `available_at <= now()`
  - 조회 주기: 실행 가능한 작업이 없으면 1초 대기
- 실행 기준:
  - Redis `job:lock:{job_id}`로 같은 작업의 동시 실행을 완화한다.
  - 작업을 `running`으로 바꾼 뒤 처리한다.
  - AI 해석 정보를 저장한다.
  - 기존 활성 임베딩을 삭제 처리한다.
  - 현재 기록이 source인 연관 후보를 숨긴다.
  - 현재 기록의 타임라인 후보를 삭제한다.
  - 새 임베딩, 연관 기록 후보, 타임라인 후보를 생성한다.
- 완료 기준:
  - 성공 시 작업은 `succeeded`, 기록은 `ready`가 된다.
  - 최종 실패 시 작업은 `failed`, 기록은 `failed`가 된다.

## 5. 재시도 기준

재시도는 작업 상태와 실행 가능 시각으로 관리한다.

- 1회 실패:
  - `attempt_count = 1`
  - `status = retrying`
  - 10초 뒤 실행 가능
- 2회 실패:
  - `attempt_count = 2`
  - `status = retrying`
  - 30초 뒤 실행 가능
- 3회 실패:
  - `attempt_count = 3`
  - `status = failed`
  - 기록 상태도 `failed`
- 재시도 버튼:
  - 개발용 상세 화면에서 `재시도 필요` 뱃지로 노출한다.
  - 클릭 시 `POST /records/{record_id}/ai-analysis/retry`를 호출한다.
  - 호출 후 화면은 다시 작업 상태를 polling한다.

## 6. UI 상태 조회

UI는 서버 push가 아니라 polling으로 처리 상태를 확인한다.

- 조회 API:
  - `GET /jobs/records/{record_id}`
- 조회 주기:
  - 1초
- 대기 상태:
  - `queued`
  - `running`
  - `retrying`
- 완료 상태:
  - `succeeded`
- 실패 상태:
  - `failed`
- 완료 후 갱신:
  - 기록 목록을 다시 조회한다.
  - 선택 기록 상세를 다시 조회한다.
  - AI 해석 정보를 다시 조회한다.
  - 저장 JSON, 연관 기록, 타임라인 후보를 다시 조회한다.
- 실패 후 갱신:
  - 기록 목록과 상세를 다시 조회한다.
  - 개발용 화면에 `재시도 필요`를 표시한다.

## 7. 처리 데이터 확인 화면 호출 흐름

처리 데이터 확인 화면은 선택한 기록의 저장 결과를 조회 API로 모아 보여준다.

- 대상 화면:
  - `GET /ui/upload`
- 호출 기준:
  - 화면 진입 시 기록 목록을 먼저 조회한다.
  - 사용자가 기록을 선택하면 선택 기록의 상세 데이터와 파생 데이터를 함께 조회한다.
  - AI 해석이 없을 수 있는 항목은 없는 상태를 허용한다.
  - 저장 JSON은 처리 결과 원문 확인용으로 사용한다.

| 단계 | Method | URL | 용도 |
|---|---:|---|---|
| 목록 조회 | GET | `/records` | 화면에 표시할 기록 목록을 가져온다. |
| 기록 선택 | GET | `/records/{record_id}` | 선택한 기록의 기본 정보를 가져온다. |
| 기록 선택 | GET | `/records/{record_id}/assets` | 원본 파일과 썸네일 목록을 가져온다. |
| 기록 선택 | GET | `/records/{record_id}/ai-analysis` | 최신 AI 해석 데이터를 가져온다. |
| 기록 선택 | GET | `/records/{record_id}/relations` | 연관 기록 후보를 가져온다. |
| 기록 선택 | GET | `/records/{record_id}/timeline-candidates` | 타임라인 후보를 가져온다. |
| 기록 선택 | GET | `/records/{record_id}/storage-json` | 저장된 처리 데이터 전체를 가져온다. |
| 상태 확인 | GET | `/jobs/records/{record_id}` | 처리 작업 상태를 polling한다. |

- 병렬 조회 묶음:
  - `GET /records/{record_id}`
  - `GET /records/{record_id}/assets`
  - `GET /records/{record_id}/ai-analysis`
  - `GET /records/{record_id}/relations`
  - `GET /records/{record_id}/timeline-candidates`
  - `GET /records/{record_id}/storage-json`
- 재처리 호출:
  - `POST /records/{record_id}/ai-analysis/retry`: 실패한 AI 해석 작업을 다시 등록한다.
  - `POST /records/{record_id}/embedding`: 기존 AI 해석 기준으로 임베딩, 연관 기록, 타임라인 후보를 다시 생성한다.

## 8. 상태 노출 기준

개발용 화면과 실사용자 화면은 상태 노출 기준을 분리한다.

- 개발용 화면:
  - `processing`은 `분석 대기`로 표시한다.
  - `failed`는 `재시도 필요`로 표시한다.
  - 실패 기록도 삭제와 재시도를 위해 목록과 상세에 표시한다.
- 실사용자 화면:
  - `ready` 상태의 기록만 기본 노출한다.
  - `processing`, `failed`, `deleted`는 기본 목록에서 제외한다.

## 이력관리

- 2026-06-03: 처리 데이터 확인 화면의 API 호출 흐름과 병렬 조회 묶음 추가
- 2026-06-02: 기록 업로드, AI 비동기 처리, Worker polling, 재시도, UI polling 기준 문서 신설
