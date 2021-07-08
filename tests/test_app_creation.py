import os

import pytest

from app import config_name_mapper, create_app


def test_create_app():
    try:
        create_app()
    except SystemExit:
        # Clean git repository doesn't have `local_config.py`, so it is fine
        # if we get SystemExit error.
        pass


@pytest.mark.parametrize("flask_config_name", ["production", "development", "testing"])
def test_create_app_passing_flask_config_name(monkeypatch, flask_config_name):
    if flask_config_name == "production":
        from config import ProductionConfig

        monkeypatch.setattr(
            ProductionConfig,
            "SQLALCHEMY_DATABASE_URI",
            os.getenv("DATABASE_URI", "postgresql://postgres:@localhost/postgres_test"),
        )
        monkeypatch.setattr(ProductionConfig, "SECRET_KEY", "secret")
    create_app(flask_config_name=flask_config_name)


@pytest.mark.parametrize("flask_config_name", ["production", "development", "testing"])
def test_create_app_passing_flask_config_env(monkeypatch, flask_config_name):
    monkeypatch.setenv("FLASK_CONFIG", flask_config_name)
    if flask_config_name == "production":
        from config import ProductionConfig

        monkeypatch.setattr(
            ProductionConfig,
            "SQLALCHEMY_DATABASE_URI",
            os.getenv("DATABASE_URI", "postgresql://postgres:@localhost/postgres_test"),
        )
        monkeypatch.setattr(ProductionConfig, "SECRET_KEY", "secret")
    create_app()


def test_create_app_with_conflicting_config(monkeypatch):
    monkeypatch.setenv("FLASK_CONFIG", "production")
    with pytest.raises(AssertionError):
        create_app("development")


def test_create_app_with_non_existing_config():
    with pytest.raises(KeyError):
        create_app("non-existing-config")


def test_create_app_with_broken_import_config():
    config_name_mapper["broken-import-config"] = "broken-import-config"
    with pytest.raises(ImportError):
        create_app("broken-import-config")
    del config_name_mapper["broken-import-config"]
