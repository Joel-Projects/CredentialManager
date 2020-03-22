import pytest

from tests import utils


@pytest.fixture()
def userInstanceDeactivated(patch_user_password_scheme, temp_db_instance_helper):
    for _userInstance in temp_db_instance_helper(utils.generateUserInstance(username='usernameDeactivated', password='password', is_active=False)): # pragma: no branch
        user_id = _userInstance.id
        _userInstance.get_id = lambda: user_id # pragma: no branch
        return _userInstance

@pytest.fixture()
def regularUserInstanceDeactivated(userInstanceDeactivated):
    yield userInstanceDeactivated

@pytest.fixture()
def adminUserInstanceDeactivated(userInstanceDeactivated):
    userInstanceDeactivated.is_admin = True
    yield userInstanceDeactivated

@pytest.fixture()
def internalUserInstanceDeactivated(userInstanceDeactivated):
    userInstanceDeactivated.is_internal = True
    yield userInstanceDeactivated # pragma: no cover