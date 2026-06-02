import psycopg
from io import BytesIO
import json

from PIL import Image
from psycopg.rows import dict_row
from redis import Redis

from app.main import app
from app.providers.http import ProviderHttpError
from app.schemas.storage import FIELD_CONTRACT
from app.settings import get_settings
from app.workers.jobs import process_next_job

AI_CANDIDATE_KEYS = {
    "ocr_candidates",
    "place_candidates",
    "visit_time_candidates",
    "menu_candidates",
    "activity_candidates",
    "amount_candidates",
    "similar_record_candidates",
    "revisit_candidates",
    "timeline_candidates",
}

STORAGE_TABLE_KEYS = {
    "app_users",
    "records",
    "record_assets",
    "record_ai_interpretations",
    "record_embeddings",
    "record_relations",
    "timeline_candidates",
    "processing_jobs",
}


def image_bytes() -> bytes:
    output = BytesIO()
    Image.new("RGB", (32, 32), color=(120, 80, 40)).save(output, format="JPEG")
    return output.getvalue()


def auth(user: str) -> dict[str, str]:
    return {"X-Local-User": user}


def create_record(client, user: str, memo: str = "테스트 기록") -> dict:
    response = client.post(
        "/records",
        headers=auth(user),
        json={"memo": memo, "emotion": "calm", "satisfaction_score": 4},
    )
    assert response.status_code == 201, response.text
    return response.json()


def upload_asset(client, user: str, record_id: str) -> dict:
    response = client.post(
        f"/records/{record_id}/assets",
        headers=auth(user),
        files={"file": ("scene.jpg", image_bytes(), "image/jpeg")},
    )
    assert response.status_code == 201, response.text
    return response.json()


def active_test_settings():
    return app.dependency_overrides[get_settings]()


def run_worker_once(settings, record_id: str | None = None) -> bool:
    redis_client = Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        decode_responses=True,
    )
    try:
        with psycopg.connect(settings.postgres_dsn, row_factory=dict_row) as connection:
            return process_next_job(connection, redis_client, settings, record_id=record_id)
    finally:
        redis_client.close()


def make_job_available(settings, job_id: str) -> None:
    with psycopg.connect(settings.postgres_dsn, row_factory=dict_row) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                update processing_jobs
                set available_at = now()
                where job_id = %s
                """,
                (job_id,),
            )
        connection.commit()


def job_retry_delay_seconds(settings, job_id: str) -> float:
    with psycopg.connect(settings.postgres_dsn, row_factory=dict_row) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                select extract(epoch from (available_at - updated_at)) as delay_seconds
                from processing_jobs
                where job_id = %s
                """,
                (job_id,),
            )
            row = cursor.fetchone()
    assert row is not None
    return float(row["delay_seconds"])


