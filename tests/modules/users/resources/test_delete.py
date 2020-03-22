import pytest

from app.modules.users.models import User
from tests.params import labels, users
from tests.utils import assert401, assert403, assert409, assertSuccess

usersToDelete = [
    pytest.lazy_fixture('admin_user'),
    pytest.lazy_fixture('internal_user'),
    pytest.lazy_fixture('regular_user'),
]

@pytest.mark.parametrize('loginAs', users, ids=labels)
@pytest.mark.parametrize('userToDelete', usersToDelete, ids=['delete_admin_user', 'delete_internal_user', 'delete_regular_user'])
def test_deleting_user(flask_app_client, loginAs, userToDelete):
    response = flask_app_client.delete(f'/api/v1/users/{userToDelete.id}')

    if userToDelete.is_internal:
        if loginAs.is_internal:
            assertSuccess(response, None, User, None, deleteItemId=userToDelete.id)
        else:
            assert403(response, User, oldItem=userToDelete, internal=True, action='deleted')
    elif loginAs.is_admin or loginAs.is_internal:
        assertSuccess(response, None, User, None, deleteItemId=userToDelete.id)
    else:
        assert403(response, User, oldItem=userToDelete, internal=True, action='deleted')

def test_deleting_self(flask_app_client, adminUserInstance):
    response = flask_app_client.delete(f'/api/v1/users/{adminUserInstance.id}')
    assert409(response, User, message="You can't delete yourself.", oldItem=adminUserInstance, loginAs=adminUserInstance, action='deleted')

@pytest.mark.parametrize('loginAs', [pytest.lazy_fixture('adminUserInstanceDeactivated'), pytest.lazy_fixture('internalUserInstanceDeactivated'), pytest.lazy_fixture('regularUserInstanceDeactivated')], ids=['as_deactivated_admin_user', 'as_deactivated_internal_user', 'as_deactivated_regular_user'])
@pytest.mark.parametrize('userToDelete', [pytest.lazy_fixture('internal_user'), pytest.lazy_fixture('admin_user'), pytest.lazy_fixture('regular_user')], ids=['delete_admin_user', 'delete_internal_user', 'delete_regular_user'])
def test_deleting_user_deactivated(flask_app_client, loginAs, userToDelete):
    with flask_app_client.login(loginAs):
        response = flask_app_client.delete(f'/api/v1/users/{userToDelete.id}')
    assert401(response, userToDelete, loginAs=loginAs)