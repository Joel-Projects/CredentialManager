import pytest

from app.modules.database_credentials.models import DatabaseCredential
from tests.params import labels, users
from tests.utils import assert403, assertSuccess


databaseCredentialsToDelete = [
    pytest.lazy_fixture('adminUserDatabaseCredential'),
    pytest.lazy_fixture('internalUserDatabaseCredential'),
    pytest.lazy_fixture('regularUserDatabaseCredential')
]

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_deleting_user(flask_app_client, loginAs, regularUserDatabaseCredential):
    response = flask_app_client.delete(f'/api/v1/database_credentials/{regularUserDatabaseCredential.id}')

    if loginAs.is_admin or loginAs.is_internal:
        assertSuccess(response, None, DatabaseCredential, None, deleteItemId=regularUserDatabaseCredential.id)
    else:
        assert403(response, DatabaseCredential, oldItem=regularUserDatabaseCredential, internal=True, action='deleted')

def test_deleting_self(flask_app_client, adminUserInstance, regularUserDatabaseCredential):
    response = flask_app_client.delete(f'/api/v1/database_credentials/{regularUserDatabaseCredential.id}')
    assertSuccess(response, None, DatabaseCredential, None, deleteItemId=regularUserDatabaseCredential.id)