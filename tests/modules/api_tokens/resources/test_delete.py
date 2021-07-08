import pytest

from app.modules.api_tokens.models import ApiToken
from tests.params import labels, users
from tests.utils import assert403, assert_success

path = "/api/v1/api_tokens"


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_deleting_api_token(flask_app_client, login_as, regular_user_api_token):
    response = flask_app_client.delete(f"{path}/{regular_user_api_token.id}")

    if login_as.is_admin or login_as.is_internal:
        assert_success(
            response, None, ApiToken, None, delete_item_id=regular_user_api_token.id
        )
    else:
        assert403(
            response,
            ApiToken,
            old_item=regular_user_api_token,
            internal=True,
            action="deleted",
        )


def test_deleting_self(
    flask_app_client, db, regular_user_instance, regular_user_api_token
):
    regular_user_api_token.owner = regular_user_instance
    db.session.merge(regular_user_api_token)
    response = flask_app_client.delete(f"{path}/{regular_user_api_token.id}")
    assert_success(
        response, None, ApiToken, None, delete_item_id=regular_user_api_token.id
    )
