from hashlib import sha256
from math import sqrt
from typing import Any
from typing import Protocol

from app.providers.http import ProviderHttpError, post_json, require_api_key
from app.settings import Settings


class EmbeddingProvider(Protocol):
    provider: str
    model: str
    dimension: int

    def embed(self, text: str) -> list[float]:
        """Return an embedding vector for text."""


class MockEmbeddingProvider:
    provider = "mock"

    def __init__(self, model: str, dimension: int) -> None:
        self.model = model
        self.dimension = dimension

    def embed(self, text: str) -> list[float]:
        seed = text.encode("utf-8")
        values: list[float] = []

        for index in range(self.dimension):
            digest = sha256(seed + index.to_bytes(2, "big")).digest()
            integer = int.from_bytes(digest[:8], "big")
            values.append((integer / ((1 << 64) - 1)) * 2 - 1)

        norm = sqrt(sum(value * value for value in values)) or 1.0
        return [round(value / norm, 8) for value in values]


class GeminiEmbeddingProvider:
    provider = "gemini"

    def __init__(self, settings: Settings) -> None:
        self.model = settings.embedding_model
        self.dimension = settings.embedding_dimension
        self.api_key = require_api_key(settings.gemini_api_key, "Gemini")
        self.timeout_seconds = settings.ai_timeout_seconds
        self.max_retries = settings.ai_max_retries

    def embed(self, text: str) -> list[float]:
        response = post_json(
            url=(
                "https://generativelanguage.googleapis.com/v1beta/"
                f"models/{self.model}:embedContent"
            ),
            payload={
                "content": {"parts": [{"text": text}]},
                "output_dimensionality": self.dimension,
            },
            headers={"x-goog-api-key": self.api_key},
            timeout_seconds=self.timeout_seconds,
            max_retries=self.max_retries,
        )
        values = extract_embedding_values(response, "Gemini")
        if len(values) != self.dimension:
            raise ProviderHttpError(
                "Gemini embedding dimension mismatch: "
                f"expected {self.dimension}, got {len(values)}."
            )
        return values


def extract_embedding_values(response: dict[str, Any], provider_name: str) -> list[float]:
    values = response.get("embedding", {}).get("values")
    if values is None:
        embeddings = response.get("embeddings")
        if isinstance(embeddings, list) and embeddings:
            values = embeddings[0].get("values")

    if not isinstance(values, list):
        raise ProviderHttpError(f"{provider_name} response did not include embedding values.")

    try:
        return [float(value) for value in values]
    except (TypeError, ValueError) as exc:
        raise ProviderHttpError(f"{provider_name} embedding values must be numbers.") from exc


def get_embedding_provider(settings: Settings) -> EmbeddingProvider:
    if settings.embedding_provider == "mock":
        return MockEmbeddingProvider(
            model=settings.embedding_model,
            dimension=settings.embedding_dimension,
        )
    if settings.embedding_provider == "gemini":
        return GeminiEmbeddingProvider(settings)

    raise ProviderHttpError(
        f"Embedding provider is not supported: {settings.embedding_provider}"
    )
