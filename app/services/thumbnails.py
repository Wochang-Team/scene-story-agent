from typing import Any
from uuid import UUID

from psycopg import Connection

from app.repositories import assets as asset_repository
from app.services.image_processing import create_square_thumbnail
from app.services.storage import LocalStorage
from app.settings import Settings

THUMBNAIL_ASSET_TYPE = "thumbnail"
THUMBNAIL_CONTENT_TYPE = "image/webp"
THUMBNAIL_SUFFIX = ".webp"
THUMBNAIL_SOURCE_TYPES = {"image/jpeg", "image/png", "image/webp"}


def generate_record_thumbnails(
    connection: Connection[dict[str, Any]],
    settings: Settings,
    user_id: UUID,
    record_id: UUID,
) -> list[dict[str, Any]]:
    assets = asset_repository.list_assets(connection, record_id)
    existing = [asset for asset in assets if asset["asset_type"] == THUMBNAIL_ASSET_TYPE]
    if existing:
        return existing

    storage = LocalStorage(settings)
    created = []
    for asset in assets:
        if asset["asset_type"] == THUMBNAIL_ASSET_TYPE:
            continue
        if asset["content_type"] not in THUMBNAIL_SOURCE_TYPES:
            continue

        try:
            data = create_square_thumbnail(storage.resolve_path(asset["object_key"]))
        except ValueError:
            continue

        stored_file = storage.save_bytes(
            user_id=user_id,
            record_id=record_id,
            data=data,
            asset_type=THUMBNAIL_ASSET_TYPE,
            content_type=THUMBNAIL_CONTENT_TYPE,
            suffix=THUMBNAIL_SUFFIX,
        )
        try:
            created.append(
                asset_repository.create_asset(
                    connection=connection,
                    record_id=record_id,
                    asset_type=stored_file.asset_type,
                    bucket_name=stored_file.bucket_name,
                    object_key=stored_file.object_key,
                    content_type=stored_file.content_type,
                    byte_size=stored_file.byte_size,
                    checksum_sha256=stored_file.checksum_sha256,
                )
            )
        except Exception:
            storage.delete(stored_file.object_key)
            raise

    return created
