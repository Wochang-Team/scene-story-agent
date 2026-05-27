from typing import Any
from uuid import UUID

from psycopg import Connection

from app.providers.ai import get_scene_analysis_provider
from app.repositories import ai_interpretations as interpretation_repository
from app.repositories import assets as asset_repository
from app.schemas.ai import AssetForAnalysis, SceneAnalysisInput
from app.services.image_processing import prepare_image_for_analysis
from app.services.storage import LocalStorage
from app.settings import Settings


SUPPORTED_ANALYSIS_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


def analyze_record(
    connection: Connection[dict[str, Any]],
    settings: Settings,
    record: dict[str, Any],
) -> dict[str, Any]:
    assets = asset_repository.list_assets(connection, record["record_id"])
    storage = LocalStorage(settings)
    provider = get_scene_analysis_provider(settings)

    analysis_assets = [
        AssetForAnalysis(
            asset_id=asset["asset_id"],
            asset_type=asset["asset_type"],
            content_type=asset["content_type"],
            object_key=asset["object_key"],
            byte_size=asset["byte_size"],
        )
        for asset in assets
    ]
    images = []
    for asset in assets:
        if asset["content_type"] not in SUPPORTED_ANALYSIS_IMAGE_TYPES:
            continue
        images.append(
            prepare_image_for_analysis(
                path=storage.resolve_path(asset["object_key"]),
                content_type=asset["content_type"],
                max_bytes=settings.ai_image_max_bytes,
            )
        )

    analysis_input = SceneAnalysisInput(
        record_id=record["record_id"],
        memo=record["memo"],
        emotion=record["emotion"],
        satisfaction_score=record["satisfaction_score"],
        happened_at=record["happened_at"],
        assets=analysis_assets,
        images=images,
    )
    result = provider.analyze(analysis_input)
    return interpretation_repository.create_interpretation(
        connection=connection,
        record_id=record["record_id"],
        result=result,
    )
