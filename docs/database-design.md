# DB 설계

## 1. 문서 목적

이 문서는 `scene-story-agent` MVP의 PostgreSQL 데이터 구조를 정의한다.

- 포함 범위:
  - 원본 기록
  - 원본 파일 메타데이터
  - AI 해석 정보
  - 임베딩 벡터
  - 연관 기록 후보
  - 타임라인 후보
  - 비동기 작업 상태
  - 삭제 연계 기준
- 제외 범위:
  - 최종 인증 Provider 구현
  - Object Storage 버킷 생성 절차
  - Alembic 마이그레이션 파일
  - 운영 백업 정책 상세
- 전제:
  - 현재 SQL은 PostgreSQL 18.4, pgvector, UUID v7 생성 함수를 기준으로 작성한다.
  - 로컬 DB 이미지는 PostgreSQL 18.4와 pgvector를 사용한다.
  - 운영 DB도 pgvector와 UUID v7 생성 함수를 같은 방식으로 지원해야 한다.
  - 벡터 검색은 PostgreSQL의 pgvector를 우선 사용한다.
  - 원본 파일은 DB에 저장하지 않고 Object Storage에 저장한다.
  - DB에는 원본 파일 접근에 필요한 식별자와 메타데이터만 저장한다.
- 참조:
  - 로컬 실행과 Docker Compose 기준은 `.project/core_workflow.md`를 따른다.
  - PostgreSQL 이미지와 초기화 SQL 위치는 `.project/core_project.md`를 따른다.
  - 테이블, 컬럼, 제약, 인덱스의 정본은 `scripts/postgres/initdb/002_schema.sql`을 따른다.
  - 업로드와 AI 비동기 처리 흐름은 `docs/processing-flow.md`를 따른다.

## 2. 설계 원칙

DB는 원본 기록을 기준으로 연결한다.

- 원본 기록 ID를 파일, AI 해석 정보, 임베딩, 연결 후보, 타임라인 후보의 기준 키로 사용한다.
- 신규 PK는 UUID v7을 우선 사용한다.
- 원본 기록과 AI 해석 정보는 같은 테이블에 섞지 않는다.
- 사용자가 수정 가능한 AI 결과는 수정본과 원본 Provider 응답을 분리한다.
- 원본 파일 URL을 장기 저장하지 않고 저장소 객체 키를 저장한다.
- 임베딩 벡터는 원본 기록과 연결 가능하므로 개인정보에 준해 관리한다.
- 삭제는 원본 기록 기준으로 파생 데이터를 함께 처리한다.

## 3. 데이터 구조 개요

DB 구조는 원본 기록을 중심으로 확장한다.

- 원본 데이터:
  - 사용자가 남긴 기록과 파일 메타데이터를 저장한다.
  - 실제 파일은 Object Storage에 저장하고 DB에는 접근 식별자만 둔다.
- AI 파생 데이터:
  - 해석 결과, 임베딩, 후보 관계, 타임라인 후보는 원본 기록에서 파생된다.
  - 파생 데이터는 원본 기록 삭제 정책을 따른다.
- 작업 데이터:
  - 비동기 처리 상태는 PostgreSQL에 최종 기록한다.
  - Redis는 실행 보조 용도로만 사용한다.

## 4. 테이블 설계

MVP 테이블 상세는 SQL 파일에만 둔다.

### 정본 기준

테이블 상세는 SQL 파일을 기준으로 확인한다.

- 정본 파일:
  - `scripts/postgres/initdb/002_schema.sql`
- 정본 범위:
  - 테이블 생성
  - 컬럼명과 타입
  - `not null`, 기본값, `check`
  - 기본키, 외래키, unique 제약
  - 조회용 인덱스
- 문서 범위:
  - 설계 원칙
  - 삭제와 조회 정책

### 주요 기준

구현과 운영은 아래 기준을 따른다.

- 기록:
  - 목록과 상세 조회의 시작점이다.
  - 삭제 시 상태값과 삭제 시각을 함께 기록한다.
- 파일:
  - 원본 파일 URL이나 서명 URL은 저장하지 않는다.
  - 파일 접근은 저장소 객체 키를 기준으로 서버가 권한 확인 후 처리한다.
