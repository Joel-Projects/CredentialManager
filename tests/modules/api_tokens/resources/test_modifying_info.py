import json

import pytest

from app.modules.api_tokens.models import ApiToken
from app.modules.api_tokens.schemas import DetailedApiTokenSchema
from tests.params import labels, users
from tests.utils import assert403, assert409, assert422, assert_success

data = [
    {
        "op": "replace",
        "path": "/name",
        "value": "new_name",
    },
    {
        "op": "replace",
        "path": "/enabled",
        "value": False,
    },
]

tokens = [
    pytest.lazy_fixture("regular_user_api_token"),
    pytest.lazy_fixture("admin_user_api_token"),
    pytest.lazy_fixture("internal_user_api_token"),
]


@pytest.mark.parametrize(
    "token",
    tokens,
    ids=[
        "modify_regular_user_token",
        "modify_admin_user_token",
        "modify_regular_user_token",
    ],
)
@pytest.mark.parametrize("login_as", users, ids=labels)
def test_modifying_api_token(flask_app_client, token, login_as):
    response = flask_app_client.patch(
        f"/api/v1/api_tokens/{token.id}",
        content_type="application/json",
        data=json.dumps(data),
    )

    if token.owner.is_internal:
        if login_as.is_internal:
            assert_success(response, token.owner, ApiToken, DetailedApiTokenSchema)
        else:
            assert403(response, ApiToken, action="patch", internal=True, old_item=token)
    elif login_as.is_admin or login_as.is_internal:
        assert_success(response, token.owner, ApiToken, DetailedApiTokenSchema)
    else:
        assert403(response, ApiToken, action="patch", internal=True, old_item=token)


def test_modifying_api_token_by_self(
    flask_app_client, regular_user_instance, regular_user_api_token
):
    regular_user_api_token.owner = regular_user_instance
    response = flask_app_client.patch(
        f"/api/v1/api_tokens/{regular_user_api_token.id}",
        content_type="application/json",
        data=json.dumps(data),
    )

    assert_success(response, regular_user_instance, ApiToken, DetailedApiTokenSchema)


def test_modifying_api_token_info_with_invalid_format_must_fail(
    flask_app_client, regular_user_instance, regular_user_api_token
):
    regular_user_api_token.owner = regular_user_instance
    response = flask_app_client.patch(
        f"/api/v1/api_tokens/{regular_user_instance.id}",
        content_type="application/json",
        data=json.dumps(
            [
                {
                    "op": "test",
                    "path": "/name",
                    "value": "",
                },
                {
                    "op": "replace",
                    "path": "/enabled",
                },
            ]
        ),
    )
    assert422(
        response,
        ApiToken,
        [("1", {"_schema": ["value is required"]})],
        old_item=regular_user_api_token,
        action="patch",
    )


def test_modifying_api_token_info_with_conflict_data_must_fail(
    flask_app_client,
    regular_user_instance,
    regular_user_api_token,
    admin_user_api_token,
):
    regular_user_api_token.owner = regular_user_instance
    admin_user_api_token.name = "different_name"
    admin_user_api_token.owner = regular_user_instance
    response = flask_app_client.patch(
        f"/api/v1/api_tokens/{regular_user_api_token.id}",
        content_type="application/json",
        data=json.dumps(
            [{"op": "replace", "path": "/name", "value": admin_user_api_token.name}]
        ),
    )

    assert409(
        response,
        ApiToken,
        "Failed to update API Token details.",
        login_as=regular_user_instance,
        message_attrs=[("1", {"_schema": ["value is required"]})],
        old_item=regular_user_api_token,
        action="patch",
    )
