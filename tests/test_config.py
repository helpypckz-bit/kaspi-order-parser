import pytest

pytest.importorskip("dotenv")

from config import DEFAULT_GRAPHQL_ENDPOINT, _normalize_graphql_endpoint


def test_normalize_graphql_endpoint_rejects_kaspi_page_route() -> None:
    endpoint = _normalize_graphql_endpoint("https://kaspi.kz/mc/#/facade/graphql?opName=getOrderDetails")

    assert endpoint == DEFAULT_GRAPHQL_ENDPOINT


def test_normalize_graphql_endpoint_keeps_api_route() -> None:
    endpoint = "https://mc.shop.kaspi.kz/mc/facade/graphql?opName=getOrderDetails"

    assert _normalize_graphql_endpoint(endpoint) == endpoint
