from datetime import datetime, timezone

import pytest

from app.modules.api_tokens.models import ApiToken
from app.modules.api_tokens.schemas import DetailedApiTokenSchema
from tests.utils import assertSuccess, assert403, assert403, assert422, assert401


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
path = '/api/v1/api_tokens/'

@pytest.mark.parametrize('loginAs', users, ids=labels)
@pytest.mark.parametrize('owner', [pytest.lazy_fixture('admin_user'), pytest.lazy_fixture('internal_user'), pytest.lazy_fixture('regular_user')], ids=['for_admin_user', 'for_internal_user', 'for_regular_user'])
def test_creating_api(flask_app_client, loginAs, owner):
    response = flask_app_client.post(path, data={'name': 'testToken', 'owner_id': owner.id})

    if owner.is_internal:
        if loginAs.is_internal:
            assertSuccess(response, owner, ApiToken, DetailedApiTokenSchema)
        else:
            assert403(response, ApiToken, internal=True)
    elif loginAs.is_admin or loginAs.is_internal:
        assertSuccess(response, owner, ApiToken, DetailedApiTokenSchema)
    else:
        assert403(response, ApiToken)

def test_creating_api_token_by_deactivated_user(flask_app_client, regular_user_deactivated):
    with flask_app_client.login(regular_user_deactivated):
        response = flask_app_client.post(path, data={'name': 'testToken'})
    model = ApiToken
    assert401(response, model, loginAs=regular_user_deactivated)

def test_creating_api_token_for_self(flask_app_client, regularUserInstance):
    response = flask_app_client.post(path, data={'name': 'testToken'})
    assertSuccess(response, regularUserInstance, ApiToken, DetailedApiTokenSchema)

def test_creating_api_token_for_self_with_id(flask_app_client, regularUserInstance):
    response = flask_app_client.post(path, data={'name': 'testToken', 'owner_id': regularUserInstance.id})
    assertSuccess(response, regularUserInstance, ApiToken, DetailedApiTokenSchema)

@pytest.mark.parametrize('length', range(16, 72, 8))
def test_creating_api_token_with_different_length(flask_app_client, regularUserInstance, length):
    response = flask_app_client.post(path, data={'name': 'testToken', 'length': length})
    assertSuccess(response, regularUserInstance, ApiToken, DetailedApiTokenSchema)

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_creating_api_token_with_bad_name(flask_app_client, loginAs):
    response = flask_app_client.post(path, data={'name': 'to'})

    assert422(response, ApiToken, [('name', ['Name must be greater than 3 characters long.'])])

@pytest.mark.parametrize('length', [8, 256])
def test_creating_api_token_with_bad_length(flask_app_client, regularUserInstance, length):
    response = flask_app_client.post(path, data={'name': 'token', 'length': length})

    if length < 16:
        assert422(response, ApiToken, [('length', ['Length must be greater than 16.'])])
    elif length > 128:
        assert422(response, ApiToken, [('length', ['Length must be less than 128.'])])