def test_health_and_upload_page(client):
    live = client.get("/health/live")
    assert live.status_code == 200
    assert live.json() == {"status": "ok"}

    traced = client.get("/health/live", headers={"X-Request-ID": "pytest-request-id"})
    assert traced.status_code == 200
    assert traced.headers["X-Request-ID"] == "pytest-request-id"

    ready = client.get("/health/ready")
    assert ready.status_code == 200
    assert ready.json()["dependencies"] == {"postgres": "ok", "redis": "ok"}

    page = client.get("/ui/upload")
    assert page.status_code == 200
    assert "로컬 MVP 화면 그리드" in page.text
    assert "사용자 화면" in page.text
    assert "처리 데이터 확인 화면" in page.text
    assert "user-flow-grid" in page.text
    assert "user-flow-primary" in page.text
    assert "user-flow-secondary" not in page.text
    assert "ops-grid" in page.text
    assert "업로드 화면" in page.text
    assert ">목록<" in page.text
    assert ">상세<" in page.text
    assert "내 기록 목록 화면" not in page.text
    assert "선택 기록 상세 화면" not in page.text
    assert "AI 해석 화면" not in page.text
    assert "유사 기록/재방문 화면" not in page.text
    assert "타임라인 후보 화면" not in page.text
    assert "저장 JSON 화면" not in page.text
    assert "AI 해석 데이터" in page.text
    assert "임베딩/연관 데이터" in page.text
    assert "타임라인 후보 데이터" in page.text
    assert "AI 생성" in page.text
    assert "기존 AI로 생성" in page.text
    assert "임베딩 생성 시 함께 생성" in page.text
    assert "generateAnalysisForSelectedRecord" in page.text
    assert "generateEmbeddingForSelectedRecord" in page.text
    assert "selectedRecordIdOrThrow" in page.text
    assert "저장 JSON 데이터" in page.text
    assert "임베딩 검색 결과" not in page.text
    assert "status-board" in page.text
    assert "status-curl" in page.text
    assert "status-token" in page.text
    assert "원본 기록 저장" in page.text
    assert "원본 파일 업로드" in page.text
    assert "AI 해석 저장" in page.text
    assert "썸네일 저장" in page.text
    assert "임베딩 저장" in page.text
    assert "연관 기록 저장" in page.text
    assert "타임라인 후보 저장" in page.text
    assert "저장 JSON 조회" in page.text
    assert "status-detail" in page.text
    assert "status-duration" in page.text
    assert "호출: POST /records" in page.text
    assert "처리: 기록 생성, 후속 처리 작업 등록" in page.text
    assert "처리: 업로드 파일 저장" in page.text
    assert "호출: GET /jobs/records/{record_id}" in page.text
    assert "처리: worker가 AI 해석 결과 저장" in page.text
    assert "처리: 파일 업로드 요청 중 이미지 썸네일 생성" in page.text
    assert "처리: 기존 임베딩 정리 후 벡터 저장" in page.text
    assert "처리: 기존 연관 기록 정리 후 후보 계산" in page.text
    assert "처리: 기존 타임라인 후보 정리 후 후보 계산" in page.text
    assert "처리: 저장 데이터 조회" in page.text
    assert "저장:" not in page.text
    assert "curlCommand" in page.text
    assert "shellQuote" in page.text
    assert "tokenUsageText" in page.text
    assert "force = false" in page.text
    assert 'return force ? "토큰 사용 - · 남은 토큰 -" : ""' in page.text
    assert "tokenNumber" in page.text
    assert "formatStepDuration" in page.text
    assert "performance.now()" in page.text
    assert "처리 시간" in page.text
    assert "waitForAnalysisJob" in page.text
    assert "sleepMilliseconds(1000)" in page.text
    assert "토큰 사용" in page.text
    assert "남은 토큰" in page.text
    assert "recordCurl" in page.text
    assert "assetCurl" in page.text
    assert '.join("\\n")' in page.text
    assert "analysisCurl" in page.text
    assert "별도 API 호출 없음" in page.text
    assert "별도 API 호출 없음 ·" not in page.text
    assert "worker 내부 처리" in page.text
    assert "embeddingCurl" in page.text
    assert "storageCurl" in page.text
    assert "-F" in page.text
    assert "fileName: file.name" in page.text
    assert "사진 업로드" not in page.text
    assert "summary-grid" not in page.text
    assert "renderSummary" not in page.text
    assert "renderDefaultSummary" not in page.text
    assert "similar-results" in page.text
    assert "timeline-results" in page.text
    assert "fetchRelatedRecords" in page.text
    assert "appendUniquePill" in page.text
    assert "embeddingModel" in page.text
    assert "renderTimeline(timelinePayload.timeline_candidates, storageJson)" in page.text
    assert "provider ${" not in page.text
    assert "model ${" not in page.text
    assert 'row("provider"' not in page.text
    assert 'row("model"' not in page.text
    assert "record-memo" in page.text
    assert "record-tags" in page.text
    assert "record-headline" in page.text
    assert "record-datetime" in page.text
    assert "headline.appendChild(title)" in page.text
    assert "copy.append(headline, memo, dateTime)" in page.text
    assert "content.append(copy, tagRow)" in page.text
    assert ".record-content > .record-tags" in page.text
    assert "row-gap: 10px" in page.text
    assert "column-gap: 10px" in page.text
    assert "record-thumbnail" in page.text
    assert "record-content" in page.text
    assert "record-copy" in page.text
    assert "representativeAsset" in page.text
    assert "assetObjectUrl" in page.text
    assert "loadRecordThumbnail" in page.text
    assert "uploadAssetItems" in page.text
    assert "openOriginalAsset" in page.text
    assert "const thumbnails = assets.filter((asset) => asset.asset_type === \"thumbnail\")" in page.text
    assert "caption.textContent = `원본 / ${Math.round((asset.byte_size || 0) / 1024)}KB`" in page.text
    assert "detail-thumbnail" not in page.text
    assert "related-record-thumbnail" not in page.text
    assert "record-delete" in page.text
    assert "분석 대기" in page.text
    assert "재시도 필요" in page.text
    assert "is-status-waiting" in page.text
    assert "is-status-retry" in page.text
    assert "AI 대기" not in page.text
    assert "AI 실패" not in page.text
    assert "처리실패" not in page.text
    assert "/ai-analysis/retry" in page.text
    assert "button.pill" in page.text
    assert "해석 재시도 대기" in page.text
    assert "await waitForAnalysisJob(recordId, jobsCurl)" in page.text
    assert "await refreshAfterUpload(recordId)" in page.text
    assert "recordStatusValue" in page.text
    assert "recordStatusPill" not in page.text
    assert '{label: "상태"' not in page.text
    assert "detail-hero" in page.text
    assert "detail-headline" not in page.text
    assert "detail-datetime" not in page.text
    assert "detail-section" in page.text
    assert "renderDetailHero" in page.text
    assert "recordDateTimeValue" in page.text
    assert "compactDateTime" in page.text
    assert "detailDateTime" in page.text
    assert "async function fetchRelatedRecords(relations, limit = 3)" in page.text
    assert "groupedRelatedRelations" in page.text
    assert "relationLabels" in page.text
    assert "relationLabelsWithScores" in page.text
    assert "relationScoreLabel" in page.text
    assert "grouped.set(key, {relation, relations: [relation]})" in page.text
    assert "relatedRecordItems" in page.text
    assert "detailRelatedRecords" in page.text
    assert "related-record-button" in page.text
    assert "최대 ${relatedRecordDisplayLimit}건" in page.text
    assert "section.appendChild(heading)" not in page.text
    assert "연관 기록" in page.text
    assert "유사 ${similarCount}건 · 재방문 ${revisitCount}건 · 타임라인 ${timelineCandidates.length}건" not in page.text
    assert "AI 해석 요약" not in page.text
    assert "연결 요약" not in page.text
    assert "대표 연결" not in page.text
    assert "타임라인 그룹" not in page.text
    assert "유사도" not in page.text
    assert "decision_status" in page.text
    assert "dataJson" in page.text
    assert "numberText" in page.text
    assert "dataItemTitle" in page.text
    assert "dataHelpText" in page.text
    assert "data-help" in page.text
    assert "data-tooltip" in page.text
    assert "data-help:hover::after" in page.text
    assert "help.dataset.tooltip = helpText" in page.text
    assert "help.title = helpText" not in page.text
    assert "❓" in page.text
    assert 'help.setAttribute("aria-label", `${label} 설명: ${helpText}`)' in page.text
    assert "AI가 사진과 메모에서 추정한 장소 후보입니다." in page.text
    assert "연관 유형입니다. 유사 기록, 재방문 후보 같은 관계 종류를 뜻합니다." in page.text
    assert "result-card" in page.text
    assert 'dataItemTitle("연관", index, relation.relation_type)' in page.text
    assert "for (const [index, relation] of relations.entries())" in page.text
    assert 'dataItemTitle("타임라인", index, candidate.timeline_type)' in page.text
    assert "for (const [index, candidate] of candidates.entries())" in page.text
    assert "data-json" in page.text
    assert '{label: "장소"' not in page.text
    assert '{label: "방문"' not in page.text
    assert '{label: "장면"' not in page.text
    assert '{label: "활동내역", value: bestActivityText(analysis)}' in page.text
    assert '{label: "AI 요약", value: analysis?.summary}' in page.text
    assert "메모" in page.text
    assert "장소" in page.text
    assert "메뉴" in page.text
    assert "활동" in page.text
    assert "visit_time_candidates" in page.text
    assert "relation_type" in page.text
    assert "유사한 기록" in page.text
    assert "다시 방문한 기록" in page.text
    assert "requestNoContent" in page.text
    assert 'method: "DELETE"' in page.text
    assert "이 기록을 삭제할까요?" in page.text
    assert "recordListTitle" in page.text
    assert "memoDisplayText" in page.text
    assert "bestActivityText" in page.text
    assert "createRecordListContent" in page.text
    assert "includeRecordTags: false" in page.text
    assert "record-reason" not in page.text
    assert "relationReasonText" not in page.text
    assert "추천 근거" not in page.text
    assert "return memoDisplayText(record) || activityDisplayText(analysis) || \"요약 없음\"" in page.text
    assert "related-record-title" not in page.text
    assert "related-record-subtitle" not in page.text
    assert "button.appendChild(content)" in page.text
    assert "hero.append(title, tags)" in page.text
    assert "recordListSubtitle" in page.text
    assert "recordListTags" in page.text
    assert "menuNameText" in page.text
    assert "stripMenuMeta" in page.text
    assert "menuDetailText" in page.text
    assert "menuDetailItems" in page.text
    assert "menuDetailList" in page.text
    assert "tagDetailList" in page.text
    assert "detail-menu-list" in page.text
    assert "detail-pill-list" in page.text
    assert "detail-memo-editor" in page.text
    assert "detail-memo-edit" in page.text
    assert "detail-memo-input" in page.text
    assert "inline-size: 22px" in page.text
    assert "font-size: 12px" in page.text
    assert 'value instanceof Node' in page.text
    assert "memoDetailEditor" in page.text
    assert "saveRecordMemo" in page.text
    assert "replaceRecord" in page.text
    assert 'method: "PATCH"' in page.text
    assert "input.addEventListener(\"blur\", save)" in page.text
    assert "event.key === \"Enter\"" in page.text
    assert "JSON.stringify({memo: nextMemo || null})" in page.text
    assert '{label: "메모", value: memoDetailEditor(record)}' in page.text
    assert '{label: "메뉴", value: menuDetailList(analysis)}' in page.text
    assert '{label: "태그", value: tagDetailList(analysis?.tags)}' in page.text
    assert '{label: "금액"' not in page.text
    assert "candidateField" in page.text
    assert "bestCandidate" in page.text
    assert "candidateScore" in page.text
    assert "emotionIcon" in page.text
    assert "activity_candidates" in page.text
    assert "menu_candidates" in page.text
    assert "satisfaction_score}점" in page.text
    assert "AI 완료" not in page.text
    assert "local-mvp" in page.text
    assert "방문 사진" in page.text
    assert 'id="files"' in page.text
    assert 'id="primary-picker"' in page.text
    assert "대표사진 선택" in page.text
    assert "primary-preview-button" in page.text
    assert "selectedPrimaryFileIndex" in page.text
    assert "renderPrimaryPicker" in page.text
    assert "orderedUploadFiles" in page.text
    assert "URL.createObjectURL" in page.text
    assert "multiple required" in page.text
    assert "files.length" in page.text
    assert "😊" in page.text
    assert "satisfaction-5" in page.text
    assert "/records" in page.text
    assert "/ai-analysis" in page.text
    assert "/embedding" in page.text
    assert "/storage-json" in page.text


