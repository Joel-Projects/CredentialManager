import pytest

from app.modules.api_tokens.models import ApiToken
from app.modules.api_tokens.schemas import DetailedApiTokenSchema
from tests.utils import assertSuccess, assert401, assert403


users = [
    pytest.lazy_fixture('adminUserInstance'),
    pytest.lazy_fixture('internalUserInstance'),
    pytest.lazy_fixture('regularUserInstance')
]
labels = [
    'login_as_admin_user',
    'login_as_internal_user',
    'login_as_regular_user'
]

@pytest.mark.parametrize('loginAs', users, ids=labels)
@pytest.mark.parametrize('tokenToGet', [pytest.lazy_fixture('adminUserApiToken'), pytest.lazy_fixture('internalUserApiToken'), pytest.lazy_fixture('regularUserApiToken')], ids=['get_admin_user_token', 'get_internal_user_token', 'get_regular_user_token'])
def test_getting_api_token_with_id(flask_app_client, loginAs, tokenToGet):
    response = flask_app_client.get(f'/api/v1/api_tokens/{tokenToGet.id}')

    if loginAs == tokenToGet:
        assertSuccess(response, tokenToGet.owner, ApiToken, DetailedApiTokenSchema)
    elif tokenToGet.owner.is_internal:
        if loginAs.is_internal:
            assertSuccess(response, tokenToGet.owner, ApiToken, DetailedApiTokenSchema)
        elif loginAs.is_admin:
            assert403(response, ApiToken, created=False, internal=True)
        else:
            assert403(response, ApiToken, created=False, internal=True)
    elif loginAs.is_admin or loginAs.is_internal:
        assertSuccess(response, tokenToGet.owner, ApiToken, DetailedApiTokenSchema)
    else:
        assert403(response, ApiToken, created=False, internal=True)

def test_getting_api_token_deactivated_user(flask_app_client, regular_user_deactivated):
    with flask_app_client.login(regular_user_deactivated):
        response = flask_app_client.get(f'/api/v1/api_tokens/')
    assert401(response, ApiToken, loginAs=regular_user_deactivated, created=False)

def test_getting_list_of_api_tokens(flask_app_client, regularUserInstance, regularUserApiToken):
    regularUserApiToken.owner = regularUserInstance
    response = flask_app_client.get('/api/v1/api_tokens/')

    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert isinstance(response.json, list)
    assert set(response.json[0].keys()) >= {'id', 'name'}
    assert response.json[0]['id'] == regularUserApiToken.id
    assert response.json[0]['name'] == regularUserApiToken.name

def test_getting_list_of_api_tokens_with_admin(flask_app_client, regularUserInstance, adminUserInstance, regularUserApiToken):
    regularUserApiToken.owner = regularUserInstance
    response = flask_app_client.get('/api/v1/api_tokens/', query_string={'owner_id': regularUserInstance.id})

    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert isinstance(response.json, list)
    assert set(response.json[0].keys()) >= {'id', 'name'}
    assert response.json[0]['id'] == regularUserApiToken.id
    assert response.json[0]['name'] == regularUserApiToken.name

def test_getting_list_of_api_tokens_with_owner(flask_app_client, regularUserInstance, regularUserApiToken):
    regularUserApiToken.owner = regularUserInstance
    response = flask_app_client.get('/api/v1/api_tokens/')

    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert isinstance(response.json, list)
    assert set(response.json[0].keys()) >= {'id', 'name'}
    assert response.json[0]['id'] == regularUserApiToken.id
    assert response.json[0]['name'] == regularUserApiToken.name

def test_getting_list_of_api_tokens_for_admin_user_with_regular_user(flask_app_client, regularUserInstance, admin_user, adminUserApiToken):
    adminUserApiToken.owner = admin_user
    response = flask_app_client.get('/api/v1/api_tokens/', query_string={'owner_id': admin_user.id})

    assert response.status_code == 403
    assert response.content_type == 'application/json'
    assert set(response.json.keys()) >= {'status', 'message'}

def test_getting_list_of_api_tokens_with_bad_owner_id(flask_app_client, regularUserInstance):
    response = flask_app_client.get('/api/v1/api_tokens/', query_string={'owner_id': 100500})

    assert response.status_code == 422
    assert response.content_type == 'application/json'
    assert set(response.json.keys()) >= {'status', 'message'}