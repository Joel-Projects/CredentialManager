import json
from datetime import datetime, timezone

import pytest

from app.modules.reddit_apps.models import RedditApp
from app.modules.reddit_apps.schemas import DetailedRedditAppSchema
from tests.params import labels, users
from tests.utils import assert403, assert409, assert422, assertSuccess

data = [
    {
        'op': 'replace',
        'path': '/app_name',
        'value': 'newName',
    },
    {
        'op': 'replace',
        'path': '/enabled',
        'value': False,
    }
]

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_modifying_reddit_app(flask_app_client, regularUserRedditApp, loginAs):
    response = flask_app_client.patch(f'/api/v1/reddit_apps/{regularUserRedditApp.id:d}', content_type='application/json', data=json.dumps(data))

    if loginAs.is_admin or loginAs.is_internal:
        assertSuccess(response, regularUserRedditApp.owner, RedditApp, DetailedRedditAppSchema)
    else:
        assert403(response, RedditApp, action='patch', internal=True, oldItem=regularUserRedditApp)

def test_modifying_reddit_app_by_self(flask_app_client, regularUserInstance, regularUserRedditApp):
    regularUserRedditApp.owner = regularUserInstance
    response = flask_app_client.patch(f'/api/v1/reddit_apps/{regularUserRedditApp.id}', content_type='application/json', data=json.dumps(data))
    assertSuccess(response, regularUserInstance, RedditApp, DetailedRedditAppSchema)

def test_modifying_reddit_app_info_with_invalid_format_must_fail(flask_app_client, regularUserInstance, regularUserRedditApp):
    regularUserRedditApp.owner = regularUserInstance
    response = flask_app_client.patch(f'/api/v1/reddit_apps/{regularUserInstance.id}', content_type='application/json', data=json.dumps([{'op': 'test', 'path': '/app_name', 'value': '', }, {'op': 'replace', 'path': '/enabled', }, ]))

    assert422(response, RedditApp, [('1', {'_schema': ['value is required']})], oldItem=regularUserRedditApp, action='patch')

def test_modifying_reddit_app_info_with_conflict_data_must_fail(flask_app_client, regularUserInstance, regularUserRedditApp, adminUserRedditApp):
    regularUserRedditApp.owner = regularUserInstance
    adminUserRedditApp.client_id = 'client_idOld'
    adminUserRedditApp.owner = regularUserInstance
    response = flask_app_client.patch(f'/api/v1/reddit_apps/{regularUserRedditApp.id}', content_type='application/json', data=json.dumps([{'op': 'replace', 'path': '/client_id', 'value': adminUserRedditApp.client_id}]))

    assert409(response, RedditApp, 'Failed to update Reddit App details.', loginAs=regularUserInstance, messageAttrs=[('1', {'_schema': ['value is required']})], oldItem=regularUserRedditApp, action='patch')