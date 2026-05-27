from typing import Any

from app.providers.ai import normalize_scene_result, scene_analysis_prompt
from app.providers.http import parse_json_text, post_json, require_api_key
from app.schemas.ai import SceneAnalysisInput, SceneAnalysisResult
from app.settings import Settings


class GeminiSceneAnalysisProvider:
    provider = "gemini"

    def __init__(self, settings: Settings) -> None:
        self.model = settings.ai_model
        self.api_key = require_api_key(settings.gemini_api_key, "Gemini")
        self.timeout_seconds = settings.ai_timeout_seconds
        self.max_retries = settings.ai_max_retries

    def analyze(self, analysis_input: SceneAnalysisInput) -> SceneAnalysisResult:
        parts: list[dict[str, Any]] = [{"text": scene_analysis_prompt(analysis_input)}]
        for image in analysis_input.images:
            parts.append(
                {
                    "inline_data": {
                        "mime_type": image.content_type,
                        "data": image.data_base64,
                    }
                }
            )

        response = post_json(
            url=(
                "https://generativelanguage.googleapis.com/v1beta/"
                f"models/{self.model}:generateContent?key={self.api_key}"
            ),
            payload={
                "contents": [{"parts": parts}],
                "generationConfig": {"responseMimeType": "application/json"},
            },
            headers={},
            timeout_seconds=self.timeout_seconds,
            max_retries=self.max_retries,
        )
        text = extract_output_text(response)
        payload = parse_json_text(text, "Gemini")
        return normalize_scene_result(
            provider=self.provider,
            model=self.model,
            payload=payload,
            raw_response_ref={"candidate_count": len(response.get("candidates", []))},
        )


def extract_output_text(response: dict[str, Any]) -> str:
    for candidate in response.get("candidates", []):
        content = candidate.get("content", {})
        for part in content.get("parts", []):
            if isinstance(part.get("text"), str):
                return part["text"]

    return ""
