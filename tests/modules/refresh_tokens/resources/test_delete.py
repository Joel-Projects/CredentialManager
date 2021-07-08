import pytest

from app.modules.refresh_tokens.models import RefreshToken
from tests.params import labels, users
from tests.utils import assert403, assert_success


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_deleting_user(flask_app_client, login_as, regular_user_refresh_token):
    response = flask_app_client.delete(
        f"/api/v1/refresh_tokens/{regular_user_refresh_token.id}"
    )

    if login_as.is_admin or login_as.is_internal:
        assert_success(
            response,
            None,
            RefreshToken,
            None,
            delete_item_id=regular_user_refresh_token.id,
        )
    else:
        assert403(
            response,
            RefreshToken,
            old_item=regular_user_refresh_token,
            internal=True,
            action="deleted",
        )


def test_deleting_self(
    flask_app_client, admin_user_instance, regular_user_refresh_token
):
    response = flask_app_client.delete(
        f"/api/v1/refresh_tokens/{regular_user_refresh_token.id}"
    )
    assert_success(
        response, None, RefreshToken, None, delete_item_id=regular_user_refresh_token.id
    )
