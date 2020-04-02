import pytest

from app.modules.bots.models import Bot
from tests.params import labels, users
from tests.responseStatuses import assert201, assert403Create, assert422
from tests.utils import assertCreated, assertRenderedTemplate, captured_templates


data = {
    'app_name': 'bot',
    'reddit_app': '1',
    'sentry_token': '1',
    'database_credential': '1'
}

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_create_bot(flask_app_client, loginAs, redditApp, sentryToken, databaseCredential):
    with captured_templates(flask_app_client.application) as templates:
        redditApp.owner = loginAs
        sentryToken.owner = loginAs
        databaseCredential.owner = loginAs
        response = flask_app_client.post('/bots', content_type='application/x-www-form-urlencoded', data=data)
        assert201(response)
        assertRenderedTemplate(templates, 'bots.html')
        bot = Bot.query.filter_by(app_name='bot').first()
        assertCreated(bot, data)

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_create_bot_profile(flask_app_client, loginAs, redditApp, sentryToken, databaseCredential):
    with captured_templates(flask_app_client.application) as templates:
        redditApp.owner = loginAs
        sentryToken.owner = loginAs
        databaseCredential.owner = loginAs
        response = flask_app_client.post(f'/profile/bots', content_type='application/x-www-form-urlencoded', data=data)
        assert201(response)
        assertRenderedTemplate(templates, 'bots.html')
        bot = Bot.query.filter_by(app_name='bot').first()
        assertCreated(bot, data)

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_create_bot_other_user(flask_app_client, loginAs, regular_user, redditApp, sentryToken, databaseCredential):
    with captured_templates(flask_app_client.application) as templates:
        if not (loginAs.is_admin and loginAs.is_internal):
            redditApp.owner = loginAs
            sentryToken.owner = loginAs
            databaseCredential.owner = loginAs
        response = flask_app_client.post('/bots', content_type='application/x-www-form-urlencoded', data={'owner': str(regular_user.id), 'reddit_app': str(redditApp.id), **data})
        if loginAs.is_admin or loginAs.is_internal:
            assert201(response)
            assertRenderedTemplate(templates, 'bots.html')
            bot = Bot.query.filter_by(app_name='bot').first()
            assertCreated(bot, data)
            assert bot.owner == regular_user
        else:
            assert403Create(response)
            bot = Bot.query.filter_by(app_name='bot').first()
            assert bot is None

def test_create_bot_bad_params(flask_app_client, regularUserInstance):
    response = flask_app_client.post('/bots', content_type='application/x-www-form-urlencoded', data={'app_name': 'bo', **data})
    assert response.status_code == 200
    assert response.mimetype == 'application/json'
    bot = Bot.query.filter_by(app_name='bot').first()
    assert bot is None