def test_path_validation_error_logs_actionable_context(client, monkeypatch):
    import app.main as main_module

    events = []

    def capture_log_event(event, **fields):
        events.append({"event": event, **fields})

    monkeypatch.setattr(main_module, "log_event", capture_log_event)

    response = client.get("/jobs/1", headers=auth("pytest-flow"))

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["path", "job_id"]

    validation_events = [
        event for event in events if event["event"] == "request.validation_failed"
    ]
    client_error_events = [
        event for event in events if event["event"] == "request.client_error"
    ]
    assert validation_events
    assert client_error_events
    assert client_error_events[0]["status_code"] == 422
    validation_error = validation_events[0]["errors"][0]
    assert validation_error["type"] == "uuid_parsing"
    assert validation_error["loc"] == ["path", "job_id"]
    assert validation_error["input"] == "1"


def test_record_file_job_ai_embedding_and_delete_flow(client):
    user = "pytest-flow"
    first = create_record(client, user, "카페 라떼와 조용한 작업")
    second = create_record(client, user, "카페 라떼와 조용한 작업")
    assert first["status"] == "processing"
    assert second["status"] == "processing"
    asset = upload_asset(client, user, second["record_id"])
    assert asset["storage_provider"] == "local"
    assert asset["content_type"] == "image/jpeg"

    storage_json = client.get(f"/records/{second['record_id']}/storage-json", headers=auth(user))
    assert storage_json.status_code == 200
    storage_payload = storage_json.json()
    assert storage_payload["field_contract"] == FIELD_CONTRACT
    assert set(storage_payload["data"]) == STORAGE_TABLE_KEYS
    assert storage_payload["data"]["app_users"]["auth_subject"] == user
    assert storage_payload["data"]["records"]["record_id"] == second["record_id"]
    assert "deleted_at" in storage_payload["data"]["records"]
    assert len(storage_payload["data"]["record_assets"]) == 2
    initial_assets = storage_payload["data"]["record_assets"]
    assert {item["asset_type"] for item in initial_assets} == {"photo", "thumbnail"}
    assert any(item["asset_id"] == asset["asset_id"] for item in initial_assets)
    assert next(item for item in initial_assets if item["asset_type"] == "thumbnail")[
        "content_type"
    ] == "image/webp"
    assert len(storage_payload["data"]["processing_jobs"]) == 1
    for candidate_key in AI_CANDIDATE_KEYS:
        assert candidate_key in storage_payload["field_contract"]["record_ai_interpretations"]

    records = client.get("/records", headers=auth(user))
    assert records.status_code == 200
    assert len(records.json()["records"]) == 2

    detail = client.get(f"/records/{second['record_id']}", headers=auth(user))
    assert detail.status_code == 200
    assert detail.json()["record_id"] == second["record_id"]

    update = client.patch(
        f"/records/{second['record_id']}",
        headers=auth(user),
        json={"memo": "수정된 카페 기록"},
    )
    assert update.status_code == 200
    assert update.json()["memo"] == "수정된 카페 기록"

    jobs = client.get(f"/jobs/records/{second['record_id']}", headers=auth(user))
    assert jobs.status_code == 200
    assert jobs.json()["jobs"][0]["status"] == "queued"

    settings = active_test_settings()
    assert run_worker_once(settings, first["record_id"]) is True
    assert run_worker_once(settings, second["record_id"]) is True

    completed_jobs = client.get(f"/jobs/records/{second['record_id']}", headers=auth(user))
    assert completed_jobs.status_code == 200
    assert completed_jobs.json()["jobs"][0]["status"] == "succeeded"

    ready_detail = client.get(f"/records/{second['record_id']}", headers=auth(user))
    assert ready_detail.status_code == 200
    assert ready_detail.json()["status"] == "ready"

    analysis = client.get(f"/records/{second['record_id']}/ai-analysis", headers=auth(user))
    assert analysis.status_code == 200, analysis.text
    assert analysis.json()["provider"] == "mock"
    assert AI_CANDIDATE_KEYS.issubset(analysis.json())

    final_storage_json = client.get(
        f"/records/{second['record_id']}/storage-json",
        headers=auth(user),
    )
    assert final_storage_json.status_code == 200
    final_storage_payload = final_storage_json.json()
    assert final_storage_payload["field_contract"] == FIELD_CONTRACT
    assert len(final_storage_payload["data"]["record_ai_interpretations"]) == 1
    active_embeddings = [
        item for item in final_storage_payload["data"]["record_embeddings"] if not item["deleted_at"]
    ]
    assert len(active_embeddings) == 1
    assert active_embeddings[0]["provider"] == "mock"
    assert active_embeddings[0]["input_snapshot"]["ai_interpretation"]["summary"]
    assert final_storage_payload["data"]["record_relations"]
    assert final_storage_payload["data"]["timeline_candidates"]
    final_ai = final_storage_payload["data"]["record_ai_interpretations"][0]
    for candidate_key in AI_CANDIDATE_KEYS:
        assert candidate_key in final_ai
    final_assets = final_storage_payload["data"]["record_assets"]
    assert {asset["asset_type"] for asset in final_assets} == {"photo", "thumbnail"}
    thumbnail = next(asset for asset in final_assets if asset["asset_type"] == "thumbnail")
    assert thumbnail["content_type"] == "image/webp"

    rebuilt_embedding = client.post(f"/records/{second['record_id']}/embedding", headers=auth(user))
    assert rebuilt_embedding.status_code == 200, rebuilt_embedding.text
    rebuilt_storage_json = client.get(
        f"/records/{second['record_id']}/storage-json",
        headers=auth(user),
    )
    rebuilt_storage_payload = rebuilt_storage_json.json()
    rebuilt_active_embeddings = [
        item for item in rebuilt_storage_payload["data"]["record_embeddings"] if not item["deleted_at"]
    ]
    rebuilt_active_relations = [
        item
        for item in rebuilt_storage_payload["data"]["record_relations"]
        if item["source_record_id"] == second["record_id"] and item["decision_status"] != "hidden"
    ]
    assert len(rebuilt_active_embeddings) == 1
    assert rebuilt_active_relations

    thumbnail_file = client.get(
        f"/records/{second['record_id']}/assets/{thumbnail['asset_id']}/file",
        headers=auth(user),
    )
    assert thumbnail_file.status_code == 200
    assert thumbnail_file.headers["content-type"] == "image/webp"

    relations = client.get(f"/records/{second['record_id']}/relations", headers=auth(user))
    assert relations.status_code == 200
    assert relations.json()["relations"]

    timeline = client.get(
        f"/records/{second['record_id']}/timeline-candidates",
        headers=auth(user),
    )
    assert timeline.status_code == 200
    assert timeline.json()["timeline_candidates"]

    other_user_detail = client.get(
        f"/records/{second['record_id']}",
        headers=auth("pytest-other"),
    )
    assert other_user_detail.status_code == 404

    delete = client.delete(f"/records/{second['record_id']}", headers=auth(user))
    assert delete.status_code == 204

    deleted_detail = client.get(f"/records/{second['record_id']}", headers=auth(user))
    assert deleted_detail.status_code == 404

    deleted_assets = client.get(f"/records/{second['record_id']}/assets", headers=auth(user))
    assert deleted_assets.status_code == 404


