"""Test that all configuration options are correct for production."""

from typing import Any


def test_development_config(test_app: Any) -> None:
    """Development config should contain correct config options."""
    test_app.config.from_object("src.config.DevelopmentConfig")
    assert not test_app.config["TESTING"]


def test_production_config(test_app: Any) -> None:
    """Production config should contain correct config options."""
    test_app.config.from_object("src.config.ProductionConfig")
    assert not test_app.config["TESTING"]
