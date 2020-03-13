from datetime import datetime, timezone

import pytest

from app.modules.users.models import User
from app.modules.users.schemas import DetailedUserSchema
from tests.utils import assertSuccess, assert403, assert401, assert409


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

# noinspection PyUnresolvedReferences
@pytest.mark.parametrize('is_active', [True, False], ids=['is_active', 'is_not_active'])
@pytest.mark.parametrize('is_internal,is_admin,is_regular_user', [(True, False, False), (False, True, True), (False, False, True)], ids=['internal_user', 'admin_user', 'regular_user'])
@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_creating_user(flask_app_client, is_internal, is_admin, is_regular_user, is_active, loginAs: User):
    response = flask_app_client.post('/api/v1/users/', data={'username': 'testUsername', 'password': 'testPassword', 'is_internal': is_internal, 'is_admin': is_admin, 'is_regular_user': is_regular_user, 'is_active': is_active})

    if is_internal:
        if loginAs.is_internal:
            assertSuccess(response, None, User, DetailedUserSchema)
        elif loginAs.is_admin:
            assert403(response, User, loginAs=loginAs, internal=True)
        else:
            assert403(response, User, loginAs=loginAs, internal=True)
    elif loginAs.is_admin or loginAs.is_internal:
        assertSuccess(response, None, User, DetailedUserSchema)
    else:
        assert403(response, User, loginAs=loginAs, internal=True)

@pytest.mark.parametrize('is_active', [True, False], ids=['is_active', 'is_not_active'])
@pytest.mark.parametrize('is_internal,is_admin,is_regular_user', [(True, False, False), (False, True, True), (False, False, True)], ids=['internal_user', 'admin_user', 'regular_user'])
@pytest.mark.parametrize('loginAs', [pytest.lazy_fixture('adminUserInstanceDeactivated'), pytest.lazy_fixture('internalUserInstanceDeactivated'), pytest.lazy_fixture('regularUserInstanceDeactivated')], ids=['as_deactivated_admin_user', 'as_deactivated_internal_user', 'as_deactivated_regular_user'])
def test_creating_user_as_deactivated(flask_app_client, is_internal, is_admin, is_regular_user, is_active, loginAs: User):
    with flask_app_client.login(loginAs):
        response = flask_app_client.post('/api/v1/users/', data={'username': 'testUsername', 'password': 'testPassword', 'is_internal': is_internal, 'is_admin': is_admin, 'is_regular_user': is_regular_user, 'is_active': is_active})
    assert401(response, User, loginAs=loginAs)

def test_creating_conflict_user(flask_app_client, admin_user):
    with flask_app_client.login(admin_user):
        response = flask_app_client.post('/api/v1/users/', data={'username': 'admin_user', 'password': 'testPassword'})
        assert409(response, User, 'Failed to create a new user.', loginAs=admin_user)