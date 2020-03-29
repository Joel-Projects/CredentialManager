import pytest

from tests.params import labels, users


contentType = 'application/json'

def assert403(response):
    assert response.status_code == 403
    assert response.content_type == contentType
    assert set(response.json.keys()) >= {'status', 'message'}

def test_getting_list_of_database_credentials_by_anonymous_user(flask_app_client):
    response = flask_app_client.get('/api/v1/database_credentials/')

    assert response.status_code == 401
    assert response.content_type == contentType
    assert set(response.json.keys()) >= {'status', 'message'}

def test_getting_list_of_database_credentials_by_authorized_user(flask_app_client, regular_user, regularUserDatabaseCredential, adminUserDatabaseCredential):
    with flask_app_client.login(regular_user):
        response = flask_app_client.get('/api/v1/database_credentials/')
    assert response.status_code == 200
    assert response.content_type == contentType
    assert isinstance(response.json, list)
    assert len(response.json) == 1
    assert set(response.json[0].keys()) >= {'id', 'app_name'}
    assert response.json[0]['app_name'] == regularUserDatabaseCredential.app_name

def test_getting_database_credential_info_by_unauthorized_user_must_fail(flask_app_client, regularUserInstance, regularUserDatabaseCredential):
    response = flask_app_client.get(f'/api/v1/database_credentials/{regularUserDatabaseCredential.id}')

    assert403(response)

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_getting_database_credential_info(flask_app_client, loginAs, regularUserDatabaseCredential):
    response = flask_app_client.get(f'/api/v1/database_credentials/{regularUserDatabaseCredential.id}')

    if loginAs.is_admin or loginAs.is_internal:
        assert response.status_code == 200
        assert response.content_type == contentType
        assert set(response.json.keys()) >= {'id', 'app_name'}
        assert response.json['id'] == regularUserDatabaseCredential.id
        assert response.json['app_name'] == regularUserDatabaseCredential.app_name
    else:
        assert403(response)