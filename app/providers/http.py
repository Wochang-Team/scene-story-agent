from collections.abc import Callable
import json
from time import sleep
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class ProviderHttpError(RuntimeError):
    pass


def post_json(
    url: str,
    payload: dict[str, Any],
    headers: dict[str, str],
    timeout_seconds: int,
    max_retries: int,
) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    last_error: Exception | None = None

    for attempt in range(max_retries + 1):
        request = Request(
            url=url,
            data=body,
            headers={**headers, "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            last_error = exc
            if exc.code < 500 and exc.code != 429:
                detail = exc.read().decode("utf-8")
                raise ProviderHttpError(f"Provider request failed: HTTP {exc.code} {detail}") from exc
        except URLError as exc:
            last_error = exc

        if attempt < max_retries:
            sleep(min(2**attempt, 5))

    raise ProviderHttpError("Provider request failed after retries.") from last_error


def parse_json_text(text: str, provider_name: str) -> dict[str, Any]:
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ProviderHttpError(f"{provider_name} response was not valid JSON.") from exc

    if not isinstance(value, dict):
        raise ProviderHttpError(f"{provider_name} response JSON must be an object.")

    return value


def require_api_key(api_key: str | None, provider_name: str) -> str:
    if not api_key:
        raise ProviderHttpError(f"{provider_name} API key is not configured.")
    return api_key
