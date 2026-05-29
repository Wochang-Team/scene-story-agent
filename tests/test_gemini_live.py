from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.providers.embeddings import GeminiEmbeddingProvider
from app.providers.gemini_provider import GeminiSceneAnalysisProvider
from app.schemas.ai import SceneAnalysisInput
from app.settings import get_settings


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


def test_gemini_live_ai_and_embedding_from_env():
    settings = get_settings()
    if settings.ai_provider != "gemini" or settings.embedding_provider != "gemini":
        pytest.skip("Gemini live test requires AI_PROVIDER=gemini and EMBEDDING_PROVIDER=gemini.")
    if not settings.gemini_api_key:
        pytest.skip("Gemini live test requires GEMINI_API_KEY.")

    analysis_input = SceneAnalysisInput(
        record_id=uuid4(),
        memo="카페에서 라떼를 마시며 다음 MVP 작업 순서를 정리했다.",
        emotion="calm",
        satisfaction_score=4,
        happened_at=datetime.now(timezone.utc),
        assets=[],
        images=[],
    )

    analysis = GeminiSceneAnalysisProvider(settings).analyze(analysis_input)
    assert analysis.provider == "gemini"
    assert analysis.model == settings.ai_model
    assert AI_CANDIDATE_KEYS.issubset(analysis.model_dump())

    vector = GeminiEmbeddingProvider(settings).embed(
        "카페에서 라떼를 마시며 다음 MVP 작업 순서를 정리했다."
    )
    assert len(vector) == settings.embedding_dimension
    assert all(isinstance(value, float) for value in vector)
