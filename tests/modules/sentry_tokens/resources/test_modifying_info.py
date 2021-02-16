import json
import pytest

from app.modules.sentry_tokens.models import SentryToken
from app.modules.sentry_tokens.schemas import DetailedSentryTokenSchema
from tests.params import labels, users
from tests.utils import assert403, assert409, assert422, assertSuccess


data = [
    {
        "op": "replace",
        "path": "/app_name",
        "value": "newName",
    },
    {
        "op": "replace",
        "path": "/enabled",
        "value": False,
    },
]


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_modifying_sentry_token(flask_app_client, regularUserSentryToken, loginAs):
    response = flask_app_client.patch(
        f"/api/v1/sentry_tokens/{regularUserSentryToken.id}",
        content_type="application/json",
        data=json.dumps(data),
    )

    if loginAs.is_admin or loginAs.is_internal:
        assertSuccess(
            response,
            regularUserSentryToken.owner,
            SentryToken,
            DetailedSentryTokenSchema,
        )
    else:
        assert403(
            response,
            SentryToken,
            action="patch",
            internal=True,
            oldItem=regularUserSentryToken,
        )


def test_modifying_sentry_token_by_self(
    flask_app_client, regularUserInstance, regularUserSentryToken
):
    regularUserSentryToken.owner = regularUserInstance
    response = flask_app_client.patch(
        f"/api/v1/sentry_tokens/{regularUserSentryToken.id}",
        content_type="application/json",
        data=json.dumps(data),
    )

    assertSuccess(
        response, regularUserSentryToken.owner, SentryToken, DetailedSentryTokenSchema
    )


def test_modifying_sentry_token_info_with_invalid_format_must_fail(
    flask_app_client, regularUserInstance, regularUserSentryToken
):
    regularUserSentryToken.owner = regularUserInstance
    response = flask_app_client.patch(
        f"/api/v1/sentry_tokens/{regularUserInstance.id}",
        content_type="application/json",
        data=json.dumps(
            [
                {
                    "op": "test",
                    "path": "/app_name",
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
        SentryToken,
        [("1", {"_schema": ["value is required"]})],
        oldItem=regularUserSentryToken,
        action="patch",
    )


def test_modifying_sentry_token_info_with_conflict_data_must_fail(
    flask_app_client, regularUserInstance, regularUserSentryToken, adminUserSentryToken
):
    regularUserSentryToken.owner = regularUserInstance
    adminUserSentryToken.app_name = "differentName"
    adminUserSentryToken.owner = regularUserInstance
    response = flask_app_client.patch(
        f"/api/v1/sentry_tokens/{regularUserSentryToken.id}",
        content_type="application/json",
        data=json.dumps(
            [
                {
                    "op": "replace",
                    "path": "/app_name",
                    "value": adminUserSentryToken.app_name,
                }
            ]
        ),
    )

    assert409(
        response,
        SentryToken,
        "Failed to update Sentry Token details.",
        loginAs=regularUserInstance,
        messageAttrs=[("1", {"_schema": ["value is required"]})],
        oldItem=regularUserSentryToken,
        action="patch",
    )
