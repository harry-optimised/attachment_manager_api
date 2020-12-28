"""Tests for the Files route."""

import json
from typing import Any

import src.api.files
import src.auth


def test_get_files(
    test_app: Any, add_file: Any, reset_db: Any, monkeypatch: Any
) -> None:
    """Get files on an existing user returns all and only those user's files."""
    # Patch the auth functions.
    def mock_get_token_auth_header() -> str:
        """Mock get token auth header."""
        return "token"

    def mock_authenticate_token(token: str) -> bool:
        """Mock authenticate token."""
        return True

    def mock_get_user_id() -> str:
        """Respond with specific user when asked for user ID."""
        return "harry"

    monkeypatch.setattr(src.auth, "get_token_auth_header", mock_get_token_auth_header)
    monkeypatch.setattr(src.auth, "authenticate_token", mock_authenticate_token)
    monkeypatch.setattr(src.api.files, "get_user_id", mock_get_user_id)

    # Given
    reset_db()  # Empty all items.
    client = test_app.test_client()
    add_file("harry", "file_1")
    add_file("harry", "file_2")
    add_file("arnaud", "file_3")

    # When
    resp = client.get("/files")
    data = json.loads(resp.data.decode())

    # Then
    assert resp.status_code == 200
    assert len(data["files"]) == 2
    assert "file_1" in [f["name"] for f in data["files"]]
    assert "file_2" in [f["name"] for f in data["files"]]


def test_get_files_no_user(
    test_app: Any, add_file: Any, reset_db: Any, monkeypatch: Any
) -> None:
    """Get files on a non-existing user returns an empty list."""
    # Patch the auth functions.
    def mock_get_token_auth_header() -> str:
        """Mock get token auth header."""
        return "token"

    def mock_authenticate_token(token: str) -> bool:
        """Mock authenticate token."""
        return True

    def mock_get_user_id() -> str:
        """Respond with specific user when asked for user ID."""
        return "sam"

    monkeypatch.setattr(src.auth, "get_token_auth_header", mock_get_token_auth_header)
    monkeypatch.setattr(src.auth, "authenticate_token", mock_authenticate_token)
    monkeypatch.setattr(src.api.files, "get_user_id", mock_get_user_id)

    # Given
    reset_db()  # Empty all items.
    client = test_app.test_client()
    add_file("harry", "file_1")
    add_file("harry", "file_2")
    add_file("arnaud", "file_3")

    # When
    resp = client.get("/files")
    data = json.loads(resp.data.decode())

    # Then
    assert resp.status_code == 200
    assert len(data["files"]) == 0


def test_put_files(
    test_app: Any, add_file: Any, reset_db: Any, monkeypatch: Any
) -> None:
    """Put files with valid schema results in files being added to the db."""
    # Patch the auth functions.
    def mock_get_token_auth_header() -> str:
        """Mock get token auth header."""
        return "token"

    def mock_authenticate_token(token: str) -> bool:
        """Mock authenticate token."""
        return True

    def mock_get_user_id() -> str:
        """Respond with specific user when asked for user ID."""
        return "harry"

    monkeypatch.setattr(src.auth, "get_token_auth_header", mock_get_token_auth_header)
    monkeypatch.setattr(src.auth, "authenticate_token", mock_authenticate_token)
    monkeypatch.setattr(src.api.files, "get_user_id", mock_get_user_id)

    # Given
    reset_db()  # Empty all items.
    client = test_app.test_client()

    # When
    resp = client.put(
        "/files",
        data=json.dumps(
            {
                "files": [
                    {"name": "file_1", "created": "2021-11-11T07:45:15", "type": "ppt"},
                    {"name": "file_2", "created": "2021-11-11T07:45:15", "type": "ppt"},
                ],
            }
        ),
        content_type="application/json",
    )
    data = json.loads(resp.data.decode())

    # Then
    assert resp.status_code == 200
    assert "file_1" in data["status"]
    assert "file_2" in data["status"]

    # When
    resp = client.get("/files")
    data = json.loads(resp.data.decode())

    # Then
    assert resp.status_code == 200
    assert len(data["files"]) == 2
    assert "file_1" in [f["name"] for f in data["files"]]
    assert "file_2" in [f["name"] for f in data["files"]]


