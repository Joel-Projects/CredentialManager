import pytest

from app.modules.reddit_apps.models import RedditApp
from tests.params import labels, users
from tests.utils import assert403, assertSuccess

redditAppsToDelete = [
    pytest.lazy_fixture("adminUserRedditApp"),
    pytest.lazy_fixture("internalUserRedditApp"),
    pytest.lazy_fixture("regularUserRedditApp"),
]


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_deleting_user(flask_app_client, loginAs, regularUserRedditApp):
    response = flask_app_client.delete(f"/api/v1/reddit_apps/{regularUserRedditApp.id}")

    if loginAs.is_admin or loginAs.is_internal:
        assertSuccess(
            response, None, RedditApp, None, deleteItemId=regularUserRedditApp.id
        )
    else:
        assert403(
            response,
            RedditApp,
            oldItem=regularUserRedditApp,
            internal=True,
            action="deleted",
        )


def test_deleting_self(flask_app_client, adminUserInstance, regularUserRedditApp):
    response = flask_app_client.delete(f"/api/v1/reddit_apps/{regularUserRedditApp.id}")
    assertSuccess(response, None, RedditApp, None, deleteItemId=regularUserRedditApp.id)
