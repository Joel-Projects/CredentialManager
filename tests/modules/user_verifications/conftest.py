import pytest

from app.modules.reddit_apps.models import RedditApp
from app.modules.user_verifications.models import UserVerification


@pytest.fixture()
def regularUserUserVerification(temp_db_instance_helper, regular_user, redditApp):
    for _ in temp_db_instance_helper(
        UserVerification(
            reddit_app=redditApp, owner=regular_user, user_id="123456789012345678"
        )
    ):
        yield _


@pytest.fixture()
def adminUserUserVerification(temp_db_instance_helper, admin_user, redditApp):
    for _ in temp_db_instance_helper(
        UserVerification(
            reddit_app=redditApp, owner=admin_user, user_id="123456789012345679"
        )
    ):
        yield _


@pytest.fixture()
def internalUserUserVerification(temp_db_instance_helper, internal_user, redditApp):
    for _ in temp_db_instance_helper(
        UserVerification(
            reddit_app=redditApp, owner=internal_user, user_id="123456789012345670"
        )
    ):
        yield _


redditAppTestData = {
    "app_description": "app_description",
    "client_id": "client_id",
    "client_secret": "client_secret",
    "user_agent": "user_agent",
    "app_type": "web",
    "redirect_uri": "https://credmgr.jesassn.org/oauth2/reddit_callback",
}


@pytest.fixture()
def redditApp(temp_db_instance_helper, regular_user):
    for _ in temp_db_instance_helper(
        RedditApp(app_name="reddit_app", owner=regular_user, **redditAppTestData)
    ):
        yield _
