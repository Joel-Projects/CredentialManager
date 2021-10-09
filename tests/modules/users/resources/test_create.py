import pytest

from app.modules.users.models import User
from app.modules.users.schemas import DetailedUserSchema
from tests.params import labels, users
from tests.utils import assert401, assert403, assert409, assert_success


# noinspection PyUnresolvedReferences
@pytest.mark.parametrize(
    "is_internal,is_admin,is_regular_user",
    [(True, False, False), (False, True, True), (False, False, True)],
    ids=["create_internal_user", "create_admin_user", "create_regular_user"],
)
@pytest.mark.parametrize("login_as", users, ids=labels)
def test_creating_user(flask_app_client, is_internal, is_admin, is_regular_user, login_as: User):
    response = flask_app_client.post(
        "/api/v1/users/",
        data={
            "username": "test_username",
            "password": "test_password",
            "is_internal": is_internal,
            "is_admin": is_admin,
            "is_regular_user": is_regular_user,
            "is_active": True,
        },
    )

    if is_internal:
        if login_as.is_internal:
            assert_success(response, None, User, DetailedUserSchema)
        else:
            assert403(response, User, login_as=login_as, internal=True)
    elif login_as.is_admin or login_as.is_internal:
        assert_success(response, None, User, DetailedUserSchema)
    else:
        assert403(response, User, login_as=login_as, internal=True)


@pytest.mark.parametrize(
    "is_internal,is_admin,is_regular_user",
    [(True, False, False), (False, True, True), (False, False, True)],
    ids=["internal_user", "admin_user", "regular_user"],
)
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
def test_creating_user_as_deactivated(flask_app_client, is_internal, is_admin, is_regular_user, login_as: User):
    with flask_app_client.login(login_as):
        response = flask_app_client.post(
            "/api/v1/users/",
            data={
                "username": "test_username",
                "password": "test_password",
                "is_internal": is_internal,
                "is_admin": is_admin,
                "is_regular_user": is_regular_user,
                "is_active": True,
            },
        )
    assert401(response, User, login_as=login_as)


def test_creating_conflict_user(flask_app_client, admin_user):
    with flask_app_client.login(admin_user):
        response = flask_app_client.post(
            "/api/v1/users/",
            data={"username": "admin_user", "password": "test_password"},
        )
        assert409(response, User, "Failed to create a new user.", login_as=admin_user)
