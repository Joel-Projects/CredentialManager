import pytest

from app.modules.users.models import User
from tests.utils import (
    assert_message_flashed,
    assert_rendered_template,
    captured_templates,
)

users = [
    pytest.lazy_fixture("admin_user_deactivated"),
    pytest.lazy_fixture("internal_user_deactivated"),
    pytest.lazy_fixture("regular_user_deactivated"),
]
labels = ["as_admin_user", "as_internal_user", "as_regular_user"]


def test_login_bad_credentials(flask_app_client, regular_user):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            "/login", data={"username": "username", "password": "password"}
        )
        assert response.status_code == 403
        assert_rendered_template(templates, "login.html")
        assert_message_flashed(
            templates, "Please check your login details and try again.", "error"
        )


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_login_deactivated_account(flask_app_client, login_as):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            "/login",
            data={"username": login_as.username, "password": login_as.password_secret},
        )
        assert response.status_code == 403
        assert_rendered_template(templates, "login.html")
        assert_message_flashed(templates, "Your account is disabled.", "error")


def test_login_initial_user_creation(flask_app_client):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get("/login", follow_redirects=True)
        assert response.status_code == 200
        assert_rendered_template(templates, "create_initial_user.html")


def test_login_create_initial_user(flask_app_client):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            "/create_initial_user",
            data={"username": "username", "password": "password"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        user = User.query.first()
        assert user.username == "username"
        assert user.is_internal
        assert_rendered_template(templates, "dash.html")
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get("/logout", follow_redirects=True)
        assert response.status_code == 200
        assert_rendered_template(templates, "login.html")
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            "/login",
            data={"username": "username", "password": "password"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert_rendered_template(templates, "dash.html")


def test_login_ensure_initial_once(flask_app_client, regular_user):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get("/create_initial_user")
        assert response.status_code == 404
        assert_rendered_template(templates, "errors/404.html")
