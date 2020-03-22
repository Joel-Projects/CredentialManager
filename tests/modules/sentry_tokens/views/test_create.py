import pytest

from app.modules.sentry_tokens.models import SentryToken
from tests.params import labels, users
from tests.responseStatuses import assert201, assert422
from tests.utils import assertRenderedTemplate, captured_templates
from . import assert403Create


@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_create_sentry_token(flask_app_client, loginAs):
    with captured_templates(flask_app_client.application) as templates:
        data = {'dsn': 'https://1234asdf@sentry.jesassn.org/1', 'app_name': 'sentry_token'}
        response = flask_app_client.post('/sentry_tokens', content_type='application/x-www-form-urlencoded', data=data)
        assert201(response)
        assertRenderedTemplate(templates, 'sentry_tokens.html')
        sentryToken = SentryToken.query.filter_by(app_name='sentry_token').first()
        assert sentryToken is not None

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_create_sentry_token_profile(flask_app_client, loginAs):
    with captured_templates(flask_app_client.application) as templates:
        data = {'dsn': 'https://1234asdf@sentry.jesassn.org/1', 'app_name': 'sentry_token'}
        response = flask_app_client.post(f'/profile/sentry_tokens', content_type='application/x-www-form-urlencoded', data=data)
        assert201(response)
        assertRenderedTemplate(templates, 'sentry_tokens.html')
        sentryToken = SentryToken.query.filter_by(app_name='sentry_token').first()
        assert sentryToken is not None

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_create_otherUserSentryToken(flask_app_client, loginAs, regular_user):
    with captured_templates(flask_app_client.application) as templates:
        data = {'dsn': 'https://1234asdf@sentry.jesassn.org/1', 'app_name': 'sentry_token', 'owner': regular_user.id}
        response = flask_app_client.post('/sentry_tokens', content_type='application/x-www-form-urlencoded', data=data)
        if loginAs.is_admin or loginAs.is_internal:
            assert201(response)
            assertRenderedTemplate(templates, 'sentry_tokens.html')
            sentryToken = SentryToken.query.filter_by(app_name='sentry_token').first()
            assert sentryToken is not None
            assert sentryToken.id == 1
            assert sentryToken.dsn == 'https://1234asdf@sentry.jesassn.org/1'
            assert sentryToken.owner == regular_user
        else:
            assert403Create(response, templates)
            sentryToken = SentryToken.query.filter_by(app_name='sentry_token').first()
            assert sentryToken is None

def test_create_sentry_token_bad_params(flask_app_client, regularUserInstance):
    with captured_templates(flask_app_client.application) as templates:
        data = {'dsn': 'invalid_url', 'app_name': 'sentry_token'}
        response = flask_app_client.post('/sentry_tokens', content_type='application/x-www-form-urlencoded', data=data)
        assert422(response)
        sentryToken = SentryToken.query.filter_by(app_name='sentry_token').first()
        assert sentryToken is None

def test_create_sentry_token_bad_params_profile(flask_app_client, regularUserInstance):
    with captured_templates(flask_app_client.application) as templates:
        data = {'dsn': 'invalid_url', 'app_name': 'sentry_token'}
        response = flask_app_client.post('/profile/sentry_tokens', content_type='application/x-www-form-urlencoded', data=data)
        assert422(response)
        sentryToken = SentryToken.query.filter_by(app_name='sentry_token').first()
        assert sentryToken is None