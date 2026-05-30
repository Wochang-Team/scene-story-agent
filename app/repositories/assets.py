from typing import Any
from uuid import UUID

from psycopg import Connection

ASSET_COLUMNS = """
    asset_id,
    record_id,
    asset_type,
    storage_provider,
    bucket_name,
    object_key,
    content_type,
    byte_size,
    width,
    height,
    duration_seconds,
    checksum_sha256,
    created_at
"""


def create_asset(
    connection: Connection[dict[str, Any]],
    record_id: UUID,
    asset_type: str,
    bucket_name: str,
    object_key: str,
    content_type: str,
    byte_size: int,
    checksum_sha256: str,
) -> dict[str, Any]:
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            insert into record_assets (
                record_id,
                asset_type,
                storage_provider,
                bucket_name,
                object_key,
                content_type,
                byte_size,
                checksum_sha256
            )
            values (%s, %s, 'local', %s, %s, %s, %s, %s)
            returning {ASSET_COLUMNS}
            """,
            (
                record_id,
                asset_type,
                bucket_name,
                object_key,
                content_type,
                byte_size,
                checksum_sha256,
            ),
        )
        row = cursor.fetchone()

    if row is None:
        raise RuntimeError("Failed to create asset.")

    return row


def list_assets(
    connection: Connection[dict[str, Any]],
    record_id: UUID,
) -> list[dict[str, Any]]:
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            select {ASSET_COLUMNS}
            from record_assets
            where record_id = %s
              and deleted_at is null
            order by created_at asc, asset_id asc
            """,
            (record_id,),
        )
        rows = cursor.fetchall()

    return list(rows)


def get_asset(
    connection: Connection[dict[str, Any]],
    record_id: UUID,
    asset_id: UUID,
) -> dict[str, Any] | None:
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            select {ASSET_COLUMNS}
            from record_assets
            where record_id = %s
              and asset_id = %s
              and deleted_at is null
            """,
            (record_id, asset_id),
        )
        return cursor.fetchone()


def mark_asset_deleted(
    connection: Connection[dict[str, Any]],
    record_id: UUID,
    asset_id: UUID,
) -> bool:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            update record_assets
            set deleted_at = now()
            where record_id = %s
              and asset_id = %s
              and deleted_at is null
            returning asset_id
            """,
            (record_id, asset_id),
        )
        return cursor.fetchone() is not None


def mark_assets_deleted_for_record(
    connection: Connection[dict[str, Any]],
    record_id: UUID,
) -> int:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            update record_assets
            set deleted_at = now()
            where record_id = %s
              and deleted_at is null
            """,
            (record_id,),
        )
        return cursor.rowcount
