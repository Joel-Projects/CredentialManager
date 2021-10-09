import json

import pytest

from app.modules.sentry_tokens.models import SentryToken
from app.modules.sentry_tokens.schemas import DetailedSentryTokenSchema
from tests.params import labels, users
from tests.utils import assert403, assert409, assert422, assert_success

data = [
    {
        "op": "replace",
        "path": "/app_name",
        "value": "new_name",
    },
    {
        "op": "replace",
        "path": "/enabled",
        "value": False,
    },
]


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_modifying_sentry_token(flask_app_client, regular_user_sentry_token, login_as):
    response = flask_app_client.patch(
        f"/api/v1/sentry_tokens/{regular_user_sentry_token.id}",
        content_type="application/json",
        data=json.dumps(data),
    )

    if login_as.is_admin or login_as.is_internal:
        assert_success(
            response,
            regular_user_sentry_token.owner,
            SentryToken,
            DetailedSentryTokenSchema,
        )
    else:
        assert403(
            response,
            SentryToken,
            action="patch",
            internal=True,
            old_item=regular_user_sentry_token,
        )


def test_modifying_sentry_token_by_self(flask_app_client, regular_user_instance, regular_user_sentry_token):
    regular_user_sentry_token.owner = regular_user_instance
    response = flask_app_client.patch(
        f"/api/v1/sentry_tokens/{regular_user_sentry_token.id}",
        content_type="application/json",
        data=json.dumps(data),
    )

    assert_success(
        response,
        regular_user_sentry_token.owner,
        SentryToken,
        DetailedSentryTokenSchema,
    )


def test_modifying_sentry_token_info_with_invalid_format_must_fail(
    flask_app_client, regular_user_instance, regular_user_sentry_token
):
    regular_user_sentry_token.owner = regular_user_instance
    response = flask_app_client.patch(
        f"/api/v1/sentry_tokens/{regular_user_instance.id}",
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
        old_item=regular_user_sentry_token,
        action="patch",
    )


def test_modifying_sentry_token_info_with_conflict_data_must_fail(
    flask_app_client,
    regular_user_instance,
    regular_user_sentry_token,
    admin_user_sentry_token,
):
    regular_user_sentry_token.owner = regular_user_instance
    admin_user_sentry_token.app_name = "different_name"
    admin_user_sentry_token.owner = regular_user_instance
    response = flask_app_client.patch(
        f"/api/v1/sentry_tokens/{regular_user_sentry_token.id}",
        content_type="application/json",
        data=json.dumps(
            [
                {
                    "op": "replace",
                    "path": "/app_name",
                    "value": admin_user_sentry_token.app_name,
                }
            ]
        ),
    )

    assert409(
        response,
        SentryToken,
        "Failed to update Sentry Token details.",
        login_as=regular_user_instance,
        message_attrs=[("1", {"_schema": ["value is required"]})],
        old_item=regular_user_sentry_token,
        action="patch",
    )
