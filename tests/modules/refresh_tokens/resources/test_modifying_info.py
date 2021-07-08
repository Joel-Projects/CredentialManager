import json

import pytest

from app.modules.refresh_tokens.models import RefreshToken
from app.modules.refresh_tokens.schemas import DetailedRefreshTokenSchema
from tests.params import labels, users
from tests.utils import assert403, assert422, assert_success

data = [
    {
        "op": "replace",
        "path": "/revoked",
        "value": True,
    }
]


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_modifying_refresh_token(
    flask_app_client, regular_user_refresh_token, login_as
):
    response = flask_app_client.patch(
        f"/api/v1/refresh_tokens/{regular_user_refresh_token.id}",
        content_type="application/json",
        data=json.dumps(data),
    )

    if login_as.is_admin or login_as.is_internal:
        assert_success(
            response,
            regular_user_refresh_token.owner,
            RefreshToken,
            DetailedRefreshTokenSchema,
        )
    else:
        assert403(
            response,
            RefreshToken,
            action="patch",
            internal=True,
            old_item=regular_user_refresh_token,
        )


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_modifying_refresh_token_update_token(
    flask_app_client, regular_user_refresh_token, login_as
):
    data = [
        {
            "op": "replace",
            "path": "/refresh_token",
            "value": "new",
        }
    ]
    response = flask_app_client.patch(
        f"/api/v1/refresh_tokens/{regular_user_refresh_token.id}",
        content_type="application/json",
        data=json.dumps(data),
    )
    if login_as.is_admin or login_as.is_internal:
        assert_success(
            response,
            regular_user_refresh_token.owner,
            RefreshToken,
            DetailedRefreshTokenSchema,
        )
    else:
        assert403(
            response,
            RefreshToken,
            action="patch",
            internal=True,
            old_item=regular_user_refresh_token,
        )


def test_modifying_refresh_token_by_self(
    flask_app_client, regular_user_instance, regular_user_refresh_token
):
    regular_user_refresh_token.owner = regular_user_instance
    response = flask_app_client.patch(
        f"/api/v1/refresh_tokens/{regular_user_refresh_token.id}",
        content_type="application/json",
        data=json.dumps(data),
    )

    assert_success(
        response, regular_user_instance, RefreshToken, DetailedRefreshTokenSchema
    )


def test_modifying_refresh_token_info_with_invalid_format_must_fail(
    flask_app_client, regular_user_instance, regular_user_refresh_token
):
    regular_user_refresh_token.owner = regular_user_instance
    response = flask_app_client.patch(
        f"/api/v1/refresh_tokens/{regular_user_instance.id}",
        content_type="application/json",
        data=json.dumps([{"op": "replace", "path": "/revoked"}]),
    )

    assert422(
        response,
        RefreshToken,
        [("0", {"_schema": ["value is required"]})],
        old_item=regular_user_refresh_token,
        action="patch",
    )
