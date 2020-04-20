import pytest

from app.modules.bots.models import Bot
from app.modules.bots.schemas import DetailedBotSchema
from tests.params import labels, users
from tests.responseStatuses import assert422
from tests.utils import assert403, assertSuccess


path = '/api/v1/bots/'
baseData = {
    'app_name': 'newBot'
}

@pytest.mark.parametrize('loginAs', users, ids=labels)
@pytest.mark.parametrize('useRedditApp', [True, False])
@pytest.mark.parametrize('useSentryToken', [True, False])
@pytest.mark.parametrize('useDatabaseCredential', [True, False])
def test_creating_bot(flask_app_client, loginAs, redditApp, sentryToken, databaseCredential, useRedditApp, useSentryToken, useDatabaseCredential):
    data = {**baseData}
    redditApp.owner = loginAs
    sentryToken.owner = loginAs
    databaseCredential.owner = loginAs
    if useRedditApp:
        data['reddit_app_id'] = redditApp.id
    if useSentryToken:
        data['sentry_token_id'] = sentryToken.id
    if useDatabaseCredential:
        data['database_credential_id'] = databaseCredential.id
    response = flask_app_client.post(path, data=data)

    assertSuccess(response, loginAs, Bot, DetailedBotSchema)

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_creating_bot_with_owner(flask_app_client, loginAs, regular_user, redditApp, sentryToken, databaseCredential):
    response = flask_app_client.post(path, data={'owner_id': regular_user.id, 'reddit_app_id': redditApp.id, 'sentry_token_id': sentryToken.id, 'database_credential_id': databaseCredential.id, **baseData})

    if loginAs.is_admin or loginAs.is_internal:
        assertSuccess(response, regular_user, Bot, DetailedBotSchema)
    else:
        assert403(response, Bot, action='create')

def test_creating_bot_for_self(flask_app_client, regularUserInstance, redditApp, sentryToken, databaseCredential):
    redditApp.owner = regularUserInstance
    response = flask_app_client.post(path, data={'reddit_app_id': redditApp.id, 'sentry_token_id': sentryToken.id, 'database_credential_id': databaseCredential.id, **baseData})

    assertSuccess(response, regularUserInstance, Bot, DetailedBotSchema)

def test_creating_bot_for_self_with_owner(flask_app_client, regularUserInstance, redditApp, sentryToken, databaseCredential):
    redditApp.owner = regularUserInstance
    response = flask_app_client.post(path, data={'owner_id': regularUserInstance.id, 'reddit_app_id': redditApp.id, 'sentry_token_id': sentryToken.id, 'database_credential_id': databaseCredential.id, **baseData})

    assertSuccess(response, regularUserInstance, Bot, DetailedBotSchema)

def test_creating_bot_bad_name(flask_app_client, regularUserInstance, redditApp, sentryToken, databaseCredential):
    redditApp.owner = regularUserInstance
    response = flask_app_client.post(path, data={'reddit_app_id': redditApp.id, 'sentry_token_id': sentryToken.id, 'database_credential_id': databaseCredential.id, 'app_name': 'bo'})
    assert422(response)