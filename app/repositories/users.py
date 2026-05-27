from typing import Any
from uuid import UUID

from psycopg import Connection

LOCAL_AUTH_PROVIDER = "local"


def ensure_local_user(
    connection: Connection[dict[str, Any]],
    auth_subject: str,
) -> UUID:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            insert into app_users (auth_provider, auth_subject, display_name)
            values (%s, %s, %s)
            on conflict (auth_provider, auth_subject)
            do update set updated_at = app_users.updated_at
            returning user_id
            """,
            (LOCAL_AUTH_PROVIDER, auth_subject, auth_subject),
        )
        row = cursor.fetchone()

    if row is None:
        raise RuntimeError("Failed to resolve local user.")

    return row["user_id"]
