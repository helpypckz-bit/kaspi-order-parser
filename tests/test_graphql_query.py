from pathlib import Path


def test_get_order_details_uses_kaspi_string_merchant_id() -> None:
    query = Path("graphql/get_order_details.graphql").read_text(encoding="utf-8")

    assert "$merchantUid: String!" in query
    assert "$merchantUid: ID!" not in query
    assert "merchant(id: $merchantUid)" in query
