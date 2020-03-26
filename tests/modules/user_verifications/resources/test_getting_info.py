import pytest

from tests.params import labels, users


contentType = 'application/json'

def assertContent(response):
    assert response.content_type == contentType
    assert set(response.json.keys()) >= {'status', 'message'}

def assert403(response):
    assert response.status_code == 403
    assertContent(response)

def test_getting_list_of_user_verifications_by_anonymous_user(flask_app_client):
    response = flask_app_client.get('/api/v1/user_verifications/')

    assert response.status_code == 401
    assertContent(response)

def test_getting_list_of_user_verifications_by_authorized_user(flask_app_client, regular_user, regularUserUserVerification, adminUserUserVerification):
    with flask_app_client.login(regular_user):
        response = flask_app_client.get('/api/v1/user_verifications/')
    assert response.status_code == 200
    assert response.content_type == contentType
    assert isinstance(response.json, list)
    assert len(response.json) == 1
    assert set(response.json[0].keys()) >= {'id', 'discord_id'}
    assert response.json[0]['discord_id'] == regularUserUserVerification.discord_id

def test_getting_user_verification_info_by_unauthorized_user_must_fail(flask_app_client, regularUserInstance, regularUserUserVerification):
    response = flask_app_client.get(f'/api/v1/user_verifications/{regularUserUserVerification.id}')

    assert403(response)

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_getting_user_verification_info(flask_app_client, loginAs, regularUserUserVerification):
    response = flask_app_client.get(f'/api/v1/user_verifications/{regularUserUserVerification.id}')

    if loginAs.is_admin or loginAs.is_internal:
        assert response.status_code == 200
        assert response.content_type == contentType
        assert set(response.json.keys()) >= {'id', 'discord_id'}
        assert response.json['id'] == regularUserUserVerification.id
        assert response.json['discord_id'] == regularUserUserVerification.discord_id
    else:
        assert403(response)