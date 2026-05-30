from typing import Any

from app.providers.ai import normalize_scene_result, scene_analysis_prompt
from app.providers.http import parse_json_text, post_json, require_api_key
from app.schemas.ai import SceneAnalysisInput, SceneAnalysisResult
from app.settings import Settings


class OpenAISceneAnalysisProvider:
    provider = "openai"

    def __init__(self, settings: Settings) -> None:
        self.model = settings.ai_model
        self.api_key = require_api_key(settings.openai_api_key, "OpenAI")
        self.timeout_seconds = settings.ai_timeout_seconds
        self.max_retries = settings.ai_max_retries

    def analyze(self, analysis_input: SceneAnalysisInput) -> SceneAnalysisResult:
        content: list[dict[str, Any]] = [
            {"type": "input_text", "text": scene_analysis_prompt(analysis_input)}
        ]
        for image in analysis_input.images:
            content.append(
                {
                    "type": "input_image",
                    "image_url": f"data:{image.content_type};base64,{image.data_base64}",
                }
            )

        response = post_json(
            url="https://api.openai.com/v1/responses",
            payload={
                "model": self.model,
                "input": [{"role": "user", "content": content}],
            },
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout_seconds=self.timeout_seconds,
            max_retries=self.max_retries,
        )
        text = extract_output_text(response)
        payload = parse_json_text(text, "OpenAI")
        return normalize_scene_result(
            provider=self.provider,
            model=self.model,
            payload=payload,
            raw_response_ref={
                "response_id": response.get("id"),
                "token_usage": openai_token_usage(response),
            },
        )


def extract_output_text(response: dict[str, Any]) -> str:
    if isinstance(response.get("output_text"), str):
        return response["output_text"]

    for item in response.get("output", []):
        for content in item.get("content", []):
            if isinstance(content.get("text"), str):
                return content["text"]

    return ""


def openai_token_usage(response: dict[str, Any]) -> dict[str, int | None]:
    usage = response.get("usage") if isinstance(response.get("usage"), dict) else {}
    input_tokens = usage.get("input_tokens") or usage.get("prompt_tokens")
    output_tokens = usage.get("output_tokens") or usage.get("completion_tokens")
    total_tokens = usage.get("total_tokens")
    if total_tokens is None:
        total_tokens = sum(
            value for value in [input_tokens, output_tokens] if isinstance(value, int)
        ) or None
    return {
        "used_tokens": total_tokens,
        "remaining_tokens": usage.get("remaining_tokens"),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
    }
