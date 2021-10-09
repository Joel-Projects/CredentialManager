import pytest

from app.modules.database_credentials.models import DatabaseCredential
from tests.params import labels, users
from tests.response_statuses import assert201, assert403Create, assert422
from tests.utils import assert_created, assert_rendered_template, captured_templates

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


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_create_database_credential(flask_app_client, login_as):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            "/database_credentials",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        assert201(response)
        assert_rendered_template(templates, "database_credentials.html")
        database_credential = DatabaseCredential.query.filter_by(app_name="database_credential").first()
        assert_created(database_credential, data)


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_create_database_credential_profile(flask_app_client, login_as):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            f"/profile/database_credentials",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        assert201(response)
        assert_rendered_template(templates, "database_credentials.html")
        database_credential = DatabaseCredential.query.filter_by(app_name="database_credential").first()
        assert database_credential is not None
        assert database_credential.id == 1


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_create_database_credential_other_user(flask_app_client, login_as, regular_user):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            "/database_credentials",
            content_type="application/x-www-form-urlencoded",
            data={"owner": regular_user.id, **data},
        )
        if login_as.is_admin or login_as.is_internal:
            assert201(response)
            assert_rendered_template(templates, "database_credentials.html")
            database_credential = DatabaseCredential.query.filter_by(app_name="database_credential").first()
            assert database_credential is not None
            assert database_credential.id == 1
            assert database_credential.owner == regular_user
        else:
            assert403Create(response)
            database_credential = DatabaseCredential.query.filter_by(app_name="database_credential").first()
            assert database_credential is None


def test_create_database_credential_bad_params(flask_app_client, regular_user_instance):
    data["app_name"] = "da"
    response = flask_app_client.post(
        "/database_credentials",
        content_type="application/x-www-form-urlencoded",
        data=data,
    )
    assert response.status_code == 200
    assert response.mimetype == "application/json"
    database_credential = DatabaseCredential.query.filter_by(app_name="database_credential").first()
    assert database_credential is None


def test_create_database_credential_bad_params_profile(flask_app_client, regular_user_instance):
    data["app_name"] = "da"
    response = flask_app_client.post(
        "/profile/database_credentials",
        content_type="application/x-www-form-urlencoded",
        data=data,
    )
    assert422(response)
    database_credential = DatabaseCredential.query.filter_by(app_name="database_credential").first()
    assert database_credential is None
