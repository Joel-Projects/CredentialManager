import pytest

from tests.params import labels, users
from tests.response_statuses import assert200, assert403
from tests.utils import assert_rendered_template, captured_templates


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_user_detail(flask_app_client, login_as, regular_user):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get(f"/u/{regular_user.username}")
        if login_as.is_admin or login_as.is_internal:
            assert200(response)
            assert_rendered_template(templates, "edit_user.html")
        else:
            assert403(response, templates)


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_user_detail_self(flask_app_client, login_as):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get(f"/profile", follow_redirects=True)
        assert200(response)
        assert_rendered_template(templates, "edit_user.html")