- AI 결과:
  - Provider 응답 원문 전체를 DB에 장기 저장하지 않는다.
  - 장애 재현에 필요한 참조값과 토큰 메타만 저장한다.
- 임베딩:
  - 사용자 식별자는 직접 두지 않는다.
  - 사용자 범위 필터는 원본 기록과 연결해 처리한다.
- 작업 상태:
  - 최종 추적 가능한 작업 상태는 PostgreSQL에 저장한다.
  - Redis는 lock, 상태 캐시, 중복 등록 완화에만 사용한다.

### 처리 상태 기준

상태값은 사용자 노출과 Worker 실행 기준을 함께 맞춘다.

- 기록 상태:
  - `processing`: AI 해석, 임베딩, 연관 기록, 타임라인 후보 생성 대기 또는 진행 중이다.
  - `ready`: 모든 파생 데이터 생성이 완료되어 실사용자 화면에 노출할 수 있다.
  - `failed`: 최대 재시도 횟수까지 처리에 실패한 기록이다.
  - `deleted`: 삭제 처리된 기록이다.
- 작업 상태:
  - `queued`: 등록 후 실행 대기 중이다.
  - `running`: Worker가 점유해 처리 중이다.
  - `retrying`: 실패 후 `available_at`까지 대기 중이다.
  - `succeeded`: 처리 완료 상태다.
  - `failed`: 최대 3회 실패한 상태다.
  - `canceled`: 취소된 상태다.
- 재시도 기준:
  - 1회 실패 후 10초 뒤 다시 실행한다.
  - 2회 실패 후 30초 뒤 다시 실행한다.
  - 3회 실패 시 작업과 기록을 실패 상태로 둔다.

### 파생 데이터 재생성 기준

Worker는 AI 해석 성공 뒤 검색과 연결 후보를 다시 만든다.

- 처리 대상:
  - `extract_ai_interpretation` 작업
- 순서:
  - AI 해석 정보를 저장한다.
  - 기존 활성 임베딩을 삭제 처리한다.
  - 현재 기록이 source인 연관 후보를 숨긴다.
  - 현재 기록의 타임라인 후보를 삭제한다.
  - 새 임베딩, 연관 기록 후보, 타임라인 후보를 생성한다.
- 중복 처리:
  - Redis `job:lock:{job_id}`로 같은 작업의 동시 실행을 완화한다.
  - 정본 상태는 PostgreSQL `processing_jobs`를 기준으로 판단한다.

### Redis 보조 key

Redis key는 정본 데이터가 아니라 보조 최적화 값이다.

- 작업 처리:
  - 같은 작업의 동시 실행을 완화한다.
  - 작업 상태 조회 응답을 짧게 캐시한다.
  - 같은 기록의 같은 작업 중복 등록을 완화한다.
- 로그인 보조:
  - 로그인 세션과 사용자 기본 정보 조회를 보조한다.
  - 로그인과 인증 요청 제한에 사용한다.
  - Redis 값이 없으면 PostgreSQL 또는 인증 절차로 복구한다.

- 저장 제외:
  - API key
  - 원본 파일 URL
  - OCR 원문
  - AI Provider 응답 원문
  - 장기 보관이 필요한 작업 상태

## 5. 삭제 연계

삭제는 원본 기록을 기준으로 처리한다.

### 기록 삭제 절차

1. 원본 기록의 상태를 삭제로 바꾸고 삭제 시각을 기록한다.
2. 파일 메타데이터와 AI 파생 데이터의 삭제 시각을 기록한다.
3. Object Storage의 원본 파일 삭제 작업을 등록한다.
4. 관련 후보와 타임라인 후보를 숨기거나 삭제한다.
5. 삭제 작업 결과를 작업 상태에 남긴다.

### 삭제 기준

- 사용자 조회에서는 삭제되지 않은 데이터만 반환한다.
- Object Storage 삭제가 실패하면 `delete_record_artifacts` 작업으로 재시도한다.
- AI Provider 전송 원문은 서비스 DB에 장기 저장하지 않는다.
- 백업 데이터 보관 기간은 운영 정책에서 별도로 확정한다.

## 6. 조회 패턴

