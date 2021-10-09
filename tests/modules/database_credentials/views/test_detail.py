import pytest

from tests.params import labels, users
from tests.response_statuses import assert200, assert403, assert404
from tests.utils import assert_rendered_template, captured_templates, change_owner


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_database_credential_detail(flask_app_client, login_as, regular_user_database_credential):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get(f"/database_credentials/{regular_user_database_credential.id}")
        if login_as.is_admin or login_as.is_internal:
            assert200(response)
            assert_rendered_template(templates, "edit_database_credential.html")
        else:
            assert403(response, templates)


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_database_credential_detail_self(flask_app_client, db, login_as, regular_user_database_credential):
    change_owner(db, login_as, regular_user_database_credential)
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get(f"/profile/database_credentials")
        assert200(response)
        assert_rendered_template(templates, "database_credentials.html")


def test_non_existant_database_credential_detail(flask_app_client, regular_user):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get(f"/database_credentials/1")
        assert404(response, templates)
