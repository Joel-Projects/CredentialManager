import pytest

from app.modules.reddit_apps.models import RedditApp
from tests.params import labels, users


def test_reddit_app_check_owner(regular_user, admin_user, regularUserRedditApp):
    redditApp = RedditApp.query.first()
    assert redditApp.check_owner(regular_user)
    assert not redditApp.check_owner(admin_user)
    assert not redditApp.check_owner(None)

def test_reddit_app_check_state(regularUserRedditApp):
    redditApp = RedditApp.query.first()
    import hashlib
    assert hashlib.sha256(redditApp.client_id.encode()).hexdigest() == redditApp.state

def test_reddit_app_genAuthUrl(regular_user, admin_user, regularUserRedditApp, regularUserRefreshToken):
    redditApp = RedditApp.query.first()
    scopes = ['identity', 'read', 'privatemessages']
    authUrl = 'https://www.reddit.com/api/v1/authorize?client_id=client_id&duration=permanent&redirect_uri=https%3A%2F%2Fcredmgr.jesassn.org%2Foauth2%2Freddit_callback&response_type=code&scope=identity+read+privatemessages&state=65904271c7f48ee638a684f55f76a92a1c7ecc7a0c56e5c0a1b83e2510efcb4d'
    assert authUrl ==  redditApp.genAuthUrl(scopes, 'permanent')

def test_reddit_app_getAppFromState(regular_user, admin_user, regularUserRedditApp, regularUserRefreshToken):
    redditApp = RedditApp.query.first()
    app, user_id = RedditApp.getAppFromState('65904271c7f48ee638a684f55f76a92a1c7ecc7a0c56e5c0a1b83e2510efcb4d')
    assert redditApp, None == (app, user_id)

def test_reddit_app_getAppFromState_with_user_id(regular_user, admin_user, regularUserRedditApp, regularUserRefreshToken):
    redditApp = RedditApp.query.first()
    import base64
    state = base64.urlsafe_b64encode(f'{redditApp.state}:123456789012345678'.encode()).decode()
    user_id = 123456789012345678
    app, user_id = RedditApp.getAppFromState(state)
    assert (redditApp, user_id) == (app, user_id)

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_reddit_app_getRefreshToken(loginAs, regularUserRedditApp, regularUserRefreshToken):
    redditApp = RedditApp.query.first()
    if loginAs.is_admin or loginAs.is_internal:
        assert regularUserRefreshToken == redditApp.getRefreshToken('redditor')
    else:
        assert redditApp.getRefreshToken('redditor') is None

def test_reddit_app_getRefreshToken_self(regularUserInstance, regularUserRedditApp, regularUserRefreshToken):
    redditApp = RedditApp.query.first()
    redditApp.owner = regularUserRefreshToken.owner = regularUserInstance
    assert regularUserRefreshToken == redditApp.getRefreshToken('redditor')
