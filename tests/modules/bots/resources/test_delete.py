import pytest

from app.modules.bots.models import Bot
from tests.params import labels, users
from tests.utils import assert403, assertSuccess


tokensToDelete = [
    pytest.lazy_fixture('adminUserBot'),
    pytest.lazy_fixture('internalUserBot'),
    pytest.lazy_fixture('regularUserBot')
]

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_deleting_user(flask_app_client, loginAs, regularUserBot):
    response = flask_app_client.delete(f'/api/v1/bots/{regularUserBot.id}')

    if loginAs.is_admin or loginAs.is_internal:
        assertSuccess(response, None, Bot, None, deleteItemId=regularUserBot.id)
    else:
        assert403(response, Bot, oldItem=regularUserBot, internal=True, action='deleted')

def test_deleting_self(flask_app_client, adminUserInstance, regularUserBot):
    response = flask_app_client.delete(f'/api/v1/bots/{regularUserBot.id}')
    assertSuccess(response, None, Bot, None, deleteItemId=regularUserBot.id)