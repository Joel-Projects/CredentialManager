import pytest


def assert401(response):
    assert response.status_code == 401
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}

def assert403(response):
    assert response.status_code == 403
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}

def assertPass(response):
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'id', 'username'}
    assert 'password' not in response.json.keys()

users = [
    pytest.lazy_fixture('adminUserInstance'),
    pytest.lazy_fixture('adminUserInstance2'),
    pytest.lazy_fixture('internalUserInstance'),
    pytest.lazy_fixture('internalUserInstance2'),
    pytest.lazy_fixture('regularUserInstance'),
    pytest.lazy_fixture('regularUserInstance2')
]
labels = [
    'login_as_deactivated_admin_user',
    'login_as_admin_user_2',
    'login_as_internal_user',
    'login_as_internal_user_2',
    'login_as_regular_user',
    'login_as_regular_user_2'
]

@pytest.mark.parametrize('loginAs', users, ids=labels)
@pytest.mark.parametrize('userToGet', [pytest.lazy_fixture('adminUserInstance'), pytest.lazy_fixture('internalUserInstance'), pytest.lazy_fixture('regularUserInstance')], ids=['as_admin_user', 'as_internal_user', 'as_regular_user'])
def test_getting_user(flask_app_client, loginAs, userToGet):
    response = flask_app_client.get(f'/api/v1/users/{userToGet.id}')

    if loginAs == userToGet:
        assertPass(response)
    elif userToGet.is_internal and loginAs.is_internal:
        assertPass(response)
    elif loginAs.is_admin or loginAs.is_internal:
        assertPass(response)
    else:
        assert403(response)

@pytest.mark.parametrize('loginAs', [pytest.lazy_fixture('adminUserInstanceDeactivated'), pytest.lazy_fixture('internalUserInstanceDeactivated'), pytest.lazy_fixture('regularUserInstanceDeactivated')], ids=['as_deactivated_admin_user', 'as_deactivated_internal_user', 'as_deactivated_regular_user'])
@pytest.mark.parametrize('userToGet', [pytest.lazy_fixture('internalUserInstance'), pytest.lazy_fixture('adminUserInstance'), pytest.lazy_fixture('regularUserInstance')], ids=['as_admin_user', 'as_internal_user', 'as_regular_user'])
def test_getting_user_deactivated(flask_app_client, loginAs, userToGet):
    with flask_app_client.login(loginAs):
        response = flask_app_client.delete(f'/api/v1/users/2')
    assert401(response)

def test_getting_list_of_users_by_unauthorized_user_must_fail(flask_app_client, regular_user):
    with flask_app_client.login(regular_user) as client:
        response = client.get('/api/v1/users/')

    assert response.status_code == 403
    assert response.content_type == 'application/json'
    assert set(response.json.keys()) >= {'status', 'message'}

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