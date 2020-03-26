import pytest

from app.modules.reddit_apps.models import RedditApp
from tests.params import labels, users
from tests.responseStatuses import assert201, assert422
from tests.utils import assertCreated, assertRenderedTemplate, captured_templates
from . import assert403Create

data = {
    'app_name': 'reddit_app',
    'client_id': 'client_id',
    'client_secret': 'client_secret',
    'user_agent': 'user_agent',
    'app_type': 'web',
}

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_create_reddit_app(flask_app_client, loginAs):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post('/reddit_apps', content_type='application/x-www-form-urlencoded', data=data)
        assert201(response)
        assertRenderedTemplate(templates, 'reddit_apps.html')
        redditApp = RedditApp.query.filter_by(app_name='reddit_app').first()
        assertCreated(redditApp, data)

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_create_reddit_app_profile(flask_app_client, loginAs):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(f'/profile/reddit_apps', content_type='application/x-www-form-urlencoded', data=data)
        assert201(response)
        assertRenderedTemplate(templates, 'reddit_apps.html')
        redditApp = RedditApp.query.filter_by(app_name='reddit_app').first()
        assertCreated(redditApp, data)

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_create_other_user_reddit_app(flask_app_client, loginAs, regular_user):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post('/reddit_apps', content_type='application/x-www-form-urlencoded', data={'owner': regular_user.id, **data})
        if loginAs.is_admin or loginAs.is_internal:
            assert201(response)
            assertRenderedTemplate(templates, 'reddit_apps.html')
            redditApp = RedditApp.query.filter_by(app_name='reddit_app').first()
            assertCreated(redditApp, data)
            assert redditApp.owner == regular_user
        else:
            assert403Create(response, templates)
            redditApp = RedditApp.query.filter_by(app_name='reddit_app').first()
            assert redditApp is None

def test_create_reddit_app_bad_params(flask_app_client, regularUserInstance):
    with captured_templates(flask_app_client.application) as templates:
        data = {'dsn': 'invalid_url', 'app_name': 'reddit_app'}
        response = flask_app_client.post('/reddit_apps', content_type='application/x-www-form-urlencoded', data=data)
        assert response.status_code == 200
        assert response.mimetype == 'application/json'
        redditApp = RedditApp.query.filter_by(app_name='reddit_app').first()
        assert redditApp is None

def test_create_reddit_app_bad_params_profile(flask_app_client, regularUserInstance):
    with captured_templates(flask_app_client.application) as templates:
        data = {'dsn': 'invalid_url', 'app_name': 'reddit_app'}
        response = flask_app_client.post('/profile/reddit_apps', content_type='application/x-www-form-urlencoded', data=data)
        assert422(response)
        redditApp = RedditApp.query.filter_by(app_name='reddit_app').first()
        assert redditApp is None