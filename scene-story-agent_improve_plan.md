# 🧭 문서 개요

목적
- 대용량 기록, 이미지, AI 분석, 임베딩 검색 처리를 안정적으로 받기 위한 성능 개선 우선순위를 정한다.

이번 라운드 범위
- 요청 처리 시간 단축, 비동기 작업 경계 정리, 벡터 검색 병목 완화, 리소스 사용량 제어

후속 범위
- Object Storage 전환, 부하 테스트 자동화, 운영 지표, 장기 보관과 백업 정책

# 📌 개선 항목 요약

(1) 🔴 IMP-01 무거운 처리의 요청 경로 분리
- 착수 조건: AI 분석, 썸네일, 임베딩을 작업 상태 기반 실행 흐름으로 옮길 범위 확정
- 구현 위임 가능 여부: ✅ 가능

(2) 🔴 IMP-02 벡터 검색과 목록 조회 확장성 개선
- 착수 조건: 임베딩 차원, 검색 정확도 기준, 페이지 크기 확정
- 구현 위임 가능 여부: ✅ 가능

(3) 🟠 IMP-03 DB와 Redis 연결 관리 개선
- 착수 조건: API 동시 요청 수와 worker 동시 실행 수 목표 확정
- 구현 위임 가능 여부: ✅ 가능

(4) 🟠 IMP-04 파일 처리 메모리와 CPU 사용량 제어
- 착수 조건: 기록당 파일 수, 분석 대상 이미지 수, 파생 이미지 생성 시점 확정
- 구현 위임 가능 여부: ✅ 가능

(5) 🟡 IMP-05 작업 claim과 재시도 안정화
- 착수 조건: worker 실행 방식과 작업 lease 만료 정책 확정
- 구현 위임 가능 여부: 🟡 추가 확인 필요

# 🛠 개선 항목 상세

## (1) 🔴 IMP-01 무거운 처리의 요청 경로 분리
문제 정의
- AI Provider 호출, 이미지 처리, 썸네일 생성, 임베딩 생성이 API 요청 안에서 직접 실행된다.
권장 접근
- API는 상태 변경과 작업 등록만 담당하고, 무거운 처리는 worker 단계로 옮긴다.
영향 범위
- records API, AI pipeline, 썸네일, 임베딩, 작업 상태 API
범위
- 이번 라운드에서는 동기 API 경로에서 무거운 처리를 제거한다.
선행 조건
- 작업 유형별 성공, 실패, 재시도 상태 전이 기준 확정
구현 위임 가능 여부
- ✅ 가능
근거
- [records.py:170](app/routers/records.py)
  - AI 분석 요청에서 Provider 분석과 썸네일 생성을 함께 처리한다.
- [records.py:423](app/routers/records.py)
  - 임베딩 생성 요청에서 유사 검색과 후보 저장까지 함께 처리한다.

## (2) 🔴 IMP-02 벡터 검색과 목록 조회 확장성 개선
문제 정의
- 기록 목록은 전체 조회이고, 유사 검색은 사용자 전체 최신 임베딩 후보를 만든 뒤 거리 정렬한다.
권장 접근
- 목록은 cursor pagination으로 바꾸고, 임베딩 차원 고정 후 pgvector 인덱스 방식을 선택한다.
영향 범위
- 기록 목록 API, 관련 기록 검색, 임베딩 스키마, PostgreSQL 인덱스
범위
- 이번 라운드에서는 pagination과 유사 검색 SQL 개선을 우선한다.
선행 조건
- 페이지 크기, 임베딩 모델과 차원, 검색 recall과 latency 목표 확정
구현 위임 가능 여부
- ✅ 가능
근거
- [records.py:55](app/repositories/records.py)
  - `list_records`가 `fetchall()`로 사용자 전체 기록을 반환한다.
- [embeddings.py:92](app/repositories/embeddings.py)
  - 유사 검색이 최신 임베딩 후보를 구성한 뒤 전체 후보를 거리 정렬한다.

