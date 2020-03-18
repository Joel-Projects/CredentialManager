import pytest
from app.modules.api_tokens.models import ApiToken


def assertPass(response, tokenToDelete):
    assert response.status_code == 204
    assert response.content_type == 'text/html; charset=utf-8'
    assert response.content_length is None
    initalUser = ApiToken.query.get(tokenToDelete.id)
    assert initalUser is None

def assertCorrectResponseFormat(response):
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}

def assert401(response, tokenToDelete):
    assert response.status_code == 401
    assertCorrectResponseFormat(response)
    assert response.json['message'] == "The server could not verify that you are authorized to access the URL requested. You either supplied the wrong credentials (e.g. a bad password), or your browser doesn't understand how to supply the credentials required."
    initalUser = ApiToken.query.get(tokenToDelete.id)
    assert initalUser is not None

def assert403(response, tokenToDelete):
    assert response.status_code == 403
    assertCorrectResponseFormat(response)
    assert response.json['message'] == "You don't have the permission to access the requested resource."
    initalUser = ApiToken.query.get(tokenToDelete.id)
    assert initalUser is not None

users = [
    pytest.lazy_fixture('adminUserInstance'),
    pytest.lazy_fixture('internalUserInstance'),
    pytest.lazy_fixture('regularUserInstance')
]
labels = [
    'as_admin_user',
    'as_internal_user',
    'as_regular_user'
]

tokensToDelete = [
    pytest.lazy_fixture('regularUserApiToken'),
    pytest.lazy_fixture('adminUserApiToken'),
    pytest.lazy_fixture('internalUserApiToken'),
]

@pytest.mark.parametrize('loginAs', users, ids=labels)
@pytest.mark.parametrize('tokenToDelete', tokensToDelete, ids=['delete_regular_user_api_token', 'delete_admin_user_api_token', 'delete_internal_user_api_token'])
def test_deleting_user(flask_app_client, loginAs, tokenToDelete):
    response = flask_app_client.delete(f'/api/v1/api_tokens/{tokenToDelete.id}')

    if tokenToDelete.owner.is_internal:
        if loginAs.is_internal:
            assertPass(response, tokenToDelete)
        else:
            assert403(response, tokenToDelete)
    elif loginAs.is_admin or loginAs.is_internal:
        assertPass(response, tokenToDelete)
    else:
        assert403(response, tokenToDelete)

@pytest.mark.parametrize('loginAs', [pytest.lazy_fixture('adminUserInstanceDeactivated'), pytest.lazy_fixture('internalUserInstanceDeactivated'), pytest.lazy_fixture('regularUserInstanceDeactivated')], ids=['as_deactivated_admin_user', 'as_deactivated_internal_user', 'as_deactivated_regular_user'])
@pytest.mark.parametrize('tokenToDelete', tokensToDelete, ids=['delete_regular_user_api_token', 'delete_admin_user_api_token', 'delete_internal_user_api_token'])
def test_deleting_user_deactivated(flask_app_client, loginAs, tokenToDelete):
    with flask_app_client.login(loginAs):
        response = flask_app_client.delete(f'/api/v1/api_tokens/{tokenToDelete.id}')
    assert401(response, tokenToDelete)