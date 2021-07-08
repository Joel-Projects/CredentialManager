import pytest

from app.modules.users.models import User
from tests.params import labels, users
from tests.utils import assert401, assert403, assert409, assert_success

users_to_delete = [
    pytest.lazy_fixture("admin_user"),
    pytest.lazy_fixture("internal_user"),
    pytest.lazy_fixture("regular_user"),
]


@pytest.mark.parametrize("login_as", users, ids=labels)
@pytest.mark.parametrize(
    "user_to_delete",
    users_to_delete,
    ids=["delete_admin_user", "delete_internal_user", "delete_regular_user"],
)
def test_deleting_user(flask_app_client, login_as, user_to_delete):
    response = flask_app_client.delete(f"/api/v1/users/{user_to_delete.id}")

    if user_to_delete.is_internal:
        if login_as.is_internal:
            assert_success(response, None, User, None, delete_item_id=user_to_delete.id)
        else:
            assert403(
                response, User, old_item=user_to_delete, internal=True, action="deleted"
            )
    elif login_as.is_admin or login_as.is_internal:
        assert_success(response, None, User, None, delete_item_id=user_to_delete.id)
    else:
        assert403(
            response, User, old_item=user_to_delete, internal=True, action="deleted"
        )


def test_deleting_self(flask_app_client, admin_user_instance):
    response = flask_app_client.delete(f"/api/v1/users/{admin_user_instance.id}")
    assert409(
        response,
        User,
        message="You can't delete yourself.",
        old_item=admin_user_instance,
        login_as=admin_user_instance,
        action="deleted",
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
@pytest.mark.parametrize(
    "user_to_delete",
    [
        pytest.lazy_fixture("internal_user"),
        pytest.lazy_fixture("admin_user"),
        pytest.lazy_fixture("regular_user"),
    ],
    ids=["delete_admin_user", "delete_internal_user", "delete_regular_user"],
)
def test_deleting_user_deactivated(flask_app_client, login_as, user_to_delete):
    with flask_app_client.login(login_as):
        response = flask_app_client.delete(f"/api/v1/users/{user_to_delete.id}")
    assert401(response, user_to_delete, login_as=login_as)
