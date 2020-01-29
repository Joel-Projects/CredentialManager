import pytest
from app.modules.api_tokens.models import ApiToken

def assertSuccess(response, token):
    assert response.status_code == 204
    assert response.content_type == 'text/html; charset=utf-8'
    assert response.content_length is None

    from app.modules.api_tokens.models import ApiToken

    initalToken = ApiToken.query.get(token.id)
    assert initalToken is None

def assertFail(response, token):
    assert response.status_code == 403
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}
    assert response.json['message'] == "You don't have the permission to access the requested resource."

    from app.modules.users.models import ApiToken

    createdApiToken = ApiToken.query.get(token.id)
    assert createdApiToken is not None

def assertInactive(response, token):
    assert response.status_code == 401
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}
    assert response.json['message'] == "The server could not verify that you are authorized to access the URL requested. You either supplied the wrong credentials (e.g. a bad password), or your browser doesn't understand how to supply the credentials required."

    from app.modules.users.models import ApiToken

    createdApiToken = ApiToken.query.get(token.id)
    assert createdApiToken is not None


# noinspection PyUnresolvedReferences
@pytest.mark.parametrize('token', [pytest.lazy_fixture('regularUserApiToken'), pytest.lazy_fixture('adminUserApiToken'), pytest.lazy_fixture('internalUserApiToken')], ids=['regular_user_token', 'admin_user_token', 'internal_user_token'])
@pytest.mark.parametrize('deletingUser', [pytest.lazy_fixture('admin_user'), pytest.lazy_fixture('deactivated_admin_user'), pytest.lazy_fixture('internal_user'), pytest.lazy_fixture('regular_user')], ids=['as_admin_user', 'as_deactivated_admin_user', 'as_internal_user', 'as_regular_user'])
def test_deleting_api_token(flask_app_client, token: ApiToken, deletingUser):

    with flask_app_client.login(deletingUser):
        response = flask_app_client.delete(f'/api/v1/api_tokens/{token.id}')

    if deletingUser.is_active:
        if token.owner == deletingUser:
            assertSuccess(response, token)
        elif token.owner.is_internal:
            if deletingUser.is_internal:
                assertSuccess(response, token)
            else:
                assertFail(response, token)
        elif deletingUser.is_admin or deletingUser.is_internal:
            assertSuccess(response, token)
        else:
            assertFail(response, token)
    else:
        assertInactive(response, token)