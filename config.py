from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv

DEFAULT_GRAPHQL_ENDPOINT = "https://mc.shop.kaspi.kz/mc/facade/graphql?opName=getOrderDetails"
DEFAULT_GRAPHQL_FALLBACK_ENDPOINT = "https://mc.shop.kaspi.kz/mc/facade/graphql"
DEFAULT_AUTH_URL = "https://kaspi.kz/mc/#/"


def _graphql_endpoints() -> tuple[str, ...]:
    configured = [
        os.getenv("GRAPHQL_ENDPOINT", DEFAULT_GRAPHQL_ENDPOINT),
        os.getenv("GRAPHQL_FALLBACK_ENDPOINT", DEFAULT_GRAPHQL_FALLBACK_ENDPOINT),
    ]
    endpoints: list[str] = []
    for raw_endpoint in configured:
        endpoint = _normalize_graphql_endpoint(raw_endpoint)
        if endpoint and endpoint not in endpoints:
            endpoints.append(endpoint)
    return tuple(endpoints)


def _normalize_graphql_endpoint(raw_endpoint: str | None) -> str:
    if not raw_endpoint:
        return DEFAULT_GRAPHQL_ENDPOINT
    endpoint = raw_endpoint.strip()
    parsed = urlparse(endpoint)
    if parsed.fragment or parsed.netloc == "kaspi.kz":
        return DEFAULT_GRAPHQL_ENDPOINT
    return endpoint


def _bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True, slots=True)
class Settings:
    merchant_uid: str
    input_file: Path
    output_file: Path
    headless: bool
    max_workers: int
    request_timeout: int
    retry_count: int
    storage_state_file: Path
    graphql_query_file: Path
    log_file: Path
    verify_ssl: bool
    ssl_ca_bundle: Path | None
    graphql_endpoints: tuple[str, ...]
    user_agent: str
    kaspi_origin: str = "https://kaspi.kz"
    kaspi_referer: str = "https://kaspi.kz/mc/#/"
    auth_url: str = DEFAULT_AUTH_URL

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        return cls(
            merchant_uid=os.getenv("MERCHANT_UID", "Applecity"),
            input_file=Path(os.getenv("INPUT_FILE", "orders.xlsx")),
            output_file=Path(os.getenv("OUTPUT_FILE", "result.xlsx")),
            headless=_bool(os.getenv("HEADLESS", "true")),
            max_workers=int(os.getenv("MAX_WORKERS", "5")),
            request_timeout=int(os.getenv("REQUEST_TIMEOUT", "30")),
            retry_count=int(os.getenv("RETRY_COUNT", "3")),
            storage_state_file=Path(os.getenv("STORAGE_STATE_FILE", "storage_state.json")),
            graphql_query_file=Path(
                os.getenv("GRAPHQL_QUERY_FILE", "graphql/get_order_details.graphql")
            ),
            log_file=Path(os.getenv("LOG_FILE", "logs/parser.log")),
            verify_ssl=_bool(os.getenv("VERIFY_SSL", "true")),
            ssl_ca_bundle=Path(value) if (value := os.getenv("SSL_CA_BUNDLE")) else None,
            graphql_endpoints=_graphql_endpoints(),
            user_agent=os.getenv(
                "USER_AGENT",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/126.0.0.0 Safari/537.36",
            ),
        )
