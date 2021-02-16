import pytest

from app.modules.reddit_apps.models import RedditApp
from app.modules.refresh_tokens.models import RefreshToken
from app.modules.user_verifications.models import UserVerification


test_data = {
    "app_description": "app_description",
    "client_id": "client_id",
    "client_secret": "client_secret",
    "user_agent": "user_agent",
    "app_type": "web",
    "redirect_uri": "https://credmgr.jesassn.org/oauth2/reddit_callback",
}


@pytest.fixture()
def regularUserRedditApp(temp_db_instance_helper, regular_user):
    for _ in temp_db_instance_helper(
        RedditApp(app_name="regular_user_reddit_app", owner=regular_user, **test_data)
    ):
        yield _


@pytest.fixture()
def adminUserRedditApp(temp_db_instance_helper, admin_user):
    for _ in temp_db_instance_helper(
        RedditApp(app_name="admin_user_reddit_app", owner=admin_user, **test_data)
    ):
        yield _


@pytest.fixture()
def internalUserRedditApp(temp_db_instance_helper, internal_user):
    for _ in temp_db_instance_helper(
        RedditApp(app_name="internal_user_reddit_app", owner=internal_user, **test_data)
    ):
        yield _


refreshTokenData = {
    "redditor": "redditor",
    "refresh_token": "refresh_token",
    "scopes": [
        "edit",
        "vote",
        "modwiki",
        "modflair",
        "creddits",
        "modconfig",
        "history",
        "modtraffic",
        "modmail",
        "modposts",
        "read",
        "identity",
        "report",
        "privatemessages",
        "modothers",
        "modlog",
        "structuredstyles",
        "wikiedit",
        "subscribe",
        "modself",
        "save",
        "submit",
        "flair",
        "wikiread",
        "account",
        "mysubreddits",
        "livemanage",
        "modcontributors",
    ],
}


@pytest.fixture()
def regularUserRefreshToken(
    regularUserRedditApp, temp_db_instance_helper, regular_user
):
    for _ in temp_db_instance_helper(
        RefreshToken(
            reddit_app=regularUserRedditApp, owner=regular_user, **refreshTokenData
        )
    ):
        yield _


@pytest.fixture()
def regularUserUserVerification(
    temp_db_instance_helper, regular_user, regularUserRedditApp
):
    for _ in temp_db_instance_helper(
        UserVerification(
            reddit_app=regularUserRedditApp,
            owner=regular_user,
            user_id="123456789012345678",
        )
    ):
        yield _
