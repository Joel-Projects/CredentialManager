import pytest

from app.modules.database_credentials.models import DatabaseCredential
from app.modules.database_credentials.schemas import DetailedDatabaseCredentialSchema
from tests.params import labels, users
from tests.utils import assert403, assert422, assertSuccess

path = "/api/v1/database_credentials/"
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
def test_creating_database_credential(flask_app_client, loginAs, regular_user):
    response = flask_app_client.post(path, data={"owner_id": regular_user.id, **data})

    if loginAs.is_admin or loginAs.is_internal:
        assertSuccess(
            response, regular_user, DatabaseCredential, DetailedDatabaseCredentialSchema
        )
    else:
        assert403(response, DatabaseCredential, action="create")


def test_creating_database_credential_for_self(flask_app_client, regularUserInstance):
    response = flask_app_client.post(path, data=data)

    assertSuccess(
        response,
        regularUserInstance,
        DatabaseCredential,
        DetailedDatabaseCredentialSchema,
    )


def test_creating_database_credential_for_self_with_owner(
    flask_app_client, regularUserInstance
):
    response = flask_app_client.post(
        path, data={"owner_id": regularUserInstance.id, **data}
    )

    assertSuccess(
        response,
        regularUserInstance,
        DatabaseCredential,
        DetailedDatabaseCredentialSchema,
    )


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_creating_database_credential_with_bad_name(flask_app_client, loginAs):
    response = flask_app_client.post(path, data={**data, "app_name": "to"})

    assert422(
        response,
        DatabaseCredential,
        messageAttrs=[("app_name", ["Name must be greater than 3 characters long."])],
    )
