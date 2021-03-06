import pytest

from app.modules.reddit_apps.models import RedditApp
from app.modules.user_verifications.models import UserVerification


@pytest.fixture()
def regular_user_user_verification(temp_db_instance_helper, regular_user, reddit_app):
    for _ in temp_db_instance_helper(
        UserVerification(reddit_app=reddit_app, owner=regular_user, user_id="123456789012345678")
    ):
        yield _


@pytest.fixture()
def admin_user_user_verification(temp_db_instance_helper, admin_user, reddit_app):
    for _ in temp_db_instance_helper(
        UserVerification(reddit_app=reddit_app, owner=admin_user, user_id="123456789012345679")
    ):
        yield _


@pytest.fixture()
def internal_user_user_verification(temp_db_instance_helper, internal_user, reddit_app):
    for _ in temp_db_instance_helper(
        UserVerification(reddit_app=reddit_app, owner=internal_user, user_id="123456789012345670")
    ):
        yield _


reddit_app_test_data = {
    "app_description": "app_description",
    "client_id": "client_id",
    "client_secret": "client_secret",
    "user_agent": "user_agent",
    "app_type": "web",
    "redirect_uri": "https://credmgr.jesassn.org/oauth2/reddit_callback",
}


@pytest.fixture()
def reddit_app(temp_db_instance_helper, regular_user):
    for _ in temp_db_instance_helper(RedditApp(app_name="reddit_app", owner=regular_user, **reddit_app_test_data)):
        yield _
