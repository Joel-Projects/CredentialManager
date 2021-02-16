import pytest

from app.modules.database_credentials.models import DatabaseCredential
from tests.params import labels, users
from tests.responseStatuses import assert202, assert403
from tests.utils import (
    assertMessageFlashed,
    assertRenderedTemplate,
    captured_templates,
    changeOwner,
)


databaseCredentials = [
    pytest.lazy_fixture("adminUserDatabaseCredential"),
    pytest.lazy_fixture("internalUserDatabaseCredential"),
    pytest.lazy_fixture("regularUserDatabaseCredential"),
]
databaseCredentialLabels = [
    "admin_user_database_credential",
    "internal_user_database_credential",
    "regular_user_database_credential",
]

data = {
    "itemType": "database_credentials",
    "enabled": "",
    "app_name": "newName",
    "database_flavor": "sqlite",
    "database_host": "localhostNew",
    "database_port": 7654,
    "database_username": "postgresNew",
    "database_password": "database_passwordNew",
    "database": "postgresNew",
    "use_ssh": "",
    "ssh_host": "ssh_hostNew",
    "ssh_port": 23,
    "ssh_username": "rootNew",
    "ssh_password": "passNew",
    "use_ssh_key": "",
    "private_key": "private_keyNew",
    "private_key_passphrase": "passphraseNew",
}


@pytest.mark.parametrize("loginAs", users, ids=labels)
@pytest.mark.parametrize(
    "databaseCredential", databaseCredentials, ids=databaseCredentialLabels
)
def test_database_credential_detail_edit_for_other_user(
    flask_app_client, loginAs, databaseCredential
):
    with captured_templates(flask_app_client.application) as templates:
        data["itemId"] = f"{databaseCredential.id}"
        response = flask_app_client.post(
            f"/database_credentials/{databaseCredential.id}",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        if databaseCredential.owner.is_internal and not loginAs.is_internal:
            assert403(response, templates)
            modifiedDatabaseCredential = DatabaseCredential.query.filter_by(
                id=databaseCredential.id
            ).first()
            assert modifiedDatabaseCredential == databaseCredential
        elif loginAs.is_admin or loginAs.is_internal:
            assert202(response)
            assertRenderedTemplate(templates, "edit_database_credential.html")
            assertMessageFlashed(
                templates,
                "Database Credentials 'newName' saved successfully!",
                "success",
            )
            modifiedDatabaseCredential = DatabaseCredential.query.filter_by(
                id=databaseCredential.id
            ).first()
            assert modifiedDatabaseCredential.app_name == "newName"
            assert not modifiedDatabaseCredential.enabled
            assert modifiedDatabaseCredential.database_flavor == "sqlite"
            assert modifiedDatabaseCredential.database_host == "localhostNew"
            assert modifiedDatabaseCredential.database_port == 7654
            assert modifiedDatabaseCredential.database_username == "postgresNew"
            assert (
                modifiedDatabaseCredential.database_password == "database_passwordNew"
            )
            assert modifiedDatabaseCredential.database == "postgresNew"
            assert not modifiedDatabaseCredential.use_ssh
            assert modifiedDatabaseCredential.ssh_host == "ssh_hostNew"
            assert modifiedDatabaseCredential.ssh_port == 23
            assert modifiedDatabaseCredential.ssh_username == "rootNew"
            assert modifiedDatabaseCredential.ssh_password == "passNew"
            assert not modifiedDatabaseCredential.use_ssh_key
            assert modifiedDatabaseCredential.private_key == "private_keyNew"
            assert modifiedDatabaseCredential.private_key_passphrase == "passphraseNew"
        else:
            assert403(response, templates)
            modifiedDatabaseCredential = DatabaseCredential.query.filter_by(
                id=databaseCredential.id
            ).first()
            assert modifiedDatabaseCredential == databaseCredential


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_database_credential_detail_edit(
    flask_app_client, loginAs, regularUserDatabaseCredential
):
    data["itemId"] = f"{regularUserDatabaseCredential.id}"
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            f"/database_credentials/{regularUserDatabaseCredential.id}",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        if loginAs.is_admin or loginAs.is_internal:
            assert202(response)
            assertRenderedTemplate(templates, "edit_database_credential.html")
            assertMessageFlashed(
                templates,
                "Database Credentials 'newName' saved successfully!",
                "success",
            )
            modifiedDatabaseCredential = DatabaseCredential.query.filter_by(
                id=regularUserDatabaseCredential.id
            ).first()
            assert modifiedDatabaseCredential == regularUserDatabaseCredential
        else:
            assert403(response, templates)
            modifiedDatabaseCredential = DatabaseCredential.query.filter_by(
                id=regularUserDatabaseCredential.id
            ).first()
            assert modifiedDatabaseCredential == regularUserDatabaseCredential


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_database_credential_detail_edit_self(
    flask_app_client, db, loginAs, regularUserDatabaseCredential
):
    data["itemId"] = f"{regularUserDatabaseCredential.id}"
    regularUserDatabaseCredential = changeOwner(
        db, loginAs, regularUserDatabaseCredential
    )
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            f"/database_credentials/{regularUserDatabaseCredential.id}", data=data
        )
        assert202(response)
        assertRenderedTemplate(templates, "edit_database_credential.html")
        assertMessageFlashed(
            templates, "Database Credentials 'newName' saved successfully!", "success"
        )
        modifiedDatabaseCredential = DatabaseCredential.query.filter_by(
            id=regularUserDatabaseCredential.id
        ).first()
        assert modifiedDatabaseCredential.app_name == "newName"
        assert not modifiedDatabaseCredential.enabled
        assert modifiedDatabaseCredential.database_flavor == "sqlite"
        assert modifiedDatabaseCredential.database_host == "localhostNew"
        assert modifiedDatabaseCredential.database_port == 7654
        assert modifiedDatabaseCredential.database_username == "postgresNew"
        assert modifiedDatabaseCredential.database_password == "database_passwordNew"
        assert modifiedDatabaseCredential.database == "postgresNew"
        assert not modifiedDatabaseCredential.use_ssh
        assert modifiedDatabaseCredential.ssh_host == "ssh_hostNew"
        assert modifiedDatabaseCredential.ssh_port == 23
        assert modifiedDatabaseCredential.ssh_username == "rootNew"
        assert modifiedDatabaseCredential.ssh_password == "passNew"
        assert not modifiedDatabaseCredential.use_ssh_key
        assert modifiedDatabaseCredential.private_key == "private_keyNew"
        assert modifiedDatabaseCredential.private_key_passphrase == "passphraseNew"


def test_database_credential_detail_conflicting_app_name(
    flask_app_client,
    db,
    regularUserInstance,
    regularUserDatabaseCredential,
    adminUserDatabaseCredential,
):
    original = changeOwner(db, regularUserInstance, adminUserDatabaseCredential)
    original.app_name = "original"
    toBeModified = changeOwner(db, regularUserInstance, regularUserDatabaseCredential)
    db.session.merge(original)
    data["itemId"] = f"{regularUserDatabaseCredential.id}"
    data["app_name"] = "original"
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            f"/database_credentials/{toBeModified.id}", json=data
        )
        assert response.status_code == 422
        assert response.mimetype == "text/html"
        assertRenderedTemplate(templates, "edit_database_credential.html")
        assert (
            templates["templates"][0][1]["form"].errors["app_name"][0]
            == "Already exists."
        )
        modifiedDatabaseCredential = DatabaseCredential.query.filter_by(
            id=toBeModified.id
        ).first()
        assert modifiedDatabaseCredential.app_name == toBeModified.app_name
