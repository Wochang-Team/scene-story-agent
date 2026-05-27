from hashlib import sha256
from math import sqrt
from typing import Protocol

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


def get_embedding_provider(settings: Settings) -> EmbeddingProvider:
    if settings.embedding_provider == "mock":
        return MockEmbeddingProvider(
            model=settings.embedding_model,
            dimension=settings.embedding_dimension,
        )

    raise NotImplementedError(
        f"Embedding provider is not implemented: {settings.embedding_provider}"
    )
