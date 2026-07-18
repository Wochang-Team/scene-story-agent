from app.settings import Settings


def make_settings(password: str) -> Settings:
    return Settings(
        postgres_db="scene_story_agent",
        postgres_user="postgres",
        postgres_password=password,
        postgres_host="192.168.0.103",
        postgres_port=5433,
    )


def test_postgres_connection_kwargs_preserve_reserved_password_characters() -> None:
    password = "reserved:/?#[]@!$&'()*+,;=characters"

    connection_kwargs = make_settings(password).postgres_connection_kwargs

    assert connection_kwargs == {
        "dbname": "scene_story_agent",
        "user": "postgres",
        "password": password,
        "host": "192.168.0.103",
        "port": 5433,
    }


def test_postgres_log_environment_redacts_password() -> None:
    log_environment = make_settings("do-not-log-this").postgres_log_environment

    assert log_environment == {
        "POSTGRES_DB": "scene_story_agent",
        "POSTGRES_USER": "postgres",
        "POSTGRES_PASSWORD": "[configured]",
        "POSTGRES_HOST": "192.168.0.103",
        "POSTGRES_PORT": 5433,
    }
