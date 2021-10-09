import pytest

from app.modules.reddit_apps.models import RedditApp
from tests.params import labels, users
from tests.utils import assert403, assert_success

reddit_apps_to_delete = [
    pytest.lazy_fixture("admin_user_reddit_app"),
    pytest.lazy_fixture("internal_user_reddit_app"),
    pytest.lazy_fixture("regular_user_reddit_app"),
]


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_deleting_user(flask_app_client, login_as, regular_user_reddit_app):
    response = flask_app_client.delete(f"/api/v1/reddit_apps/{regular_user_reddit_app.id}")

    if login_as.is_admin or login_as.is_internal:
        assert_success(response, None, RedditApp, None, delete_item_id=regular_user_reddit_app.id)
    else:
        assert403(
            response,
            RedditApp,
            old_item=regular_user_reddit_app,
            internal=True,
            action="deleted",
        )


def test_deleting_self(flask_app_client, admin_user_instance, regular_user_reddit_app):
    response = flask_app_client.delete(f"/api/v1/reddit_apps/{regular_user_reddit_app.id}")
    assert_success(response, None, RedditApp, None, delete_item_id=regular_user_reddit_app.id)
