"""Tests for the ping route."""

import json
from typing import Any


def test_ping(test_app: Any) -> None:
    """Ping route should return the correct response."""
    # Given
    client = test_app.test_client()

    # When
    resp = client.get("/ping")
    data = json.loads(resp.data.decode())

    # Then
    assert resp.status_code == 200
    assert "pong" in data["message"]
    assert "success" in data["status"]
