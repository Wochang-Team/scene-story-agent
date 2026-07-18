from collections.abc import Iterator
from pathlib import Path
import shutil

import psycopg
import pytest
from fastapi.testclient import TestClient
from psycopg.rows import dict_row
from redis import Redis

from app.main import app
from app.settings import Settings, get_settings

TEST_USER_PREFIX = "pytest-"


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    test_storage_root = tmp_path / "local_storage"
    cleanup_test_state()
    app.dependency_overrides[get_settings] = lambda: mock_provider_settings(test_storage_root)
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_settings, None)
        cleanup_test_state(storage_root=test_storage_root)


def mock_provider_settings(test_storage_root: Path) -> Settings:
    settings = get_settings()
    return Settings(
        **{
            **settings.model_dump(),
            "local_storage_root": str(test_storage_root),
            "ai_provider": "mock",
            "ai_model": "mock-scene-v1",
            "embedding_provider": "mock",
            "embedding_model": "mock-embedding-v1",
            "embedding_dimension": 8,
        }
    )


def cleanup_test_state(storage_root: Path | None = None) -> None:
    settings = get_settings()
    target_storage_root = storage_root or Path(settings.local_storage_root)
    test_user_pattern = f"{TEST_USER_PREFIX}%"
    with psycopg.connect(
        **settings.postgres_connection_kwargs,
        row_factory=dict_row,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                select user_id
                from app_users
                where auth_provider = 'local'
                  and auth_subject like %s
                """,
                (test_user_pattern,),
            )
            test_user_ids = [row["user_id"] for row in cursor.fetchall()]
            cleanup_statements = [
                """
                delete from record_ai_interpretations
                where record_id in (
                    select r.record_id
                    from records r
                    join app_users u on u.user_id = r.user_id
                    where u.auth_provider = 'local'
                      and u.auth_subject like %s
                )
                """,
                """
                delete from timeline_candidates
                where user_id in (
                    select user_id
                    from app_users
                    where auth_provider = 'local'
                      and auth_subject like %s
                )
                """,
                """
                delete from record_relations
                where source_record_id in (
                    select r.record_id
                    from records r
                    join app_users u on u.user_id = r.user_id
                    where u.auth_provider = 'local'
                      and u.auth_subject like %s
                )
                   or target_record_id in (
                    select r.record_id
                    from records r
                    join app_users u on u.user_id = r.user_id
                    where u.auth_provider = 'local'
                      and u.auth_subject like %s
                )
                """,
                """
                delete from record_embeddings
                where record_id in (
                    select r.record_id
                    from records r
                    join app_users u on u.user_id = r.user_id
                    where u.auth_provider = 'local'
                      and u.auth_subject like %s
                )
                """,
                """
                delete from processing_jobs
                where record_id in (
                    select r.record_id
                    from records r
                    join app_users u on u.user_id = r.user_id
                    where u.auth_provider = 'local'
                      and u.auth_subject like %s
                )
                """,
                """
                delete from record_assets
                where record_id in (
                    select r.record_id
                    from records r
                    join app_users u on u.user_id = r.user_id
                    where u.auth_provider = 'local'
                      and u.auth_subject like %s
                )
                """,
                """
                delete from records
                where user_id in (
                    select user_id
                    from app_users
                    where auth_provider = 'local'
                      and auth_subject like %s
                )
                """,
                """
                delete from app_users
                where auth_provider = 'local'
                  and auth_subject like %s
                """,
            ]
            for statement in cleanup_statements:
                cursor.execute(statement, tuple([test_user_pattern] * statement.count("%s")))
            connection.commit()

    redis_client = Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        decode_responses=True,
    )
    try:
        for pattern in (
            f"user:auth:local:{TEST_USER_PREFIX}*",
            "job:*",
            "record:job:dedupe:*",
        ):
            keys = list(redis_client.scan_iter(match=pattern))
            if keys:
                redis_client.delete(*keys)
    finally:
        redis_client.close()

    for user_id in test_user_ids:
        user_storage_root = target_storage_root / "users" / str(user_id)
        if user_storage_root.exists():
            shutil.rmtree(user_storage_root)
