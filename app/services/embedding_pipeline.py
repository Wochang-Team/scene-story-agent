from datetime import datetime
from typing import Any
from uuid import UUID

from psycopg import Connection

from app.providers.embeddings import get_embedding_provider
from app.repositories import assets as asset_repository
from app.repositories import embeddings as embedding_repository
from app.repositories import relations as relation_repository
from app.repositories import timeline_candidates as timeline_repository
from app.settings import Settings


def build_input_snapshot(record: dict[str, Any], assets: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "record_id": str(record["record_id"]),
        "memo": record["memo"],
        "emotion": record["emotion"],
        "satisfaction_score": record["satisfaction_score"],
        "happened_at": record["happened_at"].isoformat() if record["happened_at"] else None,
        "asset_count": len(assets),
        "asset_types": sorted({asset["asset_type"] for asset in assets}),
        "content_types": sorted({asset["content_type"] for asset in assets}),
    }


def snapshot_to_text(snapshot: dict[str, Any]) -> str:
    parts = [
        snapshot.get("memo") or "",
        snapshot.get("emotion") or "",
        str(snapshot.get("satisfaction_score") or ""),
        snapshot.get("happened_at") or "",
        " ".join(snapshot.get("asset_types") or []),
        " ".join(snapshot.get("content_types") or []),
    ]
    return " | ".join(part for part in parts if part)


def build_embedding_and_candidates(
    connection: Connection[dict[str, Any]],
    settings: Settings,
    user_id: UUID,
    record: dict[str, Any],
) -> dict[str, Any]:
    provider = get_embedding_provider(settings)
    assets = asset_repository.list_assets(connection, record["record_id"])
    snapshot = build_input_snapshot(record, assets)
    vector = provider.embed(snapshot_to_text(snapshot))

    embedding = embedding_repository.create_embedding(
        connection=connection,
        record_id=record["record_id"],
        provider=provider.provider,
        model=provider.model,
        dimension=provider.dimension,
        vector=vector,
        input_snapshot=snapshot,
    )

    similar_records = embedding_repository.find_similar_records(
        connection=connection,
        user_id=user_id,
        source_record_id=record["record_id"],
        vector=vector,
        dimension=provider.dimension,
        limit=settings.similar_records_limit,
    )

    relations = []
    for candidate in similar_records:
        relation = relation_repository.upsert_relation(
            connection=connection,
            source_record_id=record["record_id"],
            target_record_id=candidate["record_id"],
            relation_type="similar_scene",
            similarity_score=candidate["similarity_score"],
            reasons={
                "source": "mock_embedding",
                "provider": provider.provider,
                "model": provider.model,
            },
        )
        relations.append(relation)

        if float(candidate["similarity_score"]) >= settings.similarity_threshold:
            relations.append(
                relation_repository.upsert_relation(
                    connection=connection,
                    source_record_id=record["record_id"],
                    target_record_id=candidate["record_id"],
                    relation_type="revisit_candidate",
                    similarity_score=candidate["similarity_score"],
                    reasons={
                        "source": "mock_embedding",
                        "threshold": settings.similarity_threshold,
                    },
                )
            )

    timeline_candidates = build_timeline_candidates(
        connection=connection,
        user_id=user_id,
        record=record,
        relation_count=len(relations),
    )

    return {
        "embedding": embedding,
        "relations": relations,
        "timeline_candidates": timeline_candidates,
    }


def build_timeline_candidates(
    connection: Connection[dict[str, Any]],
    user_id: UUID,
    record: dict[str, Any],
    relation_count: int,
) -> list[dict[str, Any]]:
    candidates = []
    happened_at: datetime | None = record["happened_at"] or record["created_at"]

    if happened_at is not None:
        candidates.append(
            timeline_repository.upsert_timeline_candidate(
                connection=connection,
                user_id=user_id,
                record_id=record["record_id"],
                timeline_type="time",
                grouping_key=happened_at.strftime("%Y-%m"),
                confidence_score=0.80,
                reasons={"source": "record_time"},
            )
        )

    if record["emotion"]:
        candidates.append(
            timeline_repository.upsert_timeline_candidate(
                connection=connection,
                user_id=user_id,
                record_id=record["record_id"],
                timeline_type="emotion",
                grouping_key=record["emotion"],
                confidence_score=0.70,
                reasons={"source": "record_emotion"},
            )
        )

    if relation_count > 0:
        candidates.append(
            timeline_repository.upsert_timeline_candidate(
                connection=connection,
                user_id=user_id,
                record_id=record["record_id"],
                timeline_type="scene_type",
                grouping_key="similar_scene",
                confidence_score=0.60,
                reasons={"source": "mock_embedding_relations"},
            )
        )

    topic = extract_topic(record["memo"])
    if topic:
        candidates.append(
            timeline_repository.upsert_timeline_candidate(
                connection=connection,
                user_id=user_id,
                record_id=record["record_id"],
                timeline_type="topic",
                grouping_key=topic,
                confidence_score=0.50,
                reasons={"source": "record_memo_keyword"},
            )
        )

    return candidates


def extract_topic(memo: str | None) -> str | None:
    if not memo:
        return None

    words = [word.strip(".,!?()[]{}").lower() for word in memo.split()]
    words = [word for word in words if len(word) >= 2]
    if not words:
        return None
    return words[0][:40]
