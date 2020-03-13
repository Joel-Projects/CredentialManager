import json
from datetime import datetime, timezone

import pytest

from app.modules.api_tokens.models import ApiToken
from app.modules.api_tokens.schemas import DetailedApiTokenSchema
from tests.utils import assert409, assert422


def assertSuccess(owner, response):
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    for field in DetailedApiTokenSchema.Meta.fields:
        if response.json[field]:
            if getattr(ApiToken, field).type.python_type == datetime:
                assert isinstance(response.json[field], str)
            else:
                assert isinstance(response.json[field], getattr(ApiToken, field).type.python_type)
    createdApiToken = ApiToken.query.filter_by(id=response.json['id']).first()
    assert createdApiToken is not None
    assert response.json['owner_id'] == owner.id
    for field in DetailedApiTokenSchema.Meta.fields:
        if response.json[field]:
            if isinstance(getattr(createdApiToken, field), datetime):
                assert response.json[field] == datetime.astimezone(getattr(createdApiToken, field), timezone.utc).isoformat()
            else:
                assert response.json[field] == getattr(createdApiToken, field)

def assertFail(token, response):
    assert response.status_code == 403
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}
    assert response.json['message'] == "You don't have the permission to access the requested resource."
    createdToken = ApiToken.query.filter(ApiToken.id != token.id).first()
    assert createdToken is None

data = [
    {
        'op': 'replace',
        'path': '/name',
        'value': 'newName',
    },
    {
        'op': 'replace',
        'path': '/enabled',
        'value': False,
    }
]
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

tokens = [
    pytest.lazy_fixture('regularUserApiToken'),
    pytest.lazy_fixture('adminUserApiToken'),
    pytest.lazy_fixture('internalUserApiToken'),
]

@pytest.mark.parametrize('token', tokens, ids=['modify_regular_user_token', 'modify_admin_user_token', 'modify_regular_user_token'])
@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_modifying_api_token(flask_app_client, token, loginAs):
    response = flask_app_client.patch(f'/api/v1/api_tokens/{token.id:d}', content_type='application/json', data=json.dumps(data))

    if token.owner.is_internal:
        if loginAs.is_internal:
            assertSuccess(token.owner, response)
        else:
            assertFail(token, response)
    elif loginAs.is_admin or loginAs.is_internal:
        assertSuccess(token.owner, response)
    else:
        assertFail(token, response)

def test_modifying_api_token_by_self(flask_app_client, regularUserInstance, regularUserApiToken):
    regularUserApiToken.owner = regularUserInstance
    response = flask_app_client.patch(f'/api/v1/api_tokens/{regularUserApiToken.id}', content_type='application/json', data=json.dumps(data))

    assertSuccess(regularUserInstance, response)

def test_modifying_api_token_info_with_invalid_format_must_fail(flask_app_client, regularUserInstance, regularUserApiToken):
    regularUserApiToken.owner = regularUserInstance
    response = flask_app_client.patch(f'/api/v1/api_tokens/{regularUserInstance.id}', content_type='application/json', data=json.dumps([{'op': 'test', 'path': '/name', 'value': '', }, {'op': 'replace', 'path': '/enabled', }, ]))
    assert422(response, ApiToken, [('1', {'_schema': ['value is required']})], oldItem=regularUserApiToken, action='patch')

def test_modifying_api_token_info_with_conflict_data_must_fail(flask_app_client, regularUserInstance, regularUserApiToken, adminUserApiToken):
    regularUserApiToken.owner = regularUserInstance
    adminUserApiToken.name = 'differentName'
    adminUserApiToken.owner = regularUserInstance
    response = flask_app_client.patch(f'/api/v1/api_tokens/{regularUserApiToken.id}', content_type='application/json', data=json.dumps([{'op': 'replace', 'path': '/name', 'value': adminUserApiToken.name}]))

    assert409(response, ApiToken, 'Failed to update API Token details.', loginAs=regularUserInstance, messageAttrs=[('1', {'_schema': ['value is required']})], oldItem=regularUserApiToken, action='patch')