import pytest

from app.modules.database_credentials.models import DatabaseCredential
from tests.params import labels, users
from tests.response_statuses import assert202, assert403
from tests.utils import assert_message_flashed, assert_rendered_template, captured_templates, change_owner

database_credentials = [
    pytest.lazy_fixture("admin_user_database_credential"),
    pytest.lazy_fixture("internal_user_database_credential"),
    pytest.lazy_fixture("regular_user_database_credential"),
]
database_credential_labels = [
    "admin_user_database_credential",
    "internal_user_database_credential",
    "regular_user_database_credential",
]

data = {
    "item_type": "database_credentials",
    "enabled": "",
    "app_name": "new_name",
    "database_flavor": "sqlite",
    "database_host": "localhost_new",
    "database_port": 7654,
    "database_username": "postgres_new",
    "database_password": "database_password_new",
    "database": "postgres_new",
    "use_ssh": "",
    "ssh_host": "ssh_host_new",
    "ssh_port": 23,
    "ssh_username": "root_new",
    "ssh_password": "pass_new",
    "use_ssh_key": "",
    "private_key": "private_key_new",
    "private_key_passphrase": "passphrase_new",
}


@pytest.mark.parametrize("login_as", users, ids=labels)
@pytest.mark.parametrize("database_credential", database_credentials, ids=database_credential_labels)
def test_database_credential_detail_edit_for_other_user(flask_app_client, login_as, database_credential):
    with captured_templates(flask_app_client.application) as templates:
        data["item_id"] = f"{database_credential.id}"
        response = flask_app_client.post(
            f"/database_credentials/{database_credential.id}",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        if database_credential.owner.is_internal and not login_as.is_internal:
            assert403(response, templates)
            modified_database_credential = DatabaseCredential.query.filter_by(id=database_credential.id).first()
            assert modified_database_credential == database_credential
        elif login_as.is_admin or login_as.is_internal:
            assert202(response)
            assert_rendered_template(templates, "edit_database_credential.html")
            assert_message_flashed(
                templates,
                "Database Credentials 'new_name' saved successfully!",
                "success",
            )
            modified_database_credential = DatabaseCredential.query.filter_by(id=database_credential.id).first()
            assert modified_database_credential.app_name == "new_name"
            assert not modified_database_credential.enabled
            assert modified_database_credential.database_flavor == "sqlite"
            assert modified_database_credential.database_host == "localhost_new"
            assert modified_database_credential.database_port == 7654
            assert modified_database_credential.database_username == "postgres_new"
            assert modified_database_credential.database_password == "database_password_new"
            assert modified_database_credential.database == "postgres_new"
            assert not modified_database_credential.use_ssh
            assert modified_database_credential.ssh_host == "ssh_host_new"
            assert modified_database_credential.ssh_port == 23
            assert modified_database_credential.ssh_username == "root_new"
            assert modified_database_credential.ssh_password == "pass_new"
            assert not modified_database_credential.use_ssh_key
            assert modified_database_credential.private_key == "private_key_new"
            assert modified_database_credential.private_key_passphrase == "passphrase_new"
        else:
            assert403(response, templates)
            modified_database_credential = DatabaseCredential.query.filter_by(id=database_credential.id).first()
            assert modified_database_credential == database_credential


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_database_credential_detail_edit(flask_app_client, login_as, regular_user_database_credential):
    data["item_id"] = f"{regular_user_database_credential.id}"
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            f"/database_credentials/{regular_user_database_credential.id}",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        if login_as.is_admin or login_as.is_internal:
            assert202(response)
            assert_rendered_template(templates, "edit_database_credential.html")
            assert_message_flashed(
                templates,
                "Database Credentials 'new_name' saved successfully!",
                "success",
            )
            modified_database_credential = DatabaseCredential.query.filter_by(
                id=regular_user_database_credential.id
            ).first()
            assert modified_database_credential == regular_user_database_credential
        else:
            assert403(response, templates)
            modified_database_credential = DatabaseCredential.query.filter_by(
                id=regular_user_database_credential.id
            ).first()
            assert modified_database_credential == regular_user_database_credential


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_database_credential_detail_edit_self(flask_app_client, db, login_as, regular_user_database_credential):
    data["item_id"] = f"{regular_user_database_credential.id}"
    regular_user_database_credential = change_owner(db, login_as, regular_user_database_credential)
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(f"/database_credentials/{regular_user_database_credential.id}", data=data)
        assert202(response)
        assert_rendered_template(templates, "edit_database_credential.html")
        assert_message_flashed(templates, "Database Credentials 'new_name' saved successfully!", "success")
        modified_database_credential = DatabaseCredential.query.filter_by(
            id=regular_user_database_credential.id
        ).first()
        assert modified_database_credential.app_name == "new_name"
        assert not modified_database_credential.enabled
        assert modified_database_credential.database_flavor == "sqlite"
        assert modified_database_credential.database_host == "localhost_new"
        assert modified_database_credential.database_port == 7654
        assert modified_database_credential.database_username == "postgres_new"
        assert modified_database_credential.database_password == "database_password_new"
        assert modified_database_credential.database == "postgres_new"
        assert not modified_database_credential.use_ssh
        assert modified_database_credential.ssh_host == "ssh_host_new"
        assert modified_database_credential.ssh_port == 23
        assert modified_database_credential.ssh_username == "root_new"
        assert modified_database_credential.ssh_password == "pass_new"
        assert not modified_database_credential.use_ssh_key
        assert modified_database_credential.private_key == "private_key_new"
        assert modified_database_credential.private_key_passphrase == "passphrase_new"


def test_database_credential_detail_conflicting_app_name(
    flask_app_client,
    db,
    regular_user_instance,
    regular_user_database_credential,
    admin_user_database_credential,
):
    original = change_owner(db, regular_user_instance, admin_user_database_credential)
    original.app_name = "original"
    to_be_modified = change_owner(db, regular_user_instance, regular_user_database_credential)
    db.session.merge(original)
    data["item_id"] = f"{regular_user_database_credential.id}"
    data["app_name"] = "original"
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(f"/database_credentials/{to_be_modified.id}", json=data)
        assert response.status_code == 422
        assert response.mimetype == "text/html"
        assert_rendered_template(templates, "edit_database_credential.html")
        assert templates["templates"][0][1]["form"].errors["app_name"][0] == "Already exists."
        modified_database_credential = DatabaseCredential.query.filter_by(id=to_be_modified.id).first()
        assert modified_database_credential.app_name == to_be_modified.app_name
