import pytest

from tests.params import labels, users


contentType = 'application/json'

def assert403(response):
    assert response.status_code == 403
    assert response.content_type == contentType
    assert set(response.json.keys()) >= {'status', 'message'}

def test_getting_list_of_sentry_tokens_by_anonymous_user(flask_app_client):
    response = flask_app_client.get('/api/v1/sentry_tokens/')

    assert response.status_code == 401
    assert response.content_type == contentType
    assert set(response.json.keys()) >= {'status', 'message'}

def test_getting_list_of_sentry_tokens_by_authorized_user(flask_app_client, regular_user, regularUserSentryToken, adminUserSentryToken):
    with flask_app_client.login(regular_user):
        response = flask_app_client.get('/api/v1/sentry_tokens/')
    assert response.status_code == 200
    assert response.content_type == contentType
    assert isinstance(response.json, list)
    assert len(response.json) == 1
    assert set(response.json[0].keys()) >= {'id', 'app_name'}
    assert response.json[0]['app_name'] == regularUserSentryToken.app_name

def test_getting_sentry_token_info_by_unauthorized_user_must_fail(flask_app_client, regularUserInstance, regularUserSentryToken):
    response = flask_app_client.get(f'/api/v1/sentry_tokens/{regularUserSentryToken.id}')

    assert403(response)

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_getting_sentry_token_info(flask_app_client, loginAs, regularUserSentryToken):
    response = flask_app_client.get(f'/api/v1/sentry_tokens/{regularUserSentryToken.id}')

    if loginAs.is_admin or loginAs.is_internal:
        assert response.status_code == 200
        assert response.content_type == contentType
        assert set(response.json.keys()) >= {'id', 'app_name'}
        assert response.json['id'] == regularUserSentryToken.id
        assert response.json['app_name'] == regularUserSentryToken.app_name
    else:
        assert403(response)