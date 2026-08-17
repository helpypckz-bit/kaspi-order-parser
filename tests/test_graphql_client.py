from __future__ import annotations

import pytest

pytest.importorskip("certifi")
pytest.importorskip("requests")

from graphql_client import GraphQLResponseError


def test_graphql_response_error_includes_validation_message() -> None:
    error = GraphQLResponseError([{"message": "Missing field argument 'id'"}])

    assert "Missing field argument" in str(error)
