import json
import pytest

from app.modules.api_tokens.models import ApiToken
from app.modules.api_tokens.schemas import DetailedApiTokenSchema
from tests.params import labels, users
from tests.utils import assert403, assert409, assert422, assertSuccess


data = [
    {
        "op": "replace",
        "path": "/name",
        "value": "newName",
    },
    {
        "op": "replace",
        "path": "/enabled",
        "value": False,
    },
]

tokens = [
    pytest.lazy_fixture("regularUserApiToken"),
    pytest.lazy_fixture("adminUserApiToken"),
    pytest.lazy_fixture("internalUserApiToken"),
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
@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_modifying_api_token(flask_app_client, token, loginAs):
    response = flask_app_client.patch(
        f"/api/v1/api_tokens/{token.id}",
        content_type="application/json",
        data=json.dumps(data),
    )

    if token.owner.is_internal:
        if loginAs.is_internal:
            assertSuccess(response, token.owner, ApiToken, DetailedApiTokenSchema)
        else:
            assert403(response, ApiToken, action="patch", internal=True, oldItem=token)
    elif loginAs.is_admin or loginAs.is_internal:
        assertSuccess(response, token.owner, ApiToken, DetailedApiTokenSchema)
    else:
        assert403(response, ApiToken, action="patch", internal=True, oldItem=token)


def test_modifying_api_token_by_self(
    flask_app_client, regularUserInstance, regularUserApiToken
):
    regularUserApiToken.owner = regularUserInstance
    response = flask_app_client.patch(
        f"/api/v1/api_tokens/{regularUserApiToken.id}",
        content_type="application/json",
        data=json.dumps(data),
    )

    assertSuccess(response, regularUserInstance, ApiToken, DetailedApiTokenSchema)


def test_modifying_api_token_info_with_invalid_format_must_fail(
    flask_app_client, regularUserInstance, regularUserApiToken
):
    regularUserApiToken.owner = regularUserInstance
    response = flask_app_client.patch(
        f"/api/v1/api_tokens/{regularUserInstance.id}",
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
        oldItem=regularUserApiToken,
        action="patch",
    )


def test_modifying_api_token_info_with_conflict_data_must_fail(
    flask_app_client, regularUserInstance, regularUserApiToken, adminUserApiToken
):
    regularUserApiToken.owner = regularUserInstance
    adminUserApiToken.name = "differentName"
    adminUserApiToken.owner = regularUserInstance
    response = flask_app_client.patch(
        f"/api/v1/api_tokens/{regularUserApiToken.id}",
        content_type="application/json",
        data=json.dumps(
            [{"op": "replace", "path": "/name", "value": adminUserApiToken.name}]
        ),
    )

    assert409(
        response,
        ApiToken,
        "Failed to update API Token details.",
        loginAs=regularUserInstance,
        messageAttrs=[("1", {"_schema": ["value is required"]})],
        oldItem=regularUserApiToken,
        action="patch",
    )
