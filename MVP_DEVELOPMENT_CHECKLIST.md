# MVP 개발 체크리스트

이 문서는 `scene-story-agent` MVP 개발 순서를 로컬 환경 기준으로 정리한다.

## 적용 기준

MVP 개발은 로컬에서 먼저 완성한다.

- 실행 환경:
  - FastAPI
  - PostgreSQL 18 + pgvector
  - Redis 8.6
  - 로컬 파일 저장소
- 환경 파일:
  - `.env.local`
- 실행 기준:
  - Docker Compose로 PostgreSQL과 Redis를 실행한다.
  - API 서버는 로컬 Python 환경에서 실행한다.
  - AI Provider는 Mock 구현으로 먼저 연결한다.
- 제외 기준:
  - 클라우드 배포
  - 관리형 DB
  - 관리형 Redis
  - 외부 Object Storage
  - 실서비스 비밀값 주입

## 1. 실행 기반

로컬에서 앱과 의존 서비스를 반복 실행할 수 있게 만든다.

- [x] FastAPI 앱 진입점 확인
- [x] `.env.local` 로딩 확인
- [x] 로컬 실행 스크립트 확인
- [x] Docker Compose 실행 확인
- [x] PostgreSQL 18 + pgvector 컨테이너 실행 확인
- [x] Redis 8.6 컨테이너 실행 확인
- [x] `/health/live` API 확인
- [x] `/health/ready` API 확인
- [x] 로컬 DB 초기화 절차 확인

## 2. DB 기반

DB는 원본 기록과 AI 결과를 분리해 저장한다.

- [x] 로컬 DB 초기화 방식 확정
- [x] pgvector 확장 생성 확인
- [x] UUID v7 기본값 확인
- [x] `app_users` 테이블 생성
- [x] `records` 테이블 생성
- [x] `record_assets` 테이블 생성
- [x] `record_ai_interpretations` 테이블 생성
- [x] `record_embeddings` 테이블 생성
- [x] `record_relations` 테이블 생성
- [x] `timeline_candidates` 테이블 생성
- [x] `processing_jobs` 테이블 생성

## 3. 기록 API

기록 API는 원본 입력을 안정적으로 저장한다.

- [x] MVP용 사용자 식별 방식 확정
- [x] 기록 생성 API 구현
- [x] 기록 목록 조회 API 구현
- [x] 기록 상세 조회 API 구현
- [x] 기록 수정 API 구현
- [x] 기록 삭제 API 구현
- [x] 사용자 범위 필터 적용
- [x] 삭제된 기록 조회 제외 처리
- [x] 요청 schema 작성
- [x] 응답 schema 작성

## 4. 로컬 파일 저장

파일은 로컬 저장소에 두고 DB에는 참조만 저장한다.

- [x] 파일 저장 인터페이스 정의
- [x] 로컬 파일 저장소 구현
- [x] 로컬 저장 경로 설정값 추가
- [x] 업로드 파일 검증
- [x] `object_key` 생성 규칙 정의
- [x] `record_assets` 저장 처리
- [x] 로컬 파일 조회 API 또는 응답 방식 결정
- [x] 파일 삭제 처리
- [x] 파일 삭제 실패 처리 기준 정의

## 5. 작업 처리

AI 작업은 `processing_jobs`를 정본으로 두고 Redis는 보조 최적화에만 사용한다.

- [x] 기록 생성 후 작업 등록
- [x] 작업 상태 조회 API 구현
- [x] 실행 가능한 작업 조회 로직 구현
- [x] `queued` 상태 처리
- [x] `running` 상태 처리
- [x] `succeeded` 상태 처리
- [x] `failed` 상태 처리
- [x] `retrying` 상태 처리
- [x] `canceled` 상태 처리
- [x] 재시도 횟수 처리
- [x] 실패 사유 저장
- [x] Redis 보조 사용 기준 구현
- [x] 작업 상태 캐시 구현
- [x] 작업 중복 등록 완화 구현
- [x] 작업 실행 lock 구현
- [x] 로그인 세션 캐시 설계
- [x] 사용자 인증 조회 캐시 설계
- [x] 인증 요청 rate limit 설계

## 6. Mock AI 해석

AI Provider는 Mock 구현으로 먼저 데이터 흐름을 닫는다.

- [x] AI Provider 인터페이스 정의
- [x] OpenAI Provider 구현
- [x] Gemini Provider 구현
- [x] Mock AI Provider 구현
- [x] AI API key와 model 설정 경계 추가
- [x] AI 입력 schema 정의
- [x] AI 출력 schema 정의
- [x] 이미지 입력 준비 처리
- [x] EXIF 비저장 기준 적용
- [x] OCR 후보 저장
- [x] 장소 후보 저장
- [x] 메뉴 후보 저장
- [x] 금액 후보 저장
- [x] 태그 저장
- [x] 요약 저장
- [x] 사용자 수정값 저장 기준 정의

## 7. Mock 임베딩과 연결

