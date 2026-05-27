from typing import Any, Protocol

from app.providers.http import ProviderHttpError
from app.schemas.ai import SceneAnalysisInput, SceneAnalysisResult
from app.settings import Settings


class SceneAnalysisProvider(Protocol):
    provider: str
    model: str

    def analyze(self, analysis_input: SceneAnalysisInput) -> SceneAnalysisResult:
        """Analyze a record and return normalized scene analysis."""


def normalize_scene_result(
    provider: str,
    model: str,
    payload: dict[str, Any],
    raw_response_ref: dict | None = None,
) -> SceneAnalysisResult:
    return SceneAnalysisResult(
        provider=provider,
        model=model,
        scene_type=payload.get("scene_type"),
        summary=payload.get("summary"),
        ocr_candidates=ensure_list(payload.get("ocr_candidates")),
        place_candidates=ensure_list(payload.get("place_candidates")),
        visit_time_candidates=ensure_list(payload.get("visit_time_candidates")),
        menu_candidates=ensure_list(payload.get("menu_candidates")),
        activity_candidates=ensure_list(payload.get("activity_candidates")),
        amount_candidates=ensure_list(payload.get("amount_candidates")),
        similar_record_candidates=ensure_list(payload.get("similar_record_candidates")),
        revisit_candidates=ensure_list(payload.get("revisit_candidates")),
        timeline_candidates=ensure_list(payload.get("timeline_candidates")),
        tags=[str(tag) for tag in ensure_list(payload.get("tags"))],
        raw_response_ref=raw_response_ref,
    )


def ensure_list(value: Any) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def scene_analysis_prompt(analysis_input: SceneAnalysisInput) -> str:
    return (
        "Analyze this personal scene record. Return only JSON with keys: "
        "scene_type, summary, ocr_candidates, place_candidates, "
        "visit_time_candidates, menu_candidates, activity_candidates, "
        "amount_candidates, similar_record_candidates, revisit_candidates, "
        "timeline_candidates, tags. "
        "Use arrays for candidate fields. Do not include sensitive raw image data. "
        f"Record memo: {analysis_input.memo or ''}. "
        f"Emotion: {analysis_input.emotion or ''}. "
        f"Satisfaction score: {analysis_input.satisfaction_score or ''}. "
        f"Happened at: {analysis_input.happened_at.isoformat() if analysis_input.happened_at else ''}. "
        f"Asset count: {len(analysis_input.assets)}."
    )


class MockSceneAnalysisProvider:
    provider = "mock"

    def __init__(self, model: str) -> None:
        self.model = model

    def analyze(self, analysis_input: SceneAnalysisInput) -> SceneAnalysisResult:
        tags = []
        if analysis_input.emotion:
            tags.append(analysis_input.emotion)
        if analysis_input.assets:
            tags.extend(sorted({asset.asset_type for asset in analysis_input.assets}))

        payload = {
            "scene_type": "personal_record",
            "summary": analysis_input.memo or "Mock scene analysis result.",
            "ocr_candidates": [],
            "place_candidates": [],
            "visit_time_candidates": [],
            "menu_candidates": [],
            "activity_candidates": [],
            "amount_candidates": [],
            "similar_record_candidates": [],
            "revisit_candidates": [],
            "timeline_candidates": [],
            "tags": tags,
        }
        return normalize_scene_result(
            provider=self.provider,
            model=self.model,
            payload=payload,
            raw_response_ref={"mode": "mock"},
        )


def get_scene_analysis_provider(settings: Settings) -> SceneAnalysisProvider:
    if settings.ai_provider == "mock":
        return MockSceneAnalysisProvider(model=settings.ai_model)
    if settings.ai_provider == "openai":
        from app.providers.openai_provider import OpenAISceneAnalysisProvider

        return OpenAISceneAnalysisProvider(settings)
    if settings.ai_provider == "gemini":
        from app.providers.gemini_provider import GeminiSceneAnalysisProvider

        return GeminiSceneAnalysisProvider(settings)

    raise ProviderHttpError(f"AI provider is not supported: {settings.ai_provider}")
