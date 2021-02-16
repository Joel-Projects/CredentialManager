import os

import pytest

from app import configNameMapper, create_app


def test_create_app():
    try:
        create_app()
    except SystemExit:
        # Clean git repository doesn't have `local_config.py`, so it is fine
        # if we get SystemExit error.
        pass


@pytest.mark.parametrize("flaskConfigName", ["production", "development", "testing"])
def test_create_app_passing_flaskConfigName(monkeypatch, flaskConfigName):
    if flaskConfigName == "production":
        from config import ProductionConfig

        monkeypatch.setattr(
            ProductionConfig,
            "SQLALCHEMY_DATABASE_URI",
            os.getenv("DATABASE_URI", "postgresql://postgres:@localhost/postgres_test"),
        )
        monkeypatch.setattr(ProductionConfig, "SECRET_KEY", "secret")
    create_app(flaskConfigName=flaskConfigName)


@pytest.mark.parametrize("flaskConfigName", ["production", "development", "testing"])
def test_create_app_passing_FLASK_CONFIG_env(monkeypatch, flaskConfigName):
    monkeypatch.setenv("FLASK_CONFIG", flaskConfigName)
    if flaskConfigName == "production":
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
    configNameMapper["broken-import-config"] = "broken-import-config"
    with pytest.raises(ImportError):
        create_app("broken-import-config")
    del configNameMapper["broken-import-config"]
