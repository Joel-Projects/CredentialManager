import pytest

from flask_login import current_user, login_user, logout_user

from tests import utils


@pytest.fixture()
def userInstance(patch_user_password_scheme, temp_db_instance_helper):
    for _userInstance in temp_db_instance_helper(utils.generateUserInstance(username='username', password='password')):
        user_id = _userInstance.id
        _userInstance.get_id = lambda: user_id
        return _userInstance

@pytest.fixture()
def userInstanceDeactivated(patch_user_password_scheme, temp_db_instance_helper):
    for _userInstance in temp_db_instance_helper(utils.generateUserInstance(username='usernameDeactivated', password='password', is_active=False)):
        user_id = _userInstance.id
        _userInstance.get_id = lambda: user_id
        return _userInstance

@pytest.yield_fixture()
def regularUserInstance(flask_app, userInstance):
    with flask_app.test_request_context('/'):
        login_user(userInstance)
        yield current_user
        logout_user()

@pytest.yield_fixture()
def adminUserInstance(flask_app, userInstance):
    with flask_app.test_request_context('/'):
        login_user(userInstance)
        current_user.is_admin = True
        yield current_user
        logout_user()

@pytest.yield_fixture()
def internalUserInstance(flask_app, userInstance):
    with flask_app.test_request_context('/'):
        login_user(userInstance)
        current_user.is_internal = True
        yield current_user
        logout_user()

@pytest.yield_fixture()
def anonymousUserInstance(flask_app):
    with flask_app.test_request_context('/'):
        yield current_user

@pytest.yield_fixture()
def regularUserInstance2(flask_app, userInstance):
    with flask_app.test_request_context('/'):
        login_user(userInstance)
        yield current_user
        logout_user()

@pytest.yield_fixture()
def adminUserInstance2(flask_app, userInstance):
    with flask_app.test_request_context('/'):
        login_user(userInstance)
        current_user.is_admin = True
        yield current_user
        logout_user()

@pytest.yield_fixture()
def internalUserInstance2(flask_app, userInstance):
    with flask_app.test_request_context('/'):
        login_user(userInstance)
        current_user.is_internal = True
        yield current_user
        logout_user()

@pytest.yield_fixture()
def regularUserInstanceDeactivated(userInstanceDeactivated):
    yield userInstanceDeactivated

@pytest.yield_fixture()
def adminUserInstanceDeactivated(userInstanceDeactivated):
    userInstanceDeactivated.is_admin = True
    yield userInstanceDeactivated

@pytest.yield_fixture()
def internalUserInstanceDeactivated(userInstanceDeactivated):
    userInstanceDeactivated.is_internal = True
    yield userInstanceDeactivated
