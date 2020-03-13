import pytest
from app.modules.users.models import User


def assertPass(response, userToDelete):
    assert response.status_code == 204
    assert response.content_type == 'text/html; charset=utf-8'
    assert response.content_length is None
    initalUser = User.query.get(userToDelete.id)
    assert initalUser is None

def assertCorrectResponseFormat(response):
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}

def assert401(response, userToDelete):
    assert response.status_code == 401
    assertCorrectResponseFormat(response)
    assert response.json['message'] == "The server could not verify that you are authorized to access the URL requested. You either supplied the wrong credentials (e.g. a bad password), or your browser doesn't understand how to supply the credentials required."
    initalUser = User.query.get(userToDelete.id)
    assert initalUser is not None

def assert403(response, userToDelete):
    assert response.status_code == 403
    assertCorrectResponseFormat(response)
    assert response.json['message'] == "You don't have the permission to access the requested resource."
    initalUser = User.query.get(userToDelete.id)
    assert initalUser is not None

def assert409(response, userToDelete):
    assert response.status_code == 409
    assertCorrectResponseFormat(response)
    assert response.json['message'] == "You can't delete yourself."
    initalUser = User.query.get(userToDelete.id)
    assert initalUser is not None

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

    if loginAs == userToDelete:
        if loginAs.is_admin or loginAs.is_internal:
            assert409(response, userToDelete)
        else:
            assert403(response, userToDelete)
    elif userToDelete.is_internal:
        if loginAs.is_internal:
            assertPass(response, userToDelete)
        else:
            assert403(response, userToDelete)
    elif loginAs.is_admin or loginAs.is_internal:
        assertPass(response, userToDelete)
    else:
        assert403(response, userToDelete)


@pytest.mark.parametrize('loginAs', [pytest.lazy_fixture('adminUserInstanceDeactivated'), pytest.lazy_fixture('internalUserInstanceDeactivated'), pytest.lazy_fixture('regularUserInstanceDeactivated')], ids=['as_deactivated_admin_user', 'as_deactivated_internal_user', 'as_deactivated_regular_user'])
@pytest.mark.parametrize('userToDelete', [pytest.lazy_fixture('internal_user'), pytest.lazy_fixture('admin_user'), pytest.lazy_fixture('regular_user')], ids=['delete_admin_user', 'delete_internal_user', 'delete_regular_user'])
def test_deleting_user_deactivated(flask_app_client, loginAs: User, userToDelete: User):
    with flask_app_client.login(loginAs):
        response = flask_app_client.delete(f'/api/v1/users/{userToDelete.id}')
    assert401(response, userToDelete)