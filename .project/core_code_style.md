# scene-story-agent 코딩 스타일

## 문서 메타
이 문서는 Python 코드 작성 기준을 정리한다.

- 생성일: 2026-05-21
- 목적: Python 코드 작성 기준을 프로젝트 관례에 맞게 정리한다.
- 문서 성격: 구현 규칙 문서
- 책임 범위(정본): 네이밍, 타입 힌트, 패키지 배치, 모델/스키마, 오류 처리, 로깅, 테스트 작성 스타일의 최종 기준
- 포함 범위: 모듈 네이밍, 타입 힌트, 모델/스키마, 서비스/API 작성 기준, 오류/로그/테스트 스타일
- 제외 범위: 실행 명령, 배포 절차, 전체 아키텍처 설명
- 연계 문서: `.project/core_project.md`, `.project/core_workflow.md`
- 중복 방지 기준:
  - 구조와 런타임 설명은 `.project/core_project.md`에만 기록한다.
  - 실행 명령과 환경 변수는 `.project/core_workflow.md`에만 기록한다.
  - 제품 상세와 개인정보 정책은 `docs/` 문서에만 기록한다.

## 패키지/모듈 네이밍
Python 표준 네이밍을 따른다.

- 패키지명: `snake_case`
- 모듈 파일명: `snake_case.py`
- 함수명: `snake_case`
- 변수명: `snake_case`
- 클래스명: `PascalCase`
- 상수명: `UPPER_SNAKE_CASE`
- route 함수명:
  - 동작을 짧게 드러낸다.
  - 예: `health`, `readiness`

## 타입 힌트 기준
공개 경계에는 타입을 명시한다.

- Python 버전 기준:
  - 확인 필요
  - 현재 코드는 `dict[str, str]`, `str | dict[str, str]` 문법을 사용한다.
- 타입 힌트 적용 범위:
  - FastAPI route handler
  - public service 함수
  - 설정 객체와 설정 helper
  - 외부 Provider client 경계
- Optional/Union 사용 기준:
  - `None`이 실제 허용되는 값일 때만 `| None`을 사용한다.
  - 두 개 이상 타입이 가능한 응답은 의미가 분리되는 모델로 우선 표현한다.
- 공개 API 타입 기준:
  - API 요청/응답은 Pydantic 모델을 우선 사용한다.
  - 단순 헬스체크처럼 작은 응답만 `dict[...]`를 허용한다.

## 레이어/모듈 책임
레이어별 책임을 좁게 유지한다.

| 레이어 | 위치 | 책임 | 금지/주의 |
|---|---|---|---|
| App | `app/main.py` | FastAPI 앱 생성, router 등록, 기본 헬스체크 | 도메인 로직을 길게 두지 않는다. |
| Settings | `app/settings.py` | 환경 변수 로딩, 기본값, 파생 설정 | 비밀값을 코드에 직접 쓰지 않는다. |
| Router | `app/routers/` | HTTP 요청/응답 처리 | SQL, 외부 API 세부 호출을 직접 하지 않는다. |
| Service | `app/services/` | 비즈니스 흐름, Provider 조합 | FastAPI 요청 객체에 강하게 의존하지 않는다. |
| Repository | `app/repositories/` | DB 읽기/쓰기 | API 응답 형식을 만들지 않는다. |
| Model/Schema | `app/models/`, `app/schemas/` | 도메인 모델, 요청/응답 모델 | 외부 Provider 원문을 그대로 노출하지 않는다. |
| Test | `tests/` | API, 설정, service 검증 | 운영 자격 증명에 의존하지 않는다. |

## 모델/스키마 기준
입출력 경계에는 명시적인 모델을 둔다.

- API 요청 모델:
  - `app/schemas/`에 둔다.
  - 필수값과 선택값을 타입으로 구분한다.
- API 응답 모델:
  - 외부에 노출되는 필드만 포함한다.
  - 내부 DB 필드나 Provider 원문을 그대로 반환하지 않는다.
- 도메인 모델:
  - `app/models/`에 둔다.
  - 원본 기록, AI 해석 정보, 벡터 정보는 구분되는 타입으로 표현한다.
- 설정 모델:
  - `app/settings.py`의 `BaseSettings` 기반 클래스로 관리한다.

## FastAPI 기준
route handler는 얇게 유지한다.

- 허용 책임:
  - 요청 입력 수신
  - dependency 주입
  - service 호출
  - 응답 모델 반환
- service로 보낼 책임:
  - AI 분석 흐름
  - DB 저장 흐름
  - Redis 작업 등록
  - 외부 Provider 예외 처리
