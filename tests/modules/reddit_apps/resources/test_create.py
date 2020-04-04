import pytest

from app.modules.reddit_apps.models import RedditApp
from app.modules.reddit_apps.schemas import DetailedRedditAppSchema
from tests.params import labels, users
from tests.utils import assert403, assert422, assertSuccess


path = '/api/v1/reddit_apps/'
data = {
    'app_name': 'reddit_app',
    'client_id': 'client_id',
    'client_secret': 'client_secret',
    'user_agent': 'user_agent',
    'redirect_uri': 'https://credmgr.jesassn.org/oauth2/reddit_callback',
    'app_type': 'web',
}

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_creating_reddit_app(flask_app_client, loginAs, regular_user):
    response = flask_app_client.post(path, data={'owner_id': regular_user.id, **data})

    if loginAs.is_admin or loginAs.is_internal:
        assertSuccess(response, regular_user, RedditApp, DetailedRedditAppSchema)
    else:
        assert403(response, RedditApp, action='create')

def test_creating_reddit_app_for_self(flask_app_client, regularUserInstance):
    response = flask_app_client.post(path, data=data)
    assertSuccess(response, regularUserInstance, RedditApp, DetailedRedditAppSchema)

def test_creating_reddit_app_for_self_with_owner(flask_app_client, regularUserInstance):
    response = flask_app_client.post(path, data={'owner_id': regularUserInstance.id, **data})
    assertSuccess(response, regularUserInstance, RedditApp, DetailedRedditAppSchema)

def test_creating_reddit_app_auth_url(db, flask_app_client, regularUserInstance, regularUserRedditApp):
    regularUserRedditApp.owner = regularUserInstance
    scopes = ['identity', 'read', 'privatemessages']
    response = flask_app_client.post(f'/api/v1/reddit_apps/{regularUserRedditApp.id}/generate_auth', data={'scopes': scopes, 'duration': 'permanent'})
    authUrl = 'https://www.reddit.com/api/v1/authorize?client_id=client_id&duration=permanent&redirect_uri=https%3A%2F%2Fcredmgr.jesassn.org%2Foauth2%2Freddit_callback&response_type=code&scope=identity+read+privatemessages&state=65904271c7f48ee638a684f55f76a92a1c7ecc7a0c56e5c0a1b83e2510efcb4d'
    assert response.json['auth_url'] == authUrl

def test_creating_reddit_app_auth_url_with_user_verification(db, flask_app_client, regularUserInstance, regularUserRedditApp, regularUserUserVerification):
    regularUserRedditApp.owner = regularUserInstance
    scopes = ['identity', 'read', 'privatemessages']
    response = flask_app_client.post(f'/api/v1/reddit_apps/{regularUserRedditApp.id}/generate_auth', data={'scopes': scopes, 'duration': 'permanent', 'user_verification_id': regularUserUserVerification.id})
    authUrl = 'https://www.reddit.com/api/v1/authorize?client_id=client_id&duration=permanent&redirect_uri=https%3A%2F%2Fcredmgr.jesassn.org%2Foauth2%2Freddit_callback&response_type=code&scope=identity+read+privatemessages&state=NjU5MDQyNzFjN2Y0OGVlNjM4YTY4NGY1NWY3NmE5MmExYzdlY2M3YTBjNTZlNWMwYTFiODNlMjUxMGVmY2I0ZDoxMjM0NTY3ODkwMTIzNDU2Nzg%3D'
    assert response.json['auth_url'] == authUrl

def test_creating_reddit_app_auth_url_with_user_verification_user_id(db, flask_app_client, regularUserInstance, regularUserRedditApp, regularUserUserVerification):
    regularUserRedditApp.owner = regularUserInstance
    scopes = ['identity', 'read', 'privatemessages']
    response = flask_app_client.post(f'/api/v1/reddit_apps/{regularUserRedditApp.id}/generate_auth', data={'scopes': scopes, 'duration': 'permanent', 'user_verification_user_id': regularUserUserVerification.user_id})
    authUrl = 'https://www.reddit.com/api/v1/authorize?client_id=client_id&duration=permanent&redirect_uri=https%3A%2F%2Fcredmgr.jesassn.org%2Foauth2%2Freddit_callback&response_type=code&scope=identity+read+privatemessages&state=NjU5MDQyNzFjN2Y0OGVlNjM4YTY4NGY1NWY3NmE5MmExYzdlY2M3YTBjNTZlNWMwYTFiODNlMjUxMGVmY2I0ZDoxMjM0NTY3ODkwMTIzNDU2Nzg%3D'
    assert response.json['auth_url'] == authUrl

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_creating_reddit_app_with_bad_name(flask_app_client, loginAs):
    response = flask_app_client.post(path, data={**data, 'app_name': 'to'})
    assert422(response, RedditApp, messageAttrs=[('app_name', ['Name must be greater than 3 characters long.'])])

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_creating_reddit_app_with_bad_app_type(flask_app_client, loginAs):
    response = flask_app_client.post(path, data={**data, 'app_type': 'bad_type'})
    assert422(response, RedditApp, messageAttrs=[('app_type', ["App type is not valid. Valid types are: 'web', 'installed'. or 'script'"])])