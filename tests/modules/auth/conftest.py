# encoding: utf-8
import datetime
import pytest


@pytest.yield_fixture()
def regularUserApiToken(regular_user, temp_db_instance_helper):

    from app.modules.api_tokens.models import ApiToken
    token = ApiToken(name='testToken', token='token', owner_id=regular_user.id)
    for _ in temp_db_instance_helper(token):
        yield _