- dependency 기준:
  - 설정은 `get_settings()`를 통해 가져온다.
  - DB 세션, Redis client, AI Provider client는 별도 생성 모듈로 분리한다.

## 오류 처리
오류는 사용자 응답과 내부 원인을 분리한다.

- API 오류:
  - 사용자에게 필요한 상태와 메시지만 반환한다.
  - 내부 예외 원문을 응답에 그대로 넣지 않는다.
- 의존 서비스 오류:
  - PostgreSQL, Redis 연결 실패는 readiness에서 구분 가능하게 처리한다.
  - 운영 로그에는 원인과 추적 키를 남긴다.
- AI 처리 오류:
  - 타임아웃, rate limit, 응답 파싱 실패를 구분한다.
  - 사용자가 수동 기록으로 이어갈 수 있는 상태를 남긴다.
- 개인정보 오류:
  - 원본 이미지 URL, OCR 원문, 프롬프트 원문, API 키는 예외 메시지에 넣지 않는다.

## 로깅
로그는 JSON 구조로 남긴다.

- logger:
  - 표준 `logging`
  - logger name: `scene_story_agent`
- 포맷:
  - 로컬 개발 환경은 들여쓰기 된 JSON
  - `timestamp`
  - `level`
  - `event`
  - `request_id`
- 민감정보 처리:
  - DB 비밀번호, API 키, 토큰은 로그에 남기지 않는다.
  - 원본 이미지 URL과 OCR 원문 전체는 로그에 남기지 않는다.
  - 원본 이미지 base64와 Provider 인증 헤더는 로그에 남기지 않는다.
  - AI 호출 로그는 장애 대응에 필요한 최소 항목만 남긴다.
- 추적 키:
  - `request_id`
  - `record_id`
  - `job_id`
- 기본 이벤트:
  - `request.completed`
  - `request.failed`
  - `record.created`
  - `asset.stored`
  - `ai.analysis.completed`
  - `ai.analysis_failed`
  - `embedding.created`
  - `storage_json.read`

## 테스트 작성 기준
테스트는 변경 경계를 기준으로 작성한다.

- API 테스트:
  - 상태 코드와 응답 스키마를 검증한다.
  - 헬스체크 API는 정상 응답과 의존성 실패를 나눠 검증한다.
- 설정 테스트:
  - 환경 변수 파싱과 기본값을 검증한다.
  - 실제 `.env.local`의 비밀값에 의존하지 않는다.
- service 테스트:
  - 외부 Provider, DB, Redis는 fake 또는 mock으로 대체한다.
  - 원본 기록 삭제 시 연결 데이터 삭제 흐름을 검증한다.
- 통합 테스트:
  - PostgreSQL과 Redis가 필요한 테스트는 격리된 의존 서비스를 사용한다.
  - 공유 로컬 상태에 의존하지 않는다.
- 파일명:
  - `test_*.py`

## 보안 작성 기준
개인정보와 비밀값은 코드 경계에서 보호한다.

- 비밀값:
  - 코드에 직접 쓰지 않는다.
  - `.env.local` 또는 배포 비밀값 관리 도구로 주입한다.
- 개인정보:
  - 원본 기록, AI 해석 정보, 임베딩 벡터는 연결 가능한 개인정보로 취급한다.
  - 삭제 기능은 원본, AI 해석 정보, 벡터 정보를 함께 처리한다.
- 외부 API:
  - 전송 데이터 항목을 service 계층에서 명시적으로 구성한다.
  - Provider 응답 원문은 필요한 필드만 저장한다.

## PR 셀프 체크리스트
변경 전후 경계를 확인한다.

1. 타입 힌트가 변경된 경계를 설명하는가?
2. 모델/스키마 위치가 프로젝트 관례와 맞는가?
3. 예외와 로그가 프로젝트 형식과 맞는가?
4. 테스트가 변경된 경계를 검증하는가?
5. 개인정보나 AI 처리 데이터 범위가 바뀌면 관련 문서를 갱신했는가?

## 확인 필요
아래 항목은 현재 파일 근거로 확정할 수 없다.

- Python 고정 버전
- 공통 API 오류 응답 스키마
- ruff, black, isort, mypy, pyright 사용 여부
- SQLAlchemy, Alembic 도입 여부

## 이력관리
- 2026-05-28: MVP JSON 로깅 기준과 기본 이벤트 정의
- 2026-05-21: Python/FastAPI 기준 코딩 스타일 문서 생성
