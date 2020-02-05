import pytest


@pytest.yield_fixture()
def regularUserApiToken(temp_db_instance_helper, regular_user):
    from app.modules.api_tokens.models import ApiToken

    for _ in temp_db_instance_helper(ApiToken(name='tokenName', owner_id=regular_user.id, token='token')):
        yield _

@pytest.yield_fixture()
def adminUserApiToken(temp_db_instance_helper, admin_user):
    from app.modules.api_tokens.models import ApiToken

    for _ in temp_db_instance_helper(ApiToken(name='tokenName', owner_id=admin_user.id, token='token')):
        yield _

@pytest.yield_fixture()
def internalUserApiToken(temp_db_instance_helper, internal_user):
    from app.modules.api_tokens.models import ApiToken

    for _ in temp_db_instance_helper(ApiToken(name='tokenName', owner_id=internal_user.id, token='token')):
        yield _
