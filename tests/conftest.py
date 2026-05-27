from collections.abc import Iterator
from pathlib import Path
import shutil

import psycopg
import pytest
from fastapi.testclient import TestClient
from psycopg.rows import dict_row
from redis import Redis

from app.main import app
from app.settings import get_settings

TEST_USER_PREFIX = "pytest-"


@pytest.fixture
def client() -> Iterator[TestClient]:
    cleanup_test_state()
    with TestClient(app) as test_client:
        yield test_client
    cleanup_test_state()


def cleanup_test_state() -> None:
    settings = get_settings()
    test_user_pattern = f"{TEST_USER_PREFIX}%"
    with psycopg.connect(settings.postgres_dsn, row_factory=dict_row) as connection:
        with connection.cursor() as cursor:
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

    storage_root = Path(settings.local_storage_root) / "users"
    if storage_root.exists():
        shutil.rmtree(storage_root)