def test_ai_worker_retries_then_marks_record_failed(client, monkeypatch):
    user = "pytest-retry"
    record = create_record(client, user, "간헐적인 Gemini 실패")
    settings = active_test_settings()

    def fail_analysis(**_kwargs):
        raise ProviderHttpError(
            "Provider request failed: HTTP 403 "
            "Lightning dunning decision is deny for project: projects/1013163396544"
        )

    from app.workers import jobs as worker_jobs

    monkeypatch.setattr(worker_jobs.ai_pipeline, "analyze_record", fail_analysis)

    assert run_worker_once(settings, record["record_id"]) is True
    first_jobs = client.get(f"/jobs/records/{record['record_id']}", headers=auth(user))
    first_job = first_jobs.json()["jobs"][0]
    assert first_job["status"] == "retrying"
    assert first_job["attempt_count"] == 1
    assert first_job["last_error_code"] == "provider_dunning_denied"
    assert 8 <= job_retry_delay_seconds(settings, first_job["job_id"]) <= 12

    make_job_available(settings, first_job["job_id"])
    assert run_worker_once(settings, record["record_id"]) is True
    second_jobs = client.get(f"/jobs/records/{record['record_id']}", headers=auth(user))
    second_job = second_jobs.json()["jobs"][0]
    assert second_job["status"] == "retrying"
    assert second_job["attempt_count"] == 2
    assert 28 <= job_retry_delay_seconds(settings, second_job["job_id"]) <= 32

    make_job_available(settings, second_job["job_id"])
    assert run_worker_once(settings, record["record_id"]) is True
    final_jobs = client.get(f"/jobs/records/{record['record_id']}", headers=auth(user))
    final_job = final_jobs.json()["jobs"][0]
    assert final_job["status"] == "failed"
    assert final_job["attempt_count"] == 3

    failed_detail = client.get(f"/records/{record['record_id']}", headers=auth(user))
    assert failed_detail.status_code == 200
    assert failed_detail.json()["status"] == "failed"

    retry = client.post(f"/records/{record['record_id']}/ai-analysis/retry", headers=auth(user))
    assert retry.status_code == 200, retry.text
    assert retry.json()["status"] == "queued"
    assert retry.json()["attempt_count"] == 0

    retried_detail = client.get(f"/records/{record['record_id']}", headers=auth(user))
    assert retried_detail.status_code == 200
    assert retried_detail.json()["status"] == "processing"

    retried_jobs = client.get(f"/jobs/records/{record['record_id']}", headers=auth(user))
    assert retried_jobs.status_code == 200
    assert retried_jobs.json()["jobs"][0]["status"] == "queued"


