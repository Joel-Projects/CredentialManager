import pytest

from app.modules.users.models import User
from app.modules.users.schemas import DetailedUserSchema
from tests.params import labels, users
from tests.utils import assert401, assert403, assert_success


@pytest.mark.parametrize("login_as", users, ids=labels)
@pytest.mark.parametrize(
    "user_to_get",
    [
        pytest.lazy_fixture("admin_user"),
        pytest.lazy_fixture("internal_user"),
        pytest.lazy_fixture("regular_user"),
    ],
    ids=["get_admin_user", "get_internal_user", "get_regular_user"],
)
def test_getting_user(flask_app_client, login_as, user_to_get):
    response = flask_app_client.post(
        f"/api/v1/users/by_name", data={"username": user_to_get.username}
    )

    if user_to_get.is_internal:
        if login_as.is_internal:
            assert_success(response, None, User, DetailedUserSchema)
        elif login_as.is_admin:
            assert403(response, User, internal=True)
        else:
            assert403(response, User, internal=True)
    elif login_as.is_admin or login_as.is_internal:
        assert_success(response, None, User, DetailedUserSchema)
    else:
        assert403(response, User, internal=True)


@pytest.mark.parametrize(
    "login_as",
    [
        pytest.lazy_fixture("admin_user_instance_deactivated"),
        pytest.lazy_fixture("internal_user_instance_deactivated"),
        pytest.lazy_fixture("regular_user_instance_deactivated"),
    ],
    ids=[
        "as_deactivated_admin_user",
        "as_deactivated_internal_user",
        "as_deactivated_regular_user",
    ],
)
@pytest.mark.parametrize(
    "user_to_get",
    [
        pytest.lazy_fixture("internal_user"),
        pytest.lazy_fixture("admin_user"),
        pytest.lazy_fixture("regular_user"),
    ],
    ids=["get_admin_user", "get_internal_user", "get_regular_user"],
)
def test_getting_user_deactivated(flask_app_client, login_as, user_to_get):
    with flask_app_client.login(login_as):
        response = flask_app_client.get(f"/api/v1/users/{user_to_get.id}")
    assert401(response, User, login_as=login_as, action="None")


def test_getting_list_of_users_by_unauthorized_user_must_fail(
    flask_app_client, regular_user_instance
):
    response = flask_app_client.get("/api/v1/users/")
    assert403(response, User, login_as=regular_user_instance, internal=True)


def test_getting_list_of_users_by_authorized_user(
    flask_app_client, admin_user_instance
):
    response = flask_app_client.get("/api/v1/users/")

    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert isinstance(response.json, list)
    assert set(response.json[0].keys()) >= {"id", "username"}


def test_getting_user_me_info(flask_app_client, regular_user_instance):
    response = flask_app_client.get("/api/v1/users/me")

    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {"id", "username"}
    assert "password" not in response.json.keys()


def test_getting_user_apps(flask_app_client, regular_user_instance):
    response = flask_app_client.get(f"/api/v1/users/{regular_user_instance.id}/apps")

    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {
        "id",
        "username",
        "reddit_apps",
        "sentry_tokens",
        "database_credentials",
    }
    assert isinstance(response.json["reddit_apps"], list)
    assert isinstance(response.json["sentry_tokens"], list)
    assert isinstance(response.json["database_credentials"], list)
