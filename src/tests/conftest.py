"""Setup the fixtures for all test suites."""

from typing import Any

import pytest

from src import cm, create_app


@pytest.fixture(scope="module")
def test_app() -> None:
    """Create the test app fixture."""
    app = create_app()
    with app.app_context():
        yield app


@pytest.fixture(scope="function")
def reset_db() -> Any:
    """Remove all items from the database."""

    def _reset_db() -> Any:
        all_items = cm.scan_db()
        for i in all_items:
            cm.delete_file(i["user"], i)
        return True

    return _reset_db


@pytest.fixture(scope="function")
def add_file() -> Any:
    """Add a file directly to the database."""

    def _add_file(
        user: str, name: str, type: str = "pdf", created: str = "2020-12-12@08:30:00"
    ) -> dict:
        file = {"name": name, "type": type, "created": created}
        cm.put_file(user, file)
        return file

    return _add_file
