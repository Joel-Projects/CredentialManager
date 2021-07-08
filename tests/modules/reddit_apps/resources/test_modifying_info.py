import json
from datetime import datetime, timezone

import pytest

from app.modules.reddit_apps.models import RedditApp
from app.modules.reddit_apps.schemas import DetailedRedditAppSchema
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
def test_modifying_reddit_app(flask_app_client, regular_user_reddit_app, login_as):
    response = flask_app_client.patch(
        f"/api/v1/reddit_apps/{regular_user_reddit_app.id}",
        content_type="application/json",
        data=json.dumps(data),
    )

    if login_as.is_admin or login_as.is_internal:
        assert_success(
            response, regular_user_reddit_app.owner, RedditApp, DetailedRedditAppSchema
        )
    else:
        assert403(
            response,
            RedditApp,
            action="patch",
            internal=True,
            old_item=regular_user_reddit_app,
        )


def test_modifying_reddit_app_by_self(
    flask_app_client, regular_user_instance, regular_user_reddit_app
):
    regular_user_reddit_app.owner = regular_user_instance
    response = flask_app_client.patch(
        f"/api/v1/reddit_apps/{regular_user_reddit_app.id}",
        content_type="application/json",
        data=json.dumps(data),
    )
    assert_success(response, regular_user_instance, RedditApp, DetailedRedditAppSchema)


def test_modifying_reddit_app_info_with_invalid_format_must_fail(
    flask_app_client, regular_user_instance, regular_user_reddit_app
):
    regular_user_reddit_app.owner = regular_user_instance
    response = flask_app_client.patch(
        f"/api/v1/reddit_apps/{regular_user_instance.id}",
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
        RedditApp,
        [("1", {"_schema": ["value is required"]})],
        old_item=regular_user_reddit_app,
        action="patch",
    )


def test_modifying_reddit_app_info_with_conflict_data_must_fail(
    flask_app_client,
    regular_user_instance,
    regular_user_reddit_app,
    admin_user_reddit_app,
):
    regular_user_reddit_app.owner = regular_user_instance
    admin_user_reddit_app.client_id = "client_id_old"
    admin_user_reddit_app.owner = regular_user_instance
    response = flask_app_client.patch(
        f"/api/v1/reddit_apps/{regular_user_reddit_app.id}",
        content_type="application/json",
        data=json.dumps(
            [
                {
                    "op": "replace",
                    "path": "/client_id",
                    "value": admin_user_reddit_app.client_id,
                }
            ]
        ),
    )

    assert409(
        response,
        RedditApp,
        "Failed to update Reddit App details.",
        login_as=regular_user_instance,
        message_attrs=[("1", {"_schema": ["value is required"]})],
        old_item=regular_user_reddit_app,
        action="patch",
    )
