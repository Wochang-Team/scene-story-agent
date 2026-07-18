from collections.abc import Iterator
from typing import Annotated, Any

import psycopg
from fastapi import Depends
from psycopg import Connection
from psycopg.rows import dict_row

from app.settings import Settings, get_settings


def get_connection(
    settings: Annotated[Settings, Depends(get_settings)],
) -> Iterator[Connection[dict[str, Any]]]:
    with psycopg.connect(
        **settings.postgres_connection_kwargs,
        row_factory=dict_row,
    ) as connection:
        yield connection
