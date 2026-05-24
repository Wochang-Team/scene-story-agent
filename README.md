# scene-story-agent

`scene-story-agent`는 사용자가 남긴 사진, 영상, 메모를 원본 기록으로 보관하고, AI 해석으로 기록 사이의 연결을 보여주는 멀티모달 AI 에이전트 프로젝트다.

상세 기준은 아래 문서를 따른다.

## 문서

- [프로덕트 스펙](docs/product-spec.md): 사용자 문제, 제품 가설, 핵심 흐름, 성공 지표, MVP 범위
- [DB 설계](docs/database-design.md): PostgreSQL 테이블, 삭제 연계, 조회 패턴, SQL 초안
- [개발 인프라](docs/development-infra.md): AWS, Google Cloud, Azure, 가성비 대안 서비스 비교와 권장 조합
- [개인정보 보호 조치](docs/privacy-compliance.md): 개인정보 분류, 동의 구조, AI 처리, 위치성 정보, 유출 대응
- [FastAPI 빠른 시작](docs/fastapi-quickstart.md): 로컬 실행과 상태 확인 절차

## 현재 상태

- 기획 초안 작성 완료
- 제품, DB, 인프라, 개인정보, 로컬 실행 문서 정리 완료
- 개발 인프라 비교 문서 작성 완료
- 개인정보 보호 조치 문서 작성 완료
- FastAPI 기본 서버와 로컬 PostgreSQL, Redis 실행 구성 완료

## 이력관리

- 2026-05-24: 문서 체계를 제품, DB, 인프라, 개인정보, 로컬 실행 기준으로 정리
- 2026-04-24: README 초안 작성
