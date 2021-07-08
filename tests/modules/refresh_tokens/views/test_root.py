import pytest

from tests.params import labels, users
from tests.response_statuses import assert200
from tests.utils import assert_rendered_template, captured_templates


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_root(flask_app_client, login_as):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get("/refresh_tokens")
        assert200(response)
        assert_rendered_template(templates, "refresh_tokens.html")


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_root_profile(flask_app_client, login_as):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get("/profile/refresh_tokens")
        assert200(response)
        assert_rendered_template(templates, "refresh_tokens.html")


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_root_user_page(flask_app_client, login_as, regular_user):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get(f"/u/{regular_user}/refresh_tokens")
        assert200(response)
        assert_rendered_template(templates, "refresh_tokens.html")


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_root_show_all(flask_app_client, login_as, regular_user):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get(
            f"/u/{regular_user}/refresh_tokens?show_old=true"
        )
        assert200(response)
        assert_rendered_template(templates, "refresh_tokens.html")
