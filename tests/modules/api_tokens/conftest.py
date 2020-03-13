import pytest
from app.modules.api_tokens.models import ApiToken

#
# @pytest.yield_fixture(params=[pytest.lazy_fixture('internalUserInstance'), pytest.lazy_fixture('adminUserInstance'), pytest.lazy_fixture('regularUserInstance')])
# def apiTokenWithOwner(request, temp_db_instance_helper):
#     for _ in temp_db_instance_helper(ApiToken(name='tokenName', owner_id=request.param.id, token='token')):
#         yield _

@pytest.yield_fixture()
def regularUserApiToken(temp_db_instance_helper, regular_user):
    for _ in temp_db_instance_helper(ApiToken(name='tokenName', owner_id=regular_user.id, token='token')):
        yield _

@pytest.yield_fixture()
def adminUserApiToken(temp_db_instance_helper, admin_user):
    for _ in temp_db_instance_helper(ApiToken(name='tokenName', owner_id=admin_user.id, token='token')):
        yield _

@pytest.yield_fixture()
def internalUserApiToken(temp_db_instance_helper, internal_user):
    for _ in temp_db_instance_helper(ApiToken(name='tokenName', owner_id=internal_user.id, token='token')):
        yield _