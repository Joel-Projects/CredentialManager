import pytest

from app.modules.database_credentials.models import DatabaseCredential
from tests.params import labels, users
from tests.responseStatuses import assert201, assert422, assert403Create
from tests.utils import assertCreated, assertRenderedTemplate, captured_templates

data = {
    "app_name": "database_credential",
    "database_flavor": "postgres",
    "database_host": "localhost",
    "database_port": 5432,
    "database_username": "postgres",
    "database_password": "database_password",
    "database": "postgres",
    "use_ssh": True,
    "ssh_host": "ssh_host",
    "ssh_port": 22,
    "ssh_username": "root",
    "ssh_password": "pass",
    "use_ssh_key": True,
    "private_key": "private_key",
    "private_key_passphrase": "passphrase",
}


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_create_database_credential(flask_app_client, loginAs):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            "/database_credentials",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        assert201(response)
        assertRenderedTemplate(templates, "database_credentials.html")
        databaseCredential = DatabaseCredential.query.filter_by(
            app_name="database_credential"
        ).first()
        assertCreated(databaseCredential, data)


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_create_database_credential_profile(flask_app_client, loginAs):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            f"/profile/database_credentials",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        assert201(response)
        assertRenderedTemplate(templates, "database_credentials.html")
        databaseCredential = DatabaseCredential.query.filter_by(
            app_name="database_credential"
        ).first()
        assert databaseCredential is not None
        assert databaseCredential.id == 1


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_create_database_credential_other_user(flask_app_client, loginAs, regular_user):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            "/database_credentials",
            content_type="application/x-www-form-urlencoded",
            data={"owner": regular_user.id, **data},
        )
        if loginAs.is_admin or loginAs.is_internal:
            assert201(response)
            assertRenderedTemplate(templates, "database_credentials.html")
            databaseCredential = DatabaseCredential.query.filter_by(
                app_name="database_credential"
            ).first()
            assert databaseCredential is not None
            assert databaseCredential.id == 1
            assert databaseCredential.owner == regular_user
        else:
            assert403Create(response)
            databaseCredential = DatabaseCredential.query.filter_by(
                app_name="database_credential"
            ).first()
            assert databaseCredential is None


def test_create_database_credential_bad_params(flask_app_client, regularUserInstance):
    data["app_name"] = "da"
    response = flask_app_client.post(
        "/database_credentials",
        content_type="application/x-www-form-urlencoded",
        data=data,
    )
    assert response.status_code == 200
    assert response.mimetype == "application/json"
    databaseCredential = DatabaseCredential.query.filter_by(
        app_name="database_credential"
    ).first()
    assert databaseCredential is None


def test_create_database_credential_bad_params_profile(
    flask_app_client, regularUserInstance
):
    data["app_name"] = "da"
    response = flask_app_client.post(
        "/profile/database_credentials",
        content_type="application/x-www-form-urlencoded",
        data=data,
    )
    assert422(response)
    databaseCredential = DatabaseCredential.query.filter_by(
        app_name="database_credential"
    ).first()
    assert databaseCredential is None
