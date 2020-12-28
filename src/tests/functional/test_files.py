"""Tests for the Files route."""

import json
from typing import Any


def test_get_files(test_app: Any, add_file: Any, reset_db: Any) -> None:
    """Get files on an existing user returns all and only those user's files."""
    # Given
    reset_db()  # Empty all items.
    client = test_app.test_client()
    add_file("harry", "file_1")
    add_file("harry", "file_2")
    add_file("arnaud", "file_3")

    # When
    resp = client.get("/files?user=harry")
    data = json.loads(resp.data.decode())

    # Then
    assert resp.status_code == 200
    assert len(data["files"]) == 2
    assert [f["user"] for f in data["files"]] == ["harry", "harry"]
    assert "file_1" in [f["name"] for f in data["files"]]
    assert "file_2" in [f["name"] for f in data["files"]]


def get_files_no_user(test_app: Any, add_file: Any, reset_db: Any) -> None:
    """Get files on a non-existing user returns an empty list."""
    # Given
    reset_db()  # Empty all items.
    client = test_app.test_client()
    add_file("harry", "file_1")
    add_file("harry", "file_2")
    add_file("arnaud", "file_3")

    # When
    resp = client.get("/files?user=sam")
    data = json.loads(resp.data.decode())

    # Then
    assert resp.status_code == 200
    assert len(data["files"]) == 0


def put_files(test_app: Any, add_file: Any, reset_db: Any) -> None:
    """Put files with valid schema results in files being added to the db."""
    # Given
    reset_db()  # Empty all items.
    client = test_app.test_client()

    # When
    resp = client.put(
        "/files",
        data=json.dumps(
            {
                "user": "harry",
                "files": [
                    {"name": "file_1", "created": "2021-11-11@07:45:15", "type": "ppt"},
                    {"name": "file_2", "created": "2021-11-11@07:45:15", "type": "ppt"},
                ],
            }
        ),
        content_type="application/json",
    )
    data = json.loads(resp.data.decode())

    # Then
    assert resp.status_code == 200
    assert "file_12021-11-11@07:45:15" in data["response_states"]
    assert "file_22021-11-11@07:45:15" in data["response_states"]

    # When
    resp = client.get("/files?user=harry")
    data = json.loads(resp.data.decode())

    # Then
    assert resp.status_code == 200
    assert len(data["files"]) == 2
    assert [f["user"] for f in data["files"]] == ["harry", "harry"]
    assert "file_1" in [f["name"] for f in data["files"]]
    assert "file_2" in [f["name"] for f in data["files"]]


def put_duplicate_files(test_app: Any, add_file: Any, reset_db: Any) -> None:
    """Putting two of the same files results in first file being overwritten."""
    # Given
    reset_db()  # Empty all items.
    client = test_app.test_client()

    # When
    resp = client.put(
        "/files",
        data=json.dumps(
            {
                "user": "harry",
                "files": [
                    {
                        "name": "file_1",
                        "created": "2021-11-11@07:45:15",
                        "type": "ppt",
                        "feature_1": "123",
                    },
                    {
                        "name": "file_1",
                        "created": "2021-11-11@07:45:15",
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
    assert "file_12021-11-11@07:45:15" in data["response_states"]

    # When
    resp = client.get("/files?user=harry")
    data = json.loads(resp.data.decode())

    # Then
    assert resp.status_code == 200
    assert len(data["files"]) == 1
    assert data["files"][0]["user"] == "harry"
    assert data["files"][0]["name"] == "file_1"
    assert data["files"][0]["feature_2"] == "456"
    assert "feature_1" not in data["files"][0].keys()


def delete_files(test_app: Any, add_file: Any, reset_db: Any) -> None:
    """Deleting files should remove them from the database.

    Try and delete one of harrys and one of Arnauds files, under harry user, expect to see corresponding
    DELETED and NOT_FOUND status responses for those files. Arnauds file should still exist.

    """
    # Given
    reset_db()  # Empty all items.
    client = test_app.test_client()
    add_file("harry", "file_1", created="2021-11-11@07:45:15")
    add_file("harry", "file_2", created="2021-11-11@07:45:15")
    add_file("arnaud", "file_3", created="2021-11-11@07:45:15")

    # When
    resp = client.delete(
        "/files",
        data=json.dumps(
            {
                "user": "harry",
                "files": [
                    {"name": "file_1", "type": "pdf", "created": "2021-11-11@07:45:15"},
                    {"name": "file_3", "type": "pdf", "created": "2021-11-11@07:45:15"},
                ],
            }
        ),
        content_type="application/json",
    )
    data = json.loads(resp.data.decode())

    # Then
    assert resp.status_code == 200
    assert "file_12021-11-11@07:45:15" in data["response_states"]
    assert data["response_states"]["file_12021-11-11@07:45:15"] == "DELETED"
    assert data["response_states"]["file_32021-11-11@07:45:15"] == "NOT_FOUND"

    # When
    resp = client.get("/files?user=harry")
    data = json.loads(resp.data.decode())

    # Then
    assert resp.status_code == 200
    assert len(data["files"]) == 1
    assert data["files"][0]["user"] == "harry"
    assert data["files"][0]["name"] == "file_2"

    # When
    resp = client.get("/files?user=arnaud")
    data = json.loads(resp.data.decode())

    # Then
    assert resp.status_code == 200
    assert len(data["files"]) == 1
    assert data["files"][0]["user"] == "arnaud"
    assert data["files"][0]["name"] == "file_3"
