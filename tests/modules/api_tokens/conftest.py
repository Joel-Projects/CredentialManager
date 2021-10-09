import pytest

from app.modules.api_tokens.models import ApiToken


@pytest.fixture()
def regular_user_api_token(temp_db_instance_helper, regular_user):
    for _ in temp_db_instance_helper(ApiToken(name="regular_api_token", owner_id=regular_user.id, token="token")):
        yield _


@pytest.fixture()
def admin_user_api_token(temp_db_instance_helper, admin_user):
    for _ in temp_db_instance_helper(ApiToken(name="admin_api_token", owner_id=admin_user.id, token="token")):
        yield _


@pytest.fixture()
def internal_user_api_token(temp_db_instance_helper, internal_user):
    for _ in temp_db_instance_helper(ApiToken(name="internal_api_token", owner_id=internal_user.id, token="token")):
        yield _