## (3) 🟠 IMP-03 DB와 Redis 연결 관리 개선
문제 정의
- 요청마다 PostgreSQL 연결과 Redis client를 새로 만들어 동시 요청 증가 시 연결 생성 비용이 커진다.
권장 접근
- PostgreSQL connection pool과 재사용 Redis client를 도입하고 pool 크기와 timeout을 설정화한다.
영향 범위
- DB dependency, Redis dependency, 설정 모델, API와 worker 운영 설정
범위
- 이번 라운드에서는 연결 재사용과 제한값 설정을 추가한다.
선행 조건
- API 프로세스 수, worker 수, PostgreSQL 최대 연결 수 확인
구현 위임 가능 여부
- ✅ 가능
근거
- [database.py:12](app/database.py)
  - 요청마다 `psycopg.connect`로 새 연결을 연다.
- [redis_client.py:10](app/redis_client.py)
  - 요청마다 Redis client를 만들고 종료한다.

## (4) 🟠 IMP-04 파일 처리 메모리와 CPU 사용량 제어
문제 정의
- 분석용 이미지는 리사이즈 후 base64로 메모리에 올리고, 썸네일은 요청 중 CPU 작업으로 생성한다.
권장 접근
- 원본 저장, 파생 이미지 생성, AI 전송 payload 생성을 분리하고 기록당 파일 수를 제한한다.
영향 범위
- 파일 업로드, 이미지 전처리, 썸네일 생성, AI Provider payload
범위
- 이번 라운드에서는 요청 경로의 이미지 CPU 작업 제거와 파일 수 제한을 우선한다.
선행 조건
- 기록당 최대 파일 수, 분석 대상 최대 이미지 수, 영상 처리 범위 확정
구현 위임 가능 여부
- ✅ 가능
근거
- [image_processing.py:18](app/services/image_processing.py)
  - 분석용 이미지를 리사이즈한 뒤 base64 문자열로 만든다.
- [thumbnails.py:17](app/services/thumbnails.py)
  - 썸네일 생성이 파일 열기, 리사이즈, 저장을 수행한다.

## (5) 🟡 IMP-05 작업 claim과 재시도 안정화
문제 정의
- 작업 claim이 후보 조회, Redis lock, DB update 순서라 worker 증가 시 lock 경합과 장기 running 방치가 생길 수 있다.
권장 접근
- 원자적 claim 방식과 running lease 만료 정책을 두고, 작업 유형별 재시도 가능 오류를 분리한다.
영향 범위
- 작업 claim API, worker 실행 방식, Redis lock, 작업 상태 전이
범위
- 이번 라운드에서는 claim 중복과 장기 running 복구 기준을 설계한다.
선행 조건
- worker 실행 방식, 작업별 최대 실행 시간, 재시도 가능 오류 분류 확정
구현 위임 가능 여부
- 🟡 추가 확인 필요
근거
- [jobs.py:38](app/services/jobs.py)
  - 사용 가능한 작업 10개를 조회한 뒤 Redis lock을 순차 시도한다.
- [jobs.py:143](app/repositories/jobs.py)
  - claim 후보 조회는 상태와 시간 조건만 사용하며 row lock은 없다.

# 📎 이번 라운드 정리

🚀 바로 구현
- IMP-01 무거운 처리의 요청 경로 분리
- IMP-02 벡터 검색과 목록 조회 확장성 개선
- IMP-03 DB와 Redis 연결 관리 개선
- IMP-04 파일 처리 메모리와 CPU 사용량 제어

🕒 후속 범위
- IMP-05 작업 claim과 재시도 안정화의 worker 실행 방식 확정
- Object Storage 전환
- 부하 테스트와 운영 지표 설계

## 🗂 이력관리

- 2026-06-01: 대용량 처리를 위한 성능 개선 우선순위 문서 작성
