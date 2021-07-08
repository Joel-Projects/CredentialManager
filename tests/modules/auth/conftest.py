import pytest


@pytest.yield_fixture()
def regular_user_api_token(regular_user, temp_db_instance_helper):
    from app.modules.api_tokens.models import ApiToken

    token = ApiToken(name="test_token", token="token", owner_id=regular_user.id)
    for _ in temp_db_instance_helper(token):
        yield _


@pytest.fixture()
def regular_user_deactivated(regular_user):
    regular_user.is_active = False
    yield regular_user


@pytest.fixture()
def admin_user_deactivated(admin_user):
    admin_user.is_active = False
    yield admin_user


@pytest.fixture()
def internal_user_deactivated(internal_user):
    internal_user.is_active = False
    yield internal_user
