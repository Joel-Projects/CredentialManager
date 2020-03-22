import json
from datetime import datetime, timezone

import pytest

from app.modules.sentry_tokens.models import SentryToken
from app.modules.sentry_tokens.schemas import DetailedSentryTokenSchema
from tests.params import labels, users
from tests.utils import assert409, assert422


def assertSuccess(owner, response):
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    for field in DetailedSentryTokenSchema.Meta.fields:
        if response.json[field]:
            if getattr(SentryToken, field).type.python_type == datetime:
                assert isinstance(response.json[field], str)
            else:
                assert isinstance(response.json[field], getattr(SentryToken, field).type.python_type)
    createdSentryToken = SentryToken.query.filter_by(id=response.json['id']).first()
    assert createdSentryToken is not None
    assert response.json['owner_id'] == owner.id
    for field in DetailedSentryTokenSchema.Meta.fields:
        if response.json[field]:
            if isinstance(getattr(createdSentryToken, field), datetime):
                assert response.json[field] == datetime.astimezone(getattr(createdSentryToken, field), timezone.utc).isoformat()
            else:
                assert response.json[field] == getattr(createdSentryToken, field)

def assertFail(token, response):
    assert response.status_code == 403
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}
    assert response.json['message'] == "You don't have the permission to access the requested resource."
    createdToken = SentryToken.query.filter(SentryToken.id != token.id).first()
    assert createdToken is None

data = [
    {
        'op': 'replace',
        'path': '/app_name',
        'value': 'newName',
    },
    {
        'op': 'replace',
        'path': '/enabled',
        'value': False,
    }
]

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_modifying_sentry_token(flask_app_client, regularUserSentryToken, loginAs):
    response = flask_app_client.patch(f'/api/v1/sentry_tokens/{regularUserSentryToken.id:d}', content_type='application/json', data=json.dumps(data))

    if loginAs.is_admin or loginAs.is_internal:
        assertSuccess(regularUserSentryToken.owner, response)
    else:
        assertFail(regularUserSentryToken, response)

def test_modifying_sentry_token_by_self(flask_app_client, regularUserInstance, regularUserSentryToken):
    regularUserSentryToken.owner = regularUserInstance
    response = flask_app_client.patch(f'/api/v1/sentry_tokens/{regularUserSentryToken.id}', content_type='application/json', data=json.dumps(data))

    assertSuccess(regularUserInstance, response)

def test_modifying_sentry_token_info_with_invalid_format_must_fail(flask_app_client, regularUserInstance, regularUserSentryToken):
    regularUserSentryToken.owner = regularUserInstance
    response = flask_app_client.patch(f'/api/v1/sentry_tokens/{regularUserInstance.id}', content_type='application/json', data=json.dumps([{'op': 'test', 'path': '/app_name', 'value': '', }, {'op': 'replace', 'path': '/enabled', }, ]))
    assert422(response, SentryToken, [('1', {'_schema': ['value is required']})], oldItem=regularUserSentryToken, action='patch')

def test_modifying_sentry_token_info_with_conflict_data_must_fail(flask_app_client, regularUserInstance, regularUserSentryToken, adminUserSentryToken):
    regularUserSentryToken.owner = regularUserInstance
    adminUserSentryToken.app_name = 'differentName'
    adminUserSentryToken.owner = regularUserInstance
    response = flask_app_client.patch(f'/api/v1/sentry_tokens/{regularUserSentryToken.id}', content_type='application/json', data=json.dumps([{'op': 'replace', 'path': '/app_name', 'value': adminUserSentryToken.app_name}]))

    assert409(response, SentryToken, 'Failed to update Sentry Token details.', loginAs=regularUserInstance, messageAttrs=[('1', {'_schema': ['value is required']})], oldItem=regularUserSentryToken, action='patch')