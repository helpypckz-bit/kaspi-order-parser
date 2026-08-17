from pathlib import Path


def test_get_order_details_uses_kaspi_string_merchant_id() -> None:
    query = Path("graphql/get_order_details.graphql").read_text(encoding="utf-8")

    assert "$merchantUid: String!" in query
    assert "$merchantUid: ID!" not in query
    assert "merchant(id: $merchantUid)" in query


def test_get_order_details_requests_supported_order_place_fragments() -> None:
    query = Path("graphql/get_order_details.graphql").read_text(encoding="utf-8")

    assert "... on Postomat" in query
    assert "... on OrderAddress" in query
    assert "... on Point" in query
    assert "... on Warehouse" not in query


def test_get_order_details_requests_delivery_dates_and_costs() -> None:
    query = Path("graphql/get_order_details.graphql").read_text(encoding="utf-8")

    assert "actualDeliveryDate" in query
    assert "orderSteps" in query
    assert "actualTime" in query
    assert "deliverySubsidyCost" in query
    assert "deliveryCost" in query
