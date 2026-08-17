from pathlib import Path


def test_get_order_details_uses_kaspi_string_merchant_id() -> None:
    query = Path("graphql/get_order_details.graphql").read_text(encoding="utf-8")

    assert "$merchantUid: String!" in query
    assert "$merchantUid: ID!" not in query
    assert "merchant(id: $merchantUid)" in query


def test_get_order_details_requests_destination_and_warehouse_cities() -> None:
    query = Path("graphql/get_order_details.graphql").read_text(encoding="utf-8")

    assert "destination {\n        city {\n          name" in query
    assert "warehouse {\n        city {\n          name" in query
