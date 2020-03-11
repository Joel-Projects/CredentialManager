import pytest
from flask_login import current_user
from datetime import datetime, timezone

from app.modules.users.models import User


def assertSuccess(response):
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'created', 'default_settings', 'id', 'is_active', 'is_admin', 'is_regular_user', 'updated', 'username'}
    assert isinstance(response.json['created'], str)
    assert isinstance(response.json['default_settings'], dict)
    assert isinstance(response.json['id'], int)
    assert isinstance(response.json['is_active'], bool)
    assert isinstance(response.json['is_admin'], bool)
    assert isinstance(response.json['is_regular_user'], bool)
    assert isinstance(response.json['updated'], str)

    createdUser = User.query.get(response.json['id'])
    assert createdUser is not None

    for key, value in response.json.items():
        if key in ['created', 'updated']:
            assert value == datetime.astimezone(getattr(createdUser, key), timezone.utc).isoformat()
        else:
            assert value == getattr(createdUser, key)

def assertFail(response, loginAs):
    assert response.status_code == 403
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}
    assert response.json['message'] == "You don't have the permission to access the requested resource."

    from app.modules.users.models import User

    createdUser = User.query.filter(User.id != loginAs.id).first()
    assert createdUser is None

def assertInactive(response, loginAs):
    assert response.status_code == 401
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}
    assert response.json['message'] == "The server could not verify that you are authorized to access the URL requested. You either supplied the wrong credentials (e.g. a bad password), or your browser doesn't understand how to supply the credentials required."

    from app.modules.users.models import User

    createdUser = User.query.filter(User.id != loginAs.id).first()
    assert createdUser is None

# noinspection PyUnresolvedReferences
@pytest.mark.parametrize('is_active', [True, False], ids=['is_active', 'is_not_active'])
@pytest.mark.parametrize('is_internal,is_admin,is_regular_user', [(True, False, False), (False, True, True), (False, False, True)], ids=['internal_user', 'admin_user', 'regular_user'])
@pytest.mark.parametrize('loginAs', [pytest.lazy_fixture('admin_user'), pytest.lazy_fixture('deactivated_admin_user'), pytest.lazy_fixture('internal_user'), pytest.lazy_fixture('regular_user')], ids=['as_admin_user', 'as_deactivated_admin_user', 'as_internal_user', 'as_regular_user'])
def test_creating_user(flask_app_client, is_internal, is_admin, is_regular_user, is_active, loginAs: User):
    with flask_app_client.login(loginAs):
        response = flask_app_client.post('/api/v1/users/', data={'username': 'testUsername', 'password': 'testPassword', 'is_internal': is_internal, 'is_admin': is_admin, 'is_regular_user': is_regular_user, 'is_active': is_active})

    if not loginAs.is_active:
        assertInactive(response, loginAs)
    elif is_internal:
        if loginAs.is_internal:
            assertSuccess(response)
        else:
            assertFail(response, loginAs)
    elif loginAs.is_admin or loginAs.is_internal:
        assertSuccess(response)
    else:
        assertFail(response, loginAs)

def test_creating_conflict_user(flask_app_client, admin_user):
    with flask_app_client.login(admin_user):
        response = flask_app_client.post('/api/v1/users/', data={'username': 'admin_user', 'password': 'testPassword'})

        assert response.status_code == 409
        assert response.content_type == 'application/json'
        assert isinstance(response.json, dict)
        assert set(response.json.keys()) >= {'status', 'message'}
        assert response.json['message'] == 'Failed to create a new user.'

        from app.modules.users.models import User

        createdUser = User.query.filter(User.id != admin_user.id).first()
        assert createdUser is None