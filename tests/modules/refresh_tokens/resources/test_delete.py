import pytest

from app.modules.refresh_tokens.models import RefreshToken
from tests.params import labels, users
from tests.utils import assert403, assertSuccess

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_deleting_user(flask_app_client, loginAs, regularUserRefreshToken):
    response = flask_app_client.delete(f'/api/v1/refresh_tokens/{regularUserRefreshToken.id}')

    if loginAs.is_admin or loginAs.is_internal:
        assertSuccess(response, None, RefreshToken, None, deleteItemId=regularUserRefreshToken.id)
    else:
        assert403(response, RefreshToken, oldItem=regularUserRefreshToken, internal=True, action='deleted')

def test_deleting_self(flask_app_client, adminUserInstance, regularUserRefreshToken):
    response = flask_app_client.delete(f'/api/v1/refresh_tokens/{regularUserRefreshToken.id}')
    assertSuccess(response, None, RefreshToken, None, deleteItemId=regularUserRefreshToken.id)