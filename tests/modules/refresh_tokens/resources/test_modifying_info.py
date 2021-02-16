import json

import pytest

from app.modules.refresh_tokens.models import RefreshToken
from app.modules.refresh_tokens.schemas import DetailedRefreshTokenSchema
from tests.params import labels, users
from tests.utils import assert403, assert422, assertSuccess

data = [
    {
        "op": "replace",
        "path": "/revoked",
        "value": True,
    }
]


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_modifying_refresh_token(flask_app_client, regularUserRefreshToken, loginAs):
    response = flask_app_client.patch(
        f"/api/v1/refresh_tokens/{regularUserRefreshToken.id}",
        content_type="application/json",
        data=json.dumps(data),
    )

    if loginAs.is_admin or loginAs.is_internal:
        assertSuccess(
            response,
            regularUserRefreshToken.owner,
            RefreshToken,
            DetailedRefreshTokenSchema,
        )
    else:
        assert403(
            response,
            RefreshToken,
            action="patch",
            internal=True,
            oldItem=regularUserRefreshToken,
        )


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_modifying_refresh_token_update_token(flask_app_client, regularUserRefreshToken, loginAs):
    data = [{
        "op": "replace", "path": "/refresh_token", "value": 'new',
    }]
    response = flask_app_client.patch(
        f"/api/v1/refresh_tokens/{regularUserRefreshToken.id}",
        content_type="application/json",
        data=json.dumps(data),
    )

def test_modifying_refresh_token_by_self(
    flask_app_client, regularUserInstance, regularUserRefreshToken
):
    regularUserRefreshToken.owner = regularUserInstance
    response = flask_app_client.patch(
        f"/api/v1/refresh_tokens/{regularUserRefreshToken.id}",
        content_type="application/json",
        data=json.dumps(data),
    )

    assertSuccess(
        response, regularUserInstance, RefreshToken, DetailedRefreshTokenSchema
    )


def test_modifying_refresh_token_info_with_invalid_format_must_fail(
    flask_app_client, regularUserInstance, regularUserRefreshToken
):
    regularUserRefreshToken.owner = regularUserInstance
    response = flask_app_client.patch(
        f"/api/v1/refresh_tokens/{regularUserInstance.id}",
        content_type="application/json",
        data=json.dumps([{"op": "replace", "path": "/revoked"}]),
    )

    assert422(
        response,
        RefreshToken,
        [("0", {"_schema": ["value is required"]})],
        oldItem=regularUserRefreshToken,
        action="patch",
    )
