import pytest

from tests.params import labels, users


contentType = 'application/json'

def assertContent(response):
    assert response.content_type == contentType
    assert set(response.json.keys()) >= {'status', 'message'}

def assert403(response):
    assert response.status_code == 403
    assertContent(response)

def test_getting_list_of_reddit_apps_by_anonymous_user(flask_app_client):
    response = flask_app_client.get('/api/v1/reddit_apps/')

    assert response.status_code == 401
    assertContent(response)

def test_getting_list_of_reddit_apps_by_authorized_user(flask_app_client, regular_user, regularUserRedditApp, adminUserRedditApp):
    with flask_app_client.login(regular_user):
        response = flask_app_client.get('/api/v1/reddit_apps/')
    assert response.status_code == 200
    assert response.content_type == contentType
    assert isinstance(response.json, list)
    assert len(response.json) == 1
    assert set(response.json[0].keys()) >= {'id', 'app_name'}
    assert response.json[0]['app_name'] == regularUserRedditApp.app_name

def test_getting_reddit_app_info_by_unauthorized_user_must_fail(flask_app_client, regularUserInstance, regularUserRedditApp):
    response = flask_app_client.get(f'/api/v1/reddit_apps/{regularUserRedditApp.id}')

    assert403(response)

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_getting_reddit_app_info(flask_app_client, loginAs, regularUserRedditApp):
    response = flask_app_client.get(f'/api/v1/reddit_apps/{regularUserRedditApp.id}')

    if loginAs.is_admin or loginAs.is_internal:
        assert response.status_code == 200
        assert response.content_type == contentType
        assert set(response.json.keys()) >= {'id', 'app_name'}
        assert response.json['id'] == regularUserRedditApp.id
        assert response.json['app_name'] == regularUserRedditApp.app_name
    else:
        assert403(response)

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_getting_redditor_from_refresh_token(flask_app_client, loginAs, regularUserRedditApp, regularUserRefreshToken):
    response = flask_app_client.post(f'/api/v1/reddit_apps/{regularUserRedditApp.id}', data={'redditor': 'redditor'})

    if loginAs.is_admin or loginAs.is_internal:
        assert response.status_code == 200
        assert response.content_type == contentType
        assert set(response.json.keys()) >= {'id', 'reddit_app', 'redditor', 'refresh_token'}
        assert response.json['reddit_app'] == regularUserRedditApp.id
        assert response.json['redditor'] == regularUserRefreshToken.redditor
        assert response.json['refresh_token'] == regularUserRefreshToken.refresh_token
    else:
        assert403(response)

def test_getting_redditor_from_non_existant_refresh_token(flask_app_client, regularUserInstance, regularUserRedditApp):
    regularUserRedditApp.owner = regularUserInstance
    response = flask_app_client.post(f'/api/v1/reddit_apps/{regularUserRedditApp.id}', data={'redditor': 'redditor'})
    assert response.status_code == 404
    assertContent(response)