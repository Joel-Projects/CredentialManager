import json

import pytest

from app.modules.bots.models import Bot
from app.modules.bots.schemas import DetailedBotSchema
from tests.params import labels, users
from tests.utils import assert403, assert409, assert422, assert_success

data = [
    {
        "op": "replace",
        "path": "/app_name",
        "value": "new_app_name",
    },
    {
        "op": "replace",
        "path": "/enabled",
        "value": False,
    },
]


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_modifying_bot(flask_app_client, regular_user_bot, login_as):
    response = flask_app_client.patch(
        f"/api/v1/bots/{regular_user_bot.id}",
        content_type="application/json",
        data=json.dumps(data),
    )

    if login_as.is_admin or login_as.is_internal:
        assert_success(response, regular_user_bot.owner, Bot, DetailedBotSchema)
    else:
        assert403(response, Bot, action="patch", internal=True, old_item=regular_user_bot)


def test_modifying_bot_by_self(flask_app_client, regular_user_instance, regular_user_bot):
    regular_user_bot.owner = regular_user_instance
    response = flask_app_client.patch(
        f"/api/v1/bots/{regular_user_bot.id}",
        content_type="application/json",
        data=json.dumps(data),
    )
    assert_success(response, regular_user_instance, Bot, DetailedBotSchema)


def test_modifying_bot_info_with_invalid_format_must_fail(flask_app_client, regular_user_instance, regular_user_bot):
    regular_user_bot.owner = regular_user_instance
    response = flask_app_client.patch(
        f"/api/v1/bots/{regular_user_bot.id}",
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
        Bot,
        [("1", {"_schema": ["value is required"]})],
        old_item=regular_user_bot,
        action="patch",
    )


def test_modifying_bot_info_with_conflict_data_must_fail(
    flask_app_client, regular_user_instance, regular_user_bot, admin_user_bot
):
    regular_user_bot.owner = regular_user_instance
    admin_user_bot.app_name = "app_name_old"
    admin_user_bot.owner = regular_user_instance
    response = flask_app_client.patch(
        f"/api/v1/bots/{regular_user_bot.id}",
        content_type="application/json",
        data=json.dumps([{"op": "replace", "path": "/app_name", "value": admin_user_bot.app_name}]),
    )

    assert409(
        response,
        Bot,
        "Failed to update Bot details.",
        login_as=regular_user_instance,
        message_attrs=[("1", {"_schema": ["value is required"]})],
        old_item=regular_user_bot,
        action="patch",
    )
