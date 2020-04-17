import pytest

from app.modules.users.models import User
from app.modules.users.schemas import DetailedUserSchema
from tests.params import labels, users
from tests.utils import assert401, assert403, assertSuccess


@pytest.mark.parametrize('loginAs', users, ids=labels)
@pytest.mark.parametrize('userToGet', [pytest.lazy_fixture('admin_user'), pytest.lazy_fixture('internal_user'), pytest.lazy_fixture('regular_user')], ids=['get_admin_user', 'get_internal_user', 'get_regular_user'])
def test_getting_user(flask_app_client, loginAs, userToGet):
    response = flask_app_client.get(f'/api/v1/users/{userToGet.id}')

    if userToGet.is_internal:
        if loginAs.is_internal:
            assertSuccess(response, None, User, DetailedUserSchema)
        elif loginAs.is_admin:
            assert403(response, User, internal=True)
        else:
            assert403(response, User, internal=True)
    elif loginAs.is_admin or loginAs.is_internal:
        assertSuccess(response, None, User, DetailedUserSchema)
    else:
        assert403(response, User, internal=True)

@pytest.mark.parametrize('loginAs', users, ids=labels)
@pytest.mark.parametrize('userToGet', [pytest.lazy_fixture('admin_user'), pytest.lazy_fixture('internal_user'), pytest.lazy_fixture('regular_user')], ids=['get_admin_user', 'get_internal_user', 'get_regular_user'])
def test_getting_user(flask_app_client, loginAs, userToGet):
    response = flask_app_client.post(f'/api/v1/users/by_name', data={'username': userToGet.username})

    if userToGet.is_internal:
        if loginAs.is_internal:
            assertSuccess(response, None, User, DetailedUserSchema)
        elif loginAs.is_admin:
            assert403(response, User, internal=True)
        else:
            assert403(response, User, internal=True)
    elif loginAs.is_admin or loginAs.is_internal:
        assertSuccess(response, None, User, DetailedUserSchema)
    else:
        assert403(response, User, internal=True)

@pytest.mark.parametrize('loginAs', [pytest.lazy_fixture('adminUserInstanceDeactivated'), pytest.lazy_fixture('internalUserInstanceDeactivated'), pytest.lazy_fixture('regularUserInstanceDeactivated')], ids=['as_deactivated_admin_user', 'as_deactivated_internal_user', 'as_deactivated_regular_user'])
@pytest.mark.parametrize('userToGet', [pytest.lazy_fixture('internal_user'), pytest.lazy_fixture('admin_user'), pytest.lazy_fixture('regular_user')], ids=['get_admin_user', 'get_internal_user', 'get_regular_user'])
def test_getting_user_deactivated(flask_app_client, loginAs, userToGet):
    with flask_app_client.login(loginAs):
        response = flask_app_client.get(f'/api/v1/users/{userToGet.id}')
    assert401(response, User, loginAs=loginAs, action='None')

def test_getting_list_of_users_by_unauthorized_user_must_fail(flask_app_client, regularUserInstance):
    response = flask_app_client.get('/api/v1/users/')
    assert403(response, User, loginAs=regularUserInstance, internal=True)

def test_getting_list_of_users_by_authorized_user(flask_app_client, adminUserInstance):
    response = flask_app_client.get('/api/v1/users/')

    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert isinstance(response.json, list)
    assert set(response.json[0].keys()) >= {'id', 'username'}

def test_getting_user_me_info(flask_app_client, regularUserInstance):
    response = flask_app_client.get('/api/v1/users/me')

    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'id', 'username'}
    assert 'password' not in response.json.keys()

def test_getting_user_apps(flask_app_client, regularUserInstance):
    response = flask_app_client.get(f'/api/v1/users/{regularUserInstance.id}/apps')

    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'id', 'username', 'reddit_apps', 'sentry_tokens', 'database_credentials'}
    assert isinstance(response.json['reddit_apps'], list)
    assert isinstance(response.json['sentry_tokens'], list)
    assert isinstance(response.json['database_credentials'], list)