초기 API는 아래 조회 패턴을 우선 지원한다.

### 기록 목록

- 조건:
  - 사용자 소유 기록
  - 삭제되지 않은 기록
- 정렬:
  - `happened_at desc nulls last`
  - `created_at desc`
- 함께 조회:
  - 대표 파일 메타데이터
  - 최신 AI 해석 정보

### 기록 상세

- 기준:
  - 기록 ID
  - 사용자 ID
- 함께 조회:
  - 전체 파일 메타데이터
  - 최신 AI 해석 정보
  - 관련 후보
  - 타임라인 후보

### 유사 기록 검색

- 기준:
  - 현재 기록의 임베딩
  - 같은 사용자 기록만 조회
  - 삭제된 기록 제외
- 구현 기준:
  - pgvector 연산은 Postgres 함수로 감싸거나 서버 SQL query 경계에서 호출한다.
  - API 서버는 Postgres 함수 또는 SQLAlchemy text query로 호출한다.

## 7. SQL 정본

초기 DB 구조는 `scripts/postgres/initdb`의 SQL 파일을 따른다.

### 파일 기준

정본 파일은 목적별로 나눈다.

- `scripts/postgres/initdb/001_extensions.sql`:
  - PostgreSQL extension을 생성한다.
  - 현재 `vector` extension을 사용한다.
- `scripts/postgres/initdb/002_schema.sql`:
  - MVP 테이블을 생성한다.
  - 컬럼, 제약, 인덱스를 정의한다.
  - 기존 로컬 DB 보강을 위한 `alter table ... add column if not exists`를 포함한다.

### 운영 기준

권한과 실행 환경은 운영 문서를 따른다.

- 로컬 실행:
  - `.project/core_workflow.md`의 Docker Compose 기준을 따른다.
- 권한 분리:
  - 운영 환경에서는 DB owner 계정과 API 서버 앱 계정을 분리한다.
  - 실제 계정, 비밀번호, secret 주입 방식은 운영 환경에서 확정한다.
- 변경 절차:
  - 테이블 구조 변경은 `002_schema.sql` 또는 이후 번호의 SQL 파일에 반영한다.
  - 이 문서에는 상세 SQL을 중복 기록하지 않는다.

## 8. 확인 필요

아래 항목은 구현 전 확정한다.

- 인증 Provider와 사용자 범위
- 만족도 입력 방식:
  - 1~5 점수
  - 감정 태그
  - 자유 메모 조합
- 임베딩 모델과 벡터 차원
- pgvector 인덱스 방식:
  - `hnsw`
  - `ivfflat`
- AI Provider 응답 원문 보관 여부와 보관 위치
- Object Storage Provider별 버킷과 객체 키 네이밍 규칙
- 물리 삭제와 soft delete의 운영 기준
- 자체 운영 PostgreSQL의 백업, 복구, 권한 분리 기준
- 운영 DB가 PostgreSQL 18.4 기준 SQL, pgvector, UUID v7 생성 함수를 같은 방식으로 지원하는지 확인
- 운영 단계에서 PostgreSQL 세션 정본이 필요한지 확인

## 9. 출처

- `docs/product-spec.md`
- `docs/development-infra.md`
- `docs/privacy-compliance.md`
- `.wiki/index.md`
- `docker-compose.yml`
- `.project/core_workflow.md`
- `.project/core_project.md`

## 이력관리

- 2026-06-02: 기록 상태, 작업 상태, Worker 재시도, 파생 데이터 재생성 기준 추가 및 처리 흐름 문서 참조 반영
- 2026-06-01: 테이블 상세와 SQL 초안을 정본 SQL 참조 방식으로 정리
- 2026-05-30: AI 해석 토큰 사용량을 `raw_response_ref.token_usage`에 저장하는 기준 추가
- 2026-05-27: AI 해석 후보에 방문 시간, 활동, 유사 기록, 재방문, 타임라인 후보 컬럼 추가
- 2026-05-24: 인프라 실행 절차를 정본 문서 참조로 대체하고 출처 정리
- 2026-05-23: PostgreSQL 18, pgvector, UUID v7, 관리자·앱 계정 기준 반영
- 2026-05-22: MVP DB 설계 초안 작성
