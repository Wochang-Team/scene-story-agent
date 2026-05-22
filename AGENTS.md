# AGENTS.md (Project Routing Only)

<!-- ct-init:core-docs:start -->
## Core 문서 참조 (ct-init 관리)
- 프로젝트 구조/모듈 상세: `.project/core_project.md`
- 코딩 스타일/네이밍 상세: `.project/core_code_style.md`
- 빌드/테스트/운영 상세: `.project/core_workflow.md`
- AGENTS.md는 라우팅 전용으로 유지하고, 상세 규칙은 위 문서에서 관리한다.
- 마지막 동기화: 2026-05-21
<!-- ct-init:core-docs:end -->

## 추가 라우팅
- 빌드/테스트/실행/환경 버전 판단이 필요한 작업은 먼저 `.project/core_workflow.md`를 확인한다.
- 패키지 구조와 런타임 진입점 판단이 필요한 작업은 먼저 `.project/core_project.md`를 확인한다.
- 타입 힌트, schema/model, 테스트 작성 규칙 판단이 필요한 작업은 먼저 `.project/core_code_style.md`를 확인한다.

## 운영 원칙
- 본 문서에는 상세 정책을 추가하지 않는다.
- 규칙/절차 변경은 대상 문서를 수정하고 동기화 일자만 갱신한다.

## LLM Wiki 규칙

`.wiki/raw/`와 `.wiki/`를 다룰 때는 `LLM-WIKI.md`를 따른다.
