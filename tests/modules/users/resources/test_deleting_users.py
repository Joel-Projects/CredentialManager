import pytest
from app.modules.users.models import User
from tests.utils import assertSuccess, assert401, assert403, assert409

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

usersToDelete = [
    pytest.lazy_fixture('internal_user'),
    pytest.lazy_fixture('internal_user2'),
    pytest.lazy_fixture('admin_user'),
    pytest.lazy_fixture('admin_user2'),
    pytest.lazy_fixture('regular_user'),
    pytest.lazy_fixture('regular_user2'),
]

@pytest.mark.parametrize('loginAs', users, ids=labels)
@pytest.mark.parametrize('userToDelete', usersToDelete, ids=['delete_admin_user', 'delete_admin_user2', 'delete_internal_user', 'delete_internal_user2', 'delete_regular_user', 'delete_regular_user2'])
def test_deleting_user(flask_app_client, loginAs: User, userToDelete: User):
    response = flask_app_client.delete(f'/api/v1/users/{userToDelete.id}')

    if userToDelete.is_internal:
        if loginAs.is_internal:
            assertSuccess(response, None, User, None, deleteItemId=userToDelete.id)
        else:
            assert403(response, User, oldItem=userToDelete.id, internal=True, action='deleted')
    elif loginAs.is_admin or loginAs.is_internal:
        assertSuccess(response, None, User, None, deleteItemId=userToDelete.id)
    else:
        assert403(response, User, oldItem=userToDelete.id, internal=True, action='deleted')

def test_deleting_self(flask_app_client, admin_user):
    with flask_app_client.login(admin_user):
        response = flask_app_client.delete(f'/api/v1/users/{admin_user.id}')
    assert409(response, User, message="You can't delete yourself.", oldItem=admin_user, loginAs=admin_user)

@pytest.mark.parametrize('loginAs', [pytest.lazy_fixture('adminUserInstanceDeactivated'), pytest.lazy_fixture('internalUserInstanceDeactivated'), pytest.lazy_fixture('regularUserInstanceDeactivated')], ids=['as_deactivated_admin_user', 'as_deactivated_internal_user', 'as_deactivated_regular_user'])
@pytest.mark.parametrize('userToDelete', [pytest.lazy_fixture('internal_user'), pytest.lazy_fixture('admin_user'), pytest.lazy_fixture('regular_user')], ids=['delete_admin_user', 'delete_internal_user', 'delete_regular_user'])
def test_deleting_user_deactivated(flask_app_client, loginAs: User, userToDelete: User):
    with flask_app_client.login(loginAs):
        response = flask_app_client.delete(f'/api/v1/users/{userToDelete.id}')
    assert401(response, userToDelete, loginAs=loginAs)