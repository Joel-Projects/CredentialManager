import pytest

from app.modules.users.models import User
from app.modules.users.schemas import DetailedUserSchema
from tests.utils import assertSuccess, assert401 ,assert403


users = [
    pytest.lazy_fixture('adminUserInstance'),
    pytest.lazy_fixture('adminUserInstance2'),
    pytest.lazy_fixture('internalUserInstance'),
    pytest.lazy_fixture('internalUserInstance2'),
    pytest.lazy_fixture('regularUserInstance'),
    pytest.lazy_fixture('regularUserInstance2')
]
labels = [
    'login_as_admin_user',
    'login_as_admin_user_2',
    'login_as_internal_user',
    'login_as_internal_user_2',
    'login_as_regular_user',
    'login_as_regular_user_2'
]

@pytest.mark.parametrize('loginAs', users, ids=labels)
@pytest.mark.parametrize('userToGet', [pytest.lazy_fixture('admin_user'), pytest.lazy_fixture('internal_user'), pytest.lazy_fixture('regular_user')], ids=['get_admin_user', 'get_internal_user', 'get_regular_user'])
def test_getting_user(flask_app_client, loginAs, userToGet):
    response = flask_app_client.get(f'/api/v1/users/{userToGet.id}')

    if loginAs == userToGet:
        assertSuccess(response, None, User, DetailedUserSchema)
    elif userToGet.is_internal:
        if loginAs.is_internal:
            assertSuccess(response, None, User, DetailedUserSchema)
        elif loginAs.is_admin:
            assert403(response, User, created=False, internal=True)
        else:
            assert403(response, User, created=False, internal=True)
    elif loginAs.is_admin or loginAs.is_internal:
        assertSuccess(response, None, User, DetailedUserSchema)
    else:
        assert403(response, User, created=False, internal=True)

@pytest.mark.parametrize('loginAs', [pytest.lazy_fixture('admin_user_deactivated'), pytest.lazy_fixture('internal_user_deactivated'), pytest.lazy_fixture('regular_user_deactivated')], ids=['as_deactivated_admin_user', 'as_deactivated_internal_user', 'as_deactivated_regular_user'])
@pytest.mark.parametrize('userToGet', [pytest.lazy_fixture('internal_user2'), pytest.lazy_fixture('admin_user2'), pytest.lazy_fixture('regular_user2')], ids=['get_admin_user', 'get_internal_user', 'get_regular_user'])
def test_getting_user_deactivated(flask_app_client, loginAs, userToGet):
    with flask_app_client.login(loginAs):
        response = flask_app_client.get(f'/api/v1/users/{userToGet.id}')
    assert401(response, User, loginAs=loginAs, created=False)

def test_getting_list_of_users_by_unauthorized_user_must_fail(flask_app_client, regular_user):
    with flask_app_client.login(regular_user) as client:
        response = client.get('/api/v1/users/')

    assert403(response, User, loginAs=regular_user, created=False, internal=True)

def test_getting_list_of_users_by_authorized_user(flask_app_client, admin_user):
    with flask_app_client.login(admin_user) as client:
        response = client.get('/api/v1/users/')

    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert isinstance(response.json, list)
    assert set(response.json[0].keys()) >= {'id', 'username'}

def test_getting_user_me_info(flask_app_client, regular_user):
    with flask_app_client.login(regular_user):
        response = flask_app_client.get('/api/v1/users/me')

    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'id', 'username'}
    assert 'password' not in response.json.keys()