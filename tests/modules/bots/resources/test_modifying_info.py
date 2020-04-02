import json

import pytest

from app.modules.bots.models import Bot
from app.modules.bots.schemas import DetailedBotSchema
from tests.params import labels, users
from tests.utils import assert403, assert409, assert422, assertSuccess


data = [
    {
        'op': 'replace',
        'path': '/app_name',
        'value': 'newAppName',
    },
    {
        'op': 'replace',
        'path': '/enabled',
        'value': False,
    }
]

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_modifying_bot(flask_app_client, regularUserBot, loginAs):
    response = flask_app_client.patch(f'/api/v1/bots/{regularUserBot.id}', content_type='application/json', data=json.dumps(data))

    if loginAs.is_admin or loginAs.is_internal:
        assertSuccess(response, regularUserBot.owner, Bot, DetailedBotSchema)
    else:
        assert403(response, Bot, action='patch', internal=True, oldItem=regularUserBot)

def test_modifying_bot_by_self(flask_app_client, regularUserInstance, regularUserBot):
    regularUserBot.owner = regularUserInstance
    response = flask_app_client.patch(f'/api/v1/bots/{regularUserBot.id}', content_type='application/json', data=json.dumps(data))
    assertSuccess(response, regularUserInstance, Bot, DetailedBotSchema)

def test_modifying_bot_info_with_invalid_format_must_fail(flask_app_client, regularUserInstance, regularUserBot):
    regularUserBot.owner = regularUserInstance
    response = flask_app_client.patch(f'/api/v1/bots/{regularUserBot.id}', content_type='application/json', data=json.dumps([{'op': 'test', 'path': '/app_name', 'value': '', }, {'op': 'replace', 'path': '/enabled', }, ]))

    assert422(response, Bot, [('1', {'_schema': ['value is required']})], oldItem=regularUserBot, action='patch')

def test_modifying_bot_info_with_conflict_data_must_fail(flask_app_client, regularUserInstance, regularUserBot, adminUserBot):
    regularUserBot.owner = regularUserInstance
    adminUserBot.app_name = 'app_nameOld'
    adminUserBot.owner = regularUserInstance
    response = flask_app_client.patch(f'/api/v1/bots/{regularUserBot.id}', content_type='application/json', data=json.dumps([{'op': 'replace', 'path': '/app_name', 'value': adminUserBot.app_name}]))

    assert409(response, Bot, 'Failed to update Bot details.', loginAs=regularUserInstance, messageAttrs=[('1', {'_schema': ['value is required']})], oldItem=regularUserBot, action='patch')