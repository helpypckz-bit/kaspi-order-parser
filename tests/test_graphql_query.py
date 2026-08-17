from pathlib import Path


def test_get_order_details_uses_kaspi_string_merchant_id() -> None:
    query = Path("graphql/get_order_details.graphql").read_text(encoding="utf-8")

    assert "$merchantUid: String!" in query
    assert "$merchantUid: ID!" not in query
    assert "merchant(id: $merchantUid)" in query


def test_get_order_details_requests_cities_through_order_place_fragments() -> None:
    query = Path("graphql/get_order_details.graphql").read_text(encoding="utf-8")

    destination_fragment = """destination {
        __typename
        ... on Postomat {
          city {
            name
          }
        }
      }"""
    warehouse_selection = """warehouse {
        __typename
      }"""

    assert destination_fragment in query
    assert warehouse_selection in query
    assert "... on Warehouse" not in query
