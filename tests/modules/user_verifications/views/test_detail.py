import pytest

from tests.params import labels, users
from tests.response_statuses import assert200, assert403, assert404
from tests.utils import assert_rendered_template, captured_templates, change_owner


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_user_verification_detail(flask_app_client, login_as, regular_user_user_verification):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get(f"/user_verifications/{regular_user_user_verification.id}")
        if login_as.is_admin or login_as.is_internal:
            assert200(response)
            assert_rendered_template(templates, "edit_user_verification.html")
        else:
            assert403(response, templates)


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_user_verification_detail_self(flask_app_client, db, login_as, regular_user_user_verification):
    change_owner(db, login_as, regular_user_user_verification)
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get(f"/profile/user_verifications")
        assert200(response)
        assert_rendered_template(templates, "user_verifications.html")


def test_non_existent_user_verification_detail(flask_app_client, regular_user):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get(f"/user_verifications/1")
        assert404(response, templates)
