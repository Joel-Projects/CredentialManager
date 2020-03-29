import json
import pytest

from app.modules.database_credentials.models import DatabaseCredential
from app.modules.database_credentials.schemas import DetailedDatabaseCredentialSchema
from tests.params import labels, users
from tests.utils import assert403, assert409, assert422, assertSuccess


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
def test_modifying_database_credential(flask_app_client, regularUserDatabaseCredential, loginAs):
    response = flask_app_client.patch(f'/api/v1/database_credentials/{regularUserDatabaseCredential.id:d}', content_type='application/json', data=json.dumps(data))

    if loginAs.is_admin or loginAs.is_internal:
        assertSuccess(response, regularUserDatabaseCredential.owner, DatabaseCredential, DetailedDatabaseCredentialSchema)
    else:
        assert403(response, DatabaseCredential, action='patch', internal=True, oldItem=regularUserDatabaseCredential)

def test_modifying_database_credential_by_self(flask_app_client, regularUserInstance, regularUserDatabaseCredential):
    regularUserDatabaseCredential.owner = regularUserInstance
    response = flask_app_client.patch(f'/api/v1/database_credentials/{regularUserDatabaseCredential.id}', content_type='application/json', data=json.dumps(data))

    assertSuccess(response, regularUserDatabaseCredential.owner, DatabaseCredential, DetailedDatabaseCredentialSchema)

def test_modifying_database_credential_info_with_invalid_format_must_fail(flask_app_client, regularUserInstance, regularUserDatabaseCredential):
    regularUserDatabaseCredential.owner = regularUserInstance
    response = flask_app_client.patch(f'/api/v1/database_credentials/{regularUserInstance.id}', content_type='application/json', data=json.dumps([{'op': 'test', 'path': '/app_name', 'value': '', }, {'op': 'replace', 'path': '/enabled', }, ]))
    assert422(response, DatabaseCredential, [('1', {'_schema': ['value is required']})], oldItem=regularUserDatabaseCredential, action='patch')

def test_modifying_database_credential_info_with_conflict_data_must_fail(flask_app_client, regularUserInstance, regularUserDatabaseCredential, adminUserDatabaseCredential):
    regularUserDatabaseCredential.owner = regularUserInstance
    adminUserDatabaseCredential.app_name = 'differentName'
    adminUserDatabaseCredential.owner = regularUserInstance
    response = flask_app_client.patch(f'/api/v1/database_credentials/{regularUserDatabaseCredential.id}', content_type='application/json', data=json.dumps([{'op': 'replace', 'path': '/app_name', 'value': adminUserDatabaseCredential.app_name}]))

    assert409(response, DatabaseCredential, 'Failed to update Database Credential details.', loginAs=regularUserInstance, messageAttrs=[('1', {'_schema': ['value is required']})], oldItem=regularUserDatabaseCredential, action='patch')