def test_put_duplicate_files(
    test_app: Any, add_file: Any, reset_db: Any, monkeypatch: Any
) -> None:
    """Putting two of the same files results in first file being overwritten."""
    # Patch the auth functions.
    def mock_get_token_auth_header() -> str:
        """Mock get token auth header."""
        return "token"

    def mock_authenticate_token(token: str) -> bool:
        """Mock authenticate token."""
        return True

    def mock_get_user_id() -> str:
        """Respond with specific user when asked for user ID."""
        return "harry"

    monkeypatch.setattr(src.auth, "get_token_auth_header", mock_get_token_auth_header)
    monkeypatch.setattr(src.auth, "authenticate_token", mock_authenticate_token)
    monkeypatch.setattr(src.api.files, "get_user_id", mock_get_user_id)

    # Given
    reset_db()  # Empty all items.
    client = test_app.test_client()

    # When
    resp = client.put(
        "/files",
        data=json.dumps(
            {
                "files": [
                    {
                        "name": "file_1",
                        "created": "2021-11-11T07:45:15",
                        "type": "ppt",
                        "feature_1": "123",
                    },
                    {
                        "name": "file_1",
                        "created": "2021-11-11T07:45:15",
                        "type": "ppt",
                        "feature_2": "456",
                    },
                ],
            }
        ),
        content_type="application/json",
    )
    data = json.loads(resp.data.decode())

    # Then
    assert resp.status_code == 200
    assert "file_1" in data["status"]

    # When
    resp = client.get("/files")
    data = json.loads(resp.data.decode())

    # Then
    assert resp.status_code == 200
    assert len(data["files"]) == 1
    assert data["files"][0]["name"] == "file_1"
    assert data["files"][0]["feature_2"] == "456"
    assert "feature_1" not in data["files"][0].keys()


def test_delete_files(
    test_app: Any, add_file: Any, reset_db: Any, monkeypatch: Any
) -> None:
    """Deleting files should remove them from the database.

    Try and delete one of harrys and one of Arnauds files, under harry user, expect to see corresponding
    DELETED and NOT_FOUND status responses for those files. Arnauds file should still exist.

    """
    # Patch the auth functions.
    def mock_get_token_auth_header() -> str:
        """Mock get token auth header."""
        return "token"

    def mock_authenticate_token(token: str) -> bool:
        """Mock authenticate token."""
        return True

    def mock_get_user_id() -> str:
        """Respond with specific user when asked for user ID."""
        return "harry"

    monkeypatch.setattr(src.auth, "get_token_auth_header", mock_get_token_auth_header)
    monkeypatch.setattr(src.auth, "authenticate_token", mock_authenticate_token)
    monkeypatch.setattr(src.api.files, "get_user_id", mock_get_user_id)

    # Given
    reset_db()  # Empty all items.
    client = test_app.test_client()
    add_file("harry", "file_1", created="2021-11-11T07:45:15")
    add_file("harry", "file_2", created="2021-11-11T07:45:15")
    add_file("arnaud", "file_3", created="2021-11-11T07:45:15")

    # When
    resp = client.delete(
        "/files",
        data=json.dumps(
            {
                "files": [
                    {"name": "file_1", "type": "pdf", "created": "2021-11-11T07:45:15"},
                    {"name": "file_3", "type": "pdf", "created": "2021-11-11T07:45:15"},
                ],
            }
        ),
        content_type="application/json",
    )
    data = json.loads(resp.data.decode())

    # Then
    assert resp.status_code == 200
    assert "file_1" in data["status"]
    assert "file_3" in data["status"]
    assert data["status"]["file_1"] == "DELETED"
    assert data["status"]["file_3"] == "NOT_FOUND"

    # When
    resp = client.get("/files")
    data = json.loads(resp.data.decode())

    # Then
    assert resp.status_code == 200
    assert len(data["files"]) == 1
    assert data["files"][0]["name"] == "file_2"

    # Now patch in arnaud as the user.
    def mock_get_user_id() -> str:
        """Respond with specific user when asked for user ID."""
        return "arnaud"

    monkeypatch.setattr(src.api.files, "get_user_id", mock_get_user_id)

    # When
    resp = client.get("/files?user=arnaud")
    data = json.loads(resp.data.decode())

    # Then
    assert resp.status_code == 200
    assert len(data["files"]) == 1
    assert data["files"][0]["name"] == "file_3"
