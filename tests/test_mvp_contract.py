import json
from pathlib import Path

from app.schemas.storage import FIELD_CONTRACT

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "mvp_full_sample.json"
PRODUCT_SPEC_PATH = Path(__file__).parents[1] / "docs" / "product-spec.md"

EXPECTED_DB_FIELDS = {
    "app_users": {
        "user_id",
        "auth_provider",
        "auth_subject",
        "email",
        "display_name",
        "created_at",
        "updated_at",
        "deleted_at",
    },
    "records": {
        "record_id",
        "user_id",
        "memo",
        "emotion",
        "satisfaction_score",
        "happened_at",
        "status",
        "created_at",
        "updated_at",
        "deleted_at",
    },
    "record_assets": {
        "asset_id",
        "record_id",
        "asset_type",
        "storage_provider",
        "bucket_name",
        "object_key",
        "content_type",
        "byte_size",
        "width",
        "height",
        "duration_seconds",
        "checksum_sha256",
        "created_at",
        "deleted_at",
    },
    "record_ai_interpretations": {
        "interpretation_id",
        "record_id",
        "provider",
        "model",
        "scene_type",
        "summary",
        "ocr_candidates",
        "place_candidates",
        "visit_time_candidates",
        "menu_candidates",
        "activity_candidates",
        "amount_candidates",
        "similar_record_candidates",
        "revisit_candidates",
        "timeline_candidates",
        "tags",
        "user_corrections",
        "raw_response_ref",
        "status",
        "created_at",
        "updated_at",
        "deleted_at",
    },
    "record_embeddings": {
        "embedding_id",
        "record_id",
        "provider",
        "model",
        "dimension",
        "embedding",
        "input_snapshot",
        "created_at",
        "deleted_at",
    },
    "record_relations": {
        "relation_id",
        "source_record_id",
        "target_record_id",
        "relation_type",
        "similarity_score",
        "decision_status",
        "reasons",
        "created_at",
        "updated_at",
    },
    "timeline_candidates": {
        "timeline_candidate_id",
        "user_id",
        "record_id",
        "timeline_type",
        "grouping_key",
        "confidence_score",
        "reasons",
        "created_at",
    },
    "processing_jobs": {
        "job_id",
        "record_id",
        "job_type",
        "status",
        "attempt_count",
        "last_error_code",
        "last_error_message",
        "available_at",
        "started_at",
        "finished_at",
        "created_at",
        "updated_at",
    },
}

AI_REPLACEABLE_FIELDS = {
    "provider",
    "model",
    "scene_type",
    "summary",
    "ocr_candidates",
    "place_candidates",
    "visit_time_candidates",
    "menu_candidates",
    "activity_candidates",
    "amount_candidates",
    "similar_record_candidates",
    "revisit_candidates",
    "timeline_candidates",
    "tags",
    "user_corrections",
    "raw_response_ref",
    "status",
}


def test_full_mvp_sample_json_exposes_all_database_fields():
    sample = json.loads(FIXTURE_PATH.read_text())

    assert set(sample) == set(EXPECTED_DB_FIELDS)
    for table_name, expected_fields in EXPECTED_DB_FIELDS.items():
        assert set(sample[table_name]) == expected_fields
        assert set(FIELD_CONTRACT[table_name]) == expected_fields


def test_full_mvp_sample_keeps_ai_provider_replacement_contract_visible():
    sample = json.loads(FIXTURE_PATH.read_text())
    ai_sample = sample["record_ai_interpretations"]

    assert AI_REPLACEABLE_FIELDS.issubset(ai_sample)
    assert ai_sample["provider"]
    assert ai_sample["model"]
    assert isinstance(ai_sample["ocr_candidates"], list)
    assert isinstance(ai_sample["place_candidates"], list)
    assert isinstance(ai_sample["visit_time_candidates"], list)
    assert isinstance(ai_sample["menu_candidates"], list)
    assert isinstance(ai_sample["activity_candidates"], list)
    assert isinstance(ai_sample["amount_candidates"], list)
    assert isinstance(ai_sample["similar_record_candidates"], list)
    assert isinstance(ai_sample["revisit_candidates"], list)
    assert isinstance(ai_sample["timeline_candidates"], list)
    assert isinstance(ai_sample["tags"], list)
    assert isinstance(ai_sample["raw_response_ref"], dict)


def test_product_spec_documents_ai_interpretation_candidates():
    product_spec = PRODUCT_SPEC_PATH.read_text()

    for keyword in (
        "장소",
        "방문 시간",
        "메뉴",
        "활동",
        "금액",
        "장면 유형",
        "태그",
        "요약",
        "유사 기록",
        "재방문",
        "타임라인",
    ):
        assert keyword in product_spec


def test_storage_json_endpoint_is_part_of_openapi_contract(client):
    openapi = client.get("/openapi.json")
    assert openapi.status_code == 200

    response_schema = openapi.json()["paths"]["/records/{record_id}/storage-json"]["get"][
        "responses"
    ]["200"]["content"]["application/json"]["schema"]
    assert response_schema["$ref"] == "#/components/schemas/StorageExportResponse"
