from __future__ import annotations

import pytest

pytest.importorskip("certifi")
pytest.importorskip("requests")

from graphql_client import GraphQLClient, GraphQLResponseError


def test_graphql_response_error_includes_validation_message() -> None:
    error = GraphQLResponseError([{"message": "Missing field argument 'id'"}])

    assert "Missing field argument" in str(error)


def test_places_query_uses_runtime_warehouse_type() -> None:
    client = GraphQLClient.__new__(GraphQLClient)
    payload = {
        "data": {
            "merchant": {
                "orderDetail": {"warehouse": {"__typename": "OrderWarehouse"}}
            }
        }
    }

    warehouse_type = client._warehouse_type(payload)

    assert warehouse_type == "OrderWarehouse"
    assert "... on OrderWarehouse" in client._places_query(warehouse_type)


def test_warehouse_type_rejects_invalid_graphql_type_name() -> None:
    client = GraphQLClient.__new__(GraphQLClient)
    payload = {
        "data": {
            "merchant": {
                "orderDetail": {"warehouse": {"__typename": "Warehouse { invalid"}}
            }
        }
    }

    assert client._warehouse_type(payload) is None


def test_merge_warehouse_adds_name_and_city_to_order_payload() -> None:
    client = GraphQLClient.__new__(GraphQLClient)
    payload = {
        "data": {
            "merchant": {
                "orderDetail": {"warehouse": {"__typename": "OrderWarehouse"}}
            }
        }
    }
    places_payload = {
        "data": {
            "merchant": {
                "orderDetail": {
                    "warehouse": {"name": "Main", "city": {"name": "Актобе"}}
                }
            }
        }
    }

    client._merge_warehouse(payload, places_payload)

    warehouse = payload["data"]["merchant"]["orderDetail"]["warehouse"]
    assert warehouse == {"name": "Main", "city": {"name": "Актобе"}}
