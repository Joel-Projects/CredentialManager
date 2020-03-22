import pytest

from app.modules.api_tokens.models import ApiToken


@pytest.fixture()
def regularUserApiToken(temp_db_instance_helper, regular_user):
    for _ in temp_db_instance_helper(ApiToken(name='regularApiToken', owner_id=regular_user.id, token='token')):
        yield _

@pytest.fixture()
def adminUserApiToken(temp_db_instance_helper, admin_user):
    for _ in temp_db_instance_helper(ApiToken(name='adminApiToken', owner_id=admin_user.id, token='token')):
        yield _

@pytest.fixture()
def internalUserApiToken(temp_db_instance_helper, internal_user):
    for _ in temp_db_instance_helper(ApiToken(name='internalApiToken', owner_id=internal_user.id, token='token')):
        yield _