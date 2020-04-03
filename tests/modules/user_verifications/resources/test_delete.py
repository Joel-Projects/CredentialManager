import pytest

from app.modules.user_verifications.models import UserVerification
from tests.params import labels, users
from tests.utils import assert403, assertSuccess


UserVerificationsToDelete = [
    pytest.lazy_fixture('adminUserUserVerification'),
    pytest.lazy_fixture('internalUserUserVerification'),
    pytest.lazy_fixture('regularUserUserVerification')
]

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_deleting_user(flask_app_client, loginAs, regularUserUserVerification):
    response = flask_app_client.delete(f'/api/v1/user_verifications/{regularUserUserVerification.id}')

    if loginAs.is_admin or loginAs.is_internal:
        assertSuccess(response, None, UserVerification, None, deleteItemId=regularUserUserVerification.id)
    else:
        assert403(response, UserVerification, oldItem=regularUserUserVerification, internal=True, action='deleted')

def test_deleting_self(flask_app_client, adminUserInstance, regularUserUserVerification):
    response = flask_app_client.delete(f'/api/v1/user_verifications/{regularUserUserVerification.id}')
    assertSuccess(response, None, UserVerification, None, deleteItemId=regularUserUserVerification.id)