import pytest

from app.modules.reddit_apps.models import RedditApp
from tests.params import labels, users


def test_reddit_app_check_owner(regular_user, admin_user, regular_user_reddit_app):
    reddit_app = RedditApp.query.first()
    assert reddit_app.check_owner(regular_user)
    assert not reddit_app.check_owner(admin_user)
    assert not reddit_app.check_owner(None)


def test_reddit_app_check_state(regular_user_reddit_app):
    reddit_app = RedditApp.query.first()
    import hashlib

    assert hashlib.sha256(reddit_app.client_id.encode()).hexdigest() == reddit_app.state


def test_reddit_app_gen_auth_url(
    regular_user, admin_user, regular_user_reddit_app, regular_user_refresh_token
):
    reddit_app = RedditApp.query.first()
    scopes = ["identity", "read", "privatemessages"]
    auth_url = "https://www.reddit.com/api/v1/authorize?client_id=client_id&duration=permanent&redirect_uri=https%3A%2F%2Fcredmgr.jesassn.org%2Foauth2%2Freddit_callback&response_type=code&scope=identity+read+privatemessages&state=65904271c7f48ee638a684f55f76a92a1c7ecc7a0c56e5c0a1b83e2510efcb4d"
    assert auth_url == reddit_app.gen_auth_url(scopes, "permanent")


def test_reddit_app_get_app_from_state(
    regular_user, admin_user, regular_user_reddit_app, regular_user_refresh_token
):
    reddit_app = RedditApp.query.first()
    app, user_id = RedditApp.get_app_from_state(
        "65904271c7f48ee638a684f55f76a92a1c7ecc7a0c56e5c0a1b83e2510efcb4d"
    )
    assert reddit_app, None == (app, user_id)


def test_reddit_app_get_app_from_state_with_user_id(
    regular_user, admin_user, regular_user_reddit_app, regular_user_refresh_token
):
    reddit_app = RedditApp.query.first()
    import base64

    state = base64.urlsafe_b64encode(
        f"{reddit_app.state}:123456789012345678".encode()
    ).decode()
    user_id = 123456789012345678
    app, user_id = RedditApp.get_app_from_state(state)
    assert (reddit_app, user_id) == (app, user_id)


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_reddit_app_get_refresh_token(
    login_as, regular_user_reddit_app, regular_user_refresh_token
):
    reddit_app = RedditApp.query.first()
    if login_as.is_admin or login_as.is_internal:
        assert regular_user_refresh_token == reddit_app.get_refresh_token("redditor")
    else:
        assert reddit_app.get_refresh_token("redditor") is None


def test_reddit_app_get_refresh_token_self(
    regular_user_instance, regular_user_reddit_app, regular_user_refresh_token
):
    reddit_app = RedditApp.query.first()
    reddit_app.owner = regular_user_refresh_token.owner = regular_user_instance
    assert regular_user_refresh_token == reddit_app.get_refresh_token("redditor")
