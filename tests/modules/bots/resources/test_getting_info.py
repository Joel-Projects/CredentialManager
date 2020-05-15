import pytest

from tests.params import labels, users


contentType = 'application/json'

def assertContent(response):
    assert response.content_type == contentType
    assert set(response.json.keys()) >= {'status', 'message'}

def assert403(response):
    assert response.status_code == 403
    assertContent(response)

def test_getting_list_of_bots_by_anonymous_user(flask_app_client):
    response = flask_app_client.get('/api/v1/bots/')

    assert response.status_code == 401
    assertContent(response)

def test_getting_list_of_bots_by_authorized_user(flask_app_client, regular_user, regularUserBot, adminUserBot):
    with flask_app_client.login(regular_user):
        response = flask_app_client.get('/api/v1/bots/')

    assert response.status_code == 200
    assert response.content_type == contentType
    assert isinstance(response.json, list)
    assert len(response.json) == 1
    assert set(response.json[0].keys()) >= {'id', 'app_name'}
    assert response.json[0]['app_name'] == regularUserBot.app_name

def test_getting_bot_info_by_unauthorized_user_must_fail(flask_app_client, regularUserInstance, regularUserBot):
    response = flask_app_client.get(f'/api/v1/bots/{regularUserBot.id}')

    assert403(response)

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_getting_bot_info(flask_app_client, loginAs, regularUserBot):
    response = flask_app_client.get(f'/api/v1/bots/{regularUserBot.id}')

    if loginAs.is_admin or loginAs.is_internal:
        assert response.status_code == 200
        assert response.content_type == contentType
        assert set(response.json.keys()) >= {'id', 'app_name'}
        assert response.json['id'] == regularUserBot.id
        assert response.json['app_name'] == regularUserBot.app_name
    else:
        assert403(response)

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_getting_bot_info_disabled(flask_app_client, loginAs, regularUserBot):
    regularUserBot.enabled = False
    response = flask_app_client.get(f'/api/v1/bots/{regularUserBot.id}')

    if loginAs.is_admin or loginAs.is_internal:
        assert response.status_code == 424
    else:
        assert403(response)

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_getting_bot_info_disabled_apps(flask_app_client, loginAs, regularUserBot):
    regularUserBot.enabled = True
    regularUserBot.reddit_app.enabled = False
    if not (loginAs.is_admin or loginAs.is_internal):
        regularUserBot.owner = loginAs
    response = flask_app_client.get(f'/api/v1/bots/{regularUserBot.id}')

    assert response.status_code == 424

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_getting_bot_info_by_name(flask_app_client, loginAs, regularUserBot):
    response = flask_app_client.post(f'/api/v1/bots/by_name', data={'app_name': regularUserBot.app_name})

    if loginAs.is_admin or loginAs.is_internal:
        assert response.status_code == 200
        assert response.content_type == contentType
        assert set(response.json.keys()) >= {'id', 'app_name'}
        assert response.json['id'] == regularUserBot.id
        assert response.json['app_name'] == regularUserBot.app_name
    else:
        assert response.status_code == 404