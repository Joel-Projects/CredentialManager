import pytest

from tests import utils


@pytest.fixture()
def user_instance_deactivated(patch_user_password_scheme, temp_db_instance_helper):
    for _user_instance in temp_db_instance_helper(
        utils.generate_user_instance(
            username="username_deactivated", password="password", is_active=False
        )
    ):
        user_id = _user_instance.id
        _user_instance.get_id = lambda: user_id
        return _user_instance


@pytest.fixture()
def regular_user_instance_deactivated(user_instance_deactivated):
    yield user_instance_deactivated


@pytest.fixture()
def admin_user_instance_deactivated(user_instance_deactivated):
    user_instance_deactivated.is_admin = True
    yield user_instance_deactivated


@pytest.fixture()
def internal_user_instance_deactivated(user_instance_deactivated):
    user_instance_deactivated.is_internal = True
    yield user_instance_deactivated
