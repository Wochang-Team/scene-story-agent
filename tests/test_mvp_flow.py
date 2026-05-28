from io import BytesIO
import json

from PIL import Image

from app.schemas.storage import FIELD_CONTRACT

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
    assert "로컬 기록 업로드" in page.text
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
    assert len(storage_payload["data"]["record_assets"]) == 1
    assert storage_payload["data"]["record_assets"][0]["asset_id"] == asset["asset_id"]
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

    claim = client.post("/jobs/claim")
    assert claim.status_code == 200
    claimed = claim.json()
    assert claimed["job"] is not None
    succeed = client.post(
        f"/jobs/{claimed['job']['job_id']}/succeed",
        json={"lock_token": claimed["lock_token"]},
    )
    assert succeed.status_code == 200
    assert succeed.json()["status"] == "succeeded"

    analysis = client.post(f"/records/{second['record_id']}/ai-analysis", headers=auth(user))
    assert analysis.status_code == 200, analysis.text
    assert analysis.json()["provider"] == "mock"
    assert AI_CANDIDATE_KEYS.issubset(analysis.json())

    first_embedding = client.post(f"/records/{first['record_id']}/embedding", headers=auth(user))
    assert first_embedding.status_code == 200, first_embedding.text

    second_embedding = client.post(f"/records/{second['record_id']}/embedding", headers=auth(user))
    assert second_embedding.status_code == 200, second_embedding.text
    assert second_embedding.json()["embedding"]["provider"] == "mock"
    assert second_embedding.json()["relations"]
    assert second_embedding.json()["timeline_candidates"]

    final_storage_json = client.get(
        f"/records/{second['record_id']}/storage-json",
        headers=auth(user),
    )
    assert final_storage_json.status_code == 200
    final_storage_payload = final_storage_json.json()
    assert final_storage_payload["field_contract"] == FIELD_CONTRACT
    assert len(final_storage_payload["data"]["record_ai_interpretations"]) == 1
    assert len(final_storage_payload["data"]["record_embeddings"]) == 1
    assert final_storage_payload["data"]["record_relations"]
    assert final_storage_payload["data"]["timeline_candidates"]
    final_ai = final_storage_payload["data"]["record_ai_interpretations"][0]
    for candidate_key in AI_CANDIDATE_KEYS:
        assert candidate_key in final_ai

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


def test_provider_payloads_are_ready_for_real_api_keys(monkeypatch):
    from datetime import datetime, timezone
    from uuid import uuid4

    from app.providers.gemini_provider import GeminiSceneAnalysisProvider
    from app.providers.openai_provider import OpenAISceneAnalysisProvider
    from app.schemas.ai import ImageForAnalysis, SceneAnalysisInput
    from app.settings import Settings
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
            "output_text": json.dumps(
                {
                    "scene_type": "cafe",
                    "summary": "ok",
                    "ocr_candidates": [],
                    "place_candidates": [],
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
    assert AI_CANDIDATE_KEYS.issubset(openai_result.model_dump())
    assert openai_calls[0]["url"] == "https://api.openai.com/v1/responses"
    assert openai_calls[0]["payload"]["model"] == "gpt-test"
    assert openai_calls[0]["headers"]["Authorization"] == "Bearer test-key"
    openai_prompt = openai_calls[0]["payload"]["input"][0]["content"][0]["text"]
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
                                        "place_candidates": [],
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
            ]
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
    assert AI_CANDIDATE_KEYS.issubset(gemini_result.model_dump())
    assert "models/gemini-test:generateContent?key=test-key" in gemini_calls[0]["url"]
    assert gemini_calls[0]["payload"]["generationConfig"]["responseMimeType"] == "application/json"
    gemini_prompt = gemini_calls[0]["payload"]["contents"][0]["parts"][0]["text"]
    for candidate_key in AI_CANDIDATE_KEYS:
        assert candidate_key in gemini_prompt
