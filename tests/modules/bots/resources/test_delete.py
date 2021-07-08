import pytest

from app.modules.bots.models import Bot
from tests.params import labels, users
from tests.utils import assert403, assert_success

bots_to_delete = [
    pytest.lazy_fixture("admin_user_bot"),
    pytest.lazy_fixture("internal_user_bot"),
    pytest.lazy_fixture("regular_user_bot"),
]


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_deleting_user(flask_app_client, login_as, regular_user_bot):
    response = flask_app_client.delete(f"/api/v1/bots/{regular_user_bot.id}")

    if login_as.is_admin or login_as.is_internal:
        assert_success(response, None, Bot, None, delete_item_id=regular_user_bot.id)
    else:
        assert403(
            response, Bot, old_item=regular_user_bot, internal=True, action="deleted"
        )


def test_deleting_self(flask_app_client, admin_user_instance, regular_user_bot):
    response = flask_app_client.delete(f"/api/v1/bots/{regular_user_bot.id}")
    assert_success(response, None, Bot, None, delete_item_id=regular_user_bot.id)