def test_provider_payloads_are_ready_for_real_api_keys(monkeypatch):
    from datetime import datetime, timezone
    from uuid import uuid4

    from app.providers.gemini_provider import GeminiSceneAnalysisProvider
    from app.providers.embeddings import GeminiEmbeddingProvider
    from app.providers.openai_provider import OpenAISceneAnalysisProvider
    from app.schemas.ai import ImageForAnalysis, SceneAnalysisInput
    from app.settings import Settings
    import app.providers.embeddings as embedding_module
    import app.providers.gemini_provider as gemini_module
    import app.providers.openai_provider as openai_module

    analysis_input = SceneAnalysisInput(
        record_id=uuid4(),
        memo="provider smoke",
        emotion="calm",
        satisfaction_score=4,
        happened_at=datetime.now(timezone.utc),
        assets=[],
        images=[ImageForAnalysis(content_type="image/jpeg", data_base64="ZmFrZQ==")],
    )

    openai_calls = []

    def fake_openai_post_json(**kwargs):
        openai_calls.append(kwargs)
        return {
            "id": "resp_test",
            "usage": {
                "input_tokens": 11,
                "output_tokens": 7,
                "total_tokens": 18,
            },
            "output_text": json.dumps(
                {
                    "scene_type": "cafe",
                    "summary": "ok",
                    "ocr_candidates": [],
                    "place_candidates": ["cafe"],
                    "visit_time_candidates": [],
                    "menu_candidates": [],
                    "activity_candidates": [],
                    "amount_candidates": [],
                    "similar_record_candidates": [],
                    "revisit_candidates": [],
                    "timeline_candidates": [],
                    "tags": ["cafe"],
                }
            ),
        }

    monkeypatch.setattr(openai_module, "post_json", fake_openai_post_json)
    openai_provider = OpenAISceneAnalysisProvider(
        Settings(
            postgres_db="x",
            postgres_user="x",
            postgres_password="x",
            ai_provider="openai",
            ai_model="gpt-test",
            openai_api_key="test-key",
        )
    )
    openai_result = openai_provider.analyze(analysis_input)
    assert openai_result.provider == "openai"
    assert openai_result.scene_type == "cafe"
    assert openai_result.place_candidates == [{"value": "cafe"}]
    assert openai_result.raw_response_ref["token_usage"]["used_tokens"] == 18
    assert openai_result.raw_response_ref["token_usage"]["input_tokens"] == 11
    assert openai_result.raw_response_ref["token_usage"]["output_tokens"] == 7
    assert openai_result.raw_response_ref["token_usage"]["remaining_tokens"] is None
    assert AI_CANDIDATE_KEYS.issubset(openai_result.model_dump())
    assert openai_calls[0]["url"] == "https://api.openai.com/v1/responses"
    assert openai_calls[0]["payload"]["model"] == "gpt-test"
    assert openai_calls[0]["headers"]["Authorization"] == "Bearer test-key"
    openai_prompt = openai_calls[0]["payload"]["input"][0]["content"][0]["text"]
    assert "Write summary in Korean." in openai_prompt
    assert "infer each image role automatically" in openai_prompt
    for candidate_key in AI_CANDIDATE_KEYS:
        assert candidate_key in openai_prompt

    gemini_calls = []

    def fake_gemini_post_json(**kwargs):
        gemini_calls.append(kwargs)
        return {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": json.dumps(
                                    {
                                        "scene_type": "gallery",
                                        "summary": "ok",
                                        "ocr_candidates": [],
                                        "place_candidates": ["gallery"],
                                        "visit_time_candidates": [],
                                        "menu_candidates": [],
                                        "activity_candidates": [],
                                        "amount_candidates": [],
                                        "similar_record_candidates": [],
                                        "revisit_candidates": [],
                                        "timeline_candidates": [],
                                        "tags": ["art"],
                                    }
                                )
                            }
                        ]
                    }
                }
            ],
            "usageMetadata": {
                "promptTokenCount": 13,
                "candidatesTokenCount": 9,
                "totalTokenCount": 22,
            },
        }

    monkeypatch.setattr(gemini_module, "post_json", fake_gemini_post_json)
    gemini_provider = GeminiSceneAnalysisProvider(
        Settings(
            postgres_db="x",
            postgres_user="x",
            postgres_password="x",
            ai_provider="gemini",
            ai_model="gemini-test",
            gemini_api_key="test-key",
        )
    )
    gemini_result = gemini_provider.analyze(analysis_input)
    assert gemini_result.provider == "gemini"
    assert gemini_result.scene_type == "gallery"
    assert gemini_result.place_candidates == [{"value": "gallery"}]
    assert gemini_result.raw_response_ref["token_usage"]["used_tokens"] == 22
    assert gemini_result.raw_response_ref["token_usage"]["input_tokens"] == 13
    assert gemini_result.raw_response_ref["token_usage"]["output_tokens"] == 9
    assert gemini_result.raw_response_ref["token_usage"]["remaining_tokens"] is None
    assert AI_CANDIDATE_KEYS.issubset(gemini_result.model_dump())
    assert "models/gemini-test:generateContent?key=test-key" in gemini_calls[0]["url"]
    assert gemini_calls[0]["payload"]["generationConfig"]["responseMimeType"] == "application/json"
    gemini_prompt = gemini_calls[0]["payload"]["contents"][0]["parts"][0]["text"]
    assert "Write summary in Korean." in gemini_prompt
    assert "infer each image role automatically" in gemini_prompt
    for candidate_key in AI_CANDIDATE_KEYS:
        assert candidate_key in gemini_prompt

    embedding_calls = []

    def fake_gemini_embedding_post_json(**kwargs):
        embedding_calls.append(kwargs)
        return {"embedding": {"values": [0.1, 0.2, 0.3]}}

    monkeypatch.setattr(embedding_module, "post_json", fake_gemini_embedding_post_json)
    embedding_provider = GeminiEmbeddingProvider(
        Settings(
            postgres_db="x",
            postgres_user="x",
            postgres_password="x",
            embedding_provider="gemini",
            embedding_model="gemini-embedding-test",
            embedding_dimension=3,
            gemini_api_key="test-key",
        )
    )
    embedding_result = embedding_provider.embed("카페 라떼와 조용한 작업")
    assert embedding_result == [0.1, 0.2, 0.3]
    assert embedding_calls[0]["url"].endswith("/models/gemini-embedding-test:embedContent")
    assert embedding_calls[0]["headers"]["x-goog-api-key"] == "test-key"
    assert embedding_calls[0]["payload"]["content"]["parts"][0]["text"] == "카페 라떼와 조용한 작업"
    assert embedding_calls[0]["payload"]["output_dimensionality"] == 3