벡터 검색 결과는 확정이 아니라 후보로 저장한다.

- [x] Embedding Provider 인터페이스 정의
- [x] Mock embedding 구현
- [x] 실제 AI API key와 model 설정 경계 추가
- [x] 임베딩 입력 snapshot 저장
- [x] pgvector 컬럼 저장 확인
- [x] 같은 사용자 기록만 검색
- [x] 삭제된 기록 제외
- [x] 유사 기록 후보 저장
- [x] 재방문 후보 저장
- [x] 타임라인 후보 저장
- [x] 후보 확정 전 노출 기준 정의

## 8. 삭제 흐름

삭제는 원본 기록 기준으로 묶는다.

- [x] 기록 soft delete 처리
- [x] 로컬 원본 파일 삭제 처리
- [x] AI 해석 정보 삭제 또는 비활성 처리
- [x] 임베딩 삭제 처리
- [x] 연결 후보 삭제 처리
- [x] 타임라인 후보 삭제 처리
- [x] 삭제 실패 시 보정 작업 등록
- [x] 삭제 후 목록 조회 제외 확인
- [x] 삭제 후 상세 조회 응답 기준 확인

## 9. 테스트

테스트는 API 흐름과 데이터 경계를 우선 검증한다.

- [x] 설정 로딩 테스트
- [x] DB 연결 테스트
- [x] Redis 연결 테스트
- [x] health API 테스트
- [x] 기록 생성 테스트
- [x] 기록 목록 조회 테스트
- [x] 기록 상세 조회 테스트
- [x] 기록 수정 테스트
- [x] 기록 삭제 테스트
- [x] 로컬 파일 저장 테스트
- [x] 작업 등록 테스트
- [x] Mock AI 처리 테스트
- [x] Mock 임베딩 저장 테스트
- [x] 유사 기록 검색 테스트
- [x] 삭제 흐름 테스트
- [x] OpenAI/Gemini Provider payload 테스트
- [x] DB 설계 전체 항목 샘플 JSON 테스트
- [x] AI 해석 후보 전체 항목 테스트
- [x] 요청 `request_id` 응답 헤더 테스트
- [x] 최종 저장 JSON OpenAPI 계약 테스트

## 10. 로컬 업로드 화면

브라우저에서 로컬 기록과 파일을 업로드할 수 있게 한다.

- [x] 업로드 화면 route 추가
- [x] 로컬 사용자 입력 지원
- [x] 감정 이모지 선택 지원
- [x] 만족도 1~5 선택 지원
- [x] 기록 생성 요청 연동
- [x] 파일 업로드 요청 연동
- [x] 업로드 결과 표시
- [x] 화면 route 테스트

## 11. 로컬 로그

정상과 실패 흐름을 추적할 수 있게 구조화 로그를 남긴다.

- [x] JSON 로그 포맷 구현
- [x] `request_id` 미들웨어 구현
- [x] `request.completed` 로그 구현
- [x] `request.failed` 로그 구현
- [x] 기록 생성 로그 구현
- [x] 파일 저장 로그 구현
- [x] AI 해석 성공/실패 로그 구현
- [x] 임베딩 생성 로그 구현
- [x] 작업 처리 로그 구현
- [x] 최종 저장 JSON 조회 로그 구현
- [x] Provider 호출 성공/실패 로그 구현
- [x] 민감정보 제외 기준 적용

## 12. 로컬 개발 완료 기준

MVP 로컬 개발은 아래 조건을 만족하면 완료로 본다.

- [x] `.env.local`만으로 API 서버가 실행된다.
- [x] Docker Compose로 PostgreSQL과 Redis가 실행된다.
- [x] 기록 생성부터 조회까지 API로 동작한다.
- [x] 사진 파일이 로컬 저장소에 저장된다.
- [x] 기록 생성 후 `processing_jobs`가 등록된다.
- [x] Mock AI 결과가 DB에 저장된다.
- [x] Mock embedding 결과가 pgvector 컬럼에 저장된다.
- [x] 유사 기록 후보가 생성된다.
- [x] 기록 삭제 시 관련 데이터가 조회에서 제외된다.
- [x] 정상/실패 흐름 로그가 남는다.
- [x] 핵심 API 테스트가 통과한다.

## 13. 이후 전환 검토

로컬 MVP가 닫힌 뒤 외부 운영 구성을 검토한다.

- [ ] 자체 서버 실행 방식 결정
- [ ] 운영 PostgreSQL 백업 기준 확정
- [ ] 운영 Redis 관리 기준 확정
- [ ] 외부 Object Storage 사용 여부 결정
- [ ] 실제 OpenAI 또는 Gemini Provider 연결
- [ ] AI API 비용 알림 기준 확정
- [ ] 운영 로그 확인 방식 확정
- [ ] 배포 절차 작성

## 이력관리

- 2026-05-28: 로컬 로그 체크리스트 추가
- 2026-05-27: 로컬 환경 기준 MVP 개발 체크리스트 작성
