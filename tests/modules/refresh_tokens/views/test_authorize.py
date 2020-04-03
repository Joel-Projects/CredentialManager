import pytest

from app.modules.refresh_tokens.models import RefreshToken
from tests.utils import assertRenderedTemplate, captured_templates


def test_authorize(db, flask_app_client, redditApp, mocker, reddit, recorder):
    redditApp.client_id = pytest.placeholders.client_id
    redditApp.client_secret = pytest.placeholders.client_secret
    redditApp.redirect_uri = pytest.placeholders.redirect_uri
    redditApp.user_agent = pytest.placeholders.user_agent
    db.session.merge(redditApp)
    mocker.patch('app.modules.reddit_apps.models.RedditApp.redditInstance', new_callable=mocker.PropertyMock, return_value=reddit)
    with recorder.use_cassette("RefreshTokens.test_authorize"):
        with captured_templates(flask_app_client.application) as templates:
            url = f'/oauth2/reddit_callback?state={redditApp.state}&code={pytest.placeholders.auth_code}'
            response = flask_app_client.get(url)
            assert response.content_type == 'text/html; charset=utf-8'
            assert response.status_code == 200
            assertRenderedTemplate(templates, 'oauth_result.html')
            newToken = RefreshToken.query.first()
            assert newToken.redditor == templates['templates'][0][1]['user']
            assert templates['templates'][0][1]['user'] == 'Lil_SpazJoekp'
            assert templates['templates'][0][1]['header'] == 'Reddit Authorization Complete'
            assert templates['templates'][0][1]['success']

def test_authorize_temp(db, flask_app_client, redditApp, mocker, reddit, recorder):
    redditApp.client_id = pytest.placeholders.client_id
    redditApp.client_secret = pytest.placeholders.client_secret
    redditApp.redirect_uri = pytest.placeholders.redirect_uri
    redditApp.user_agent = pytest.placeholders.user_agent
    db.session.merge(redditApp)
    mocker.patch('app.modules.reddit_apps.models.RedditApp.redditInstance', new_callable=mocker.PropertyMock, return_value=reddit)
    with recorder.use_cassette("RefreshTokens.test_authorize_temp"):
        with captured_templates(flask_app_client.application) as templates:
            url = f'/oauth2/reddit_callback?state={redditApp.state}&code={pytest.placeholders.auth_code}'
            response = flask_app_client.get(url)
            assert response.content_type == 'text/html; charset=utf-8'
            assert response.status_code == 200
            assertRenderedTemplate(templates, 'oauth_result.html')
            newToken = RefreshToken.query.first()
            assert newToken is None
            assert templates['templates'][0][1]['user'] == 'Lil_SpazJoekp'
            assert templates['templates'][0][1]['header'] == 'Reddit Verification Complete'
            assert templates['templates'][0][1]['success']

def test_authorize_exisiting(db, flask_app_client, redditApp, mocker, reddit, recorder, regularUserRefreshToken):
    redditApp.client_id = pytest.placeholders.client_id
    redditApp.client_secret = pytest.placeholders.client_secret
    redditApp.redirect_uri = pytest.placeholders.redirect_uri
    redditApp.user_agent = pytest.placeholders.user_agent
    db.session.merge(redditApp)
    mocker.patch('app.modules.reddit_apps.models.RedditApp.redditInstance', new_callable=mocker.PropertyMock, return_value=reddit)
    with recorder.use_cassette("RefreshTokens.test_authorize"):
        with captured_templates(flask_app_client.application) as templates:
            url = f'/oauth2/reddit_callback?state={redditApp.state}&code={pytest.placeholders.auth_code}'
            response = flask_app_client.get(url)
            assert response.content_type == 'text/html; charset=utf-8'
            assert response.status_code == 200
            assertRenderedTemplate(templates, 'oauth_result.html')
            newToken = RefreshToken.query.filter_by(redditor='Lil_SpazJoekp').first()
            assert newToken.redditor == templates['templates'][0][1]['user']
            assert templates['templates'][0][1]['user'] == 'Lil_SpazJoekp'
            assert templates['templates'][0][1]['header'] == 'Reddit Authorization Complete'
            assert templates['templates'][0][1]['success']

def test_authorize_user_id(db, flask_app_client, redditApp, mocker, reddit, recorder, regularUserUserVerification):
    redditApp.client_id = pytest.placeholders.client_id
    redditApp.client_secret = pytest.placeholders.client_secret
    redditApp.redirect_uri = pytest.placeholders.redirect_uri
    redditApp.user_agent = pytest.placeholders.user_agent
    db.session.merge(redditApp)
    mocker.patch('app.modules.reddit_apps.models.RedditApp.redditInstance', new_callable=mocker.PropertyMock, return_value=reddit)
    state = redditApp.genAuthUrl(['identity'], 'permanent', user_verification=regularUserUserVerification).split('state=')[1]
    with recorder.use_cassette("RefreshTokens.test_authorize"):
        with captured_templates(flask_app_client.application) as templates:
            url = f'/oauth2/reddit_callback?state={state}&code={pytest.placeholders.auth_code}'
            response = flask_app_client.get(url)
            assert response.content_type == 'text/html; charset=utf-8'
            assert response.status_code == 200
            assertRenderedTemplate(templates, 'oauth_result.html')
            newToken = RefreshToken.query.first()
            assert newToken.redditor == templates['templates'][0][1]['user']
            assert templates['templates'][0][1]['user'] == 'Lil_SpazJoekp'
            assert templates['templates'][0][1]['success']

def test_authorize_bad_code(flask_app_client, redditApp, mocker, reddit, recorder):
    redditApp.client_id = pytest.placeholders.client_id
    redditApp.client_secret = pytest.placeholders.client_secret
    redditApp.redirect_uri = pytest.placeholders.redirect_uri
    redditApp.user_agent = pytest.placeholders.user_agent
    mocker.patch('app.modules.reddit_apps.models.RedditApp.redditInstance', new_callable=mocker.PropertyMock, return_value=reddit)
    with recorder.use_cassette("RefreshTokens.test_authorize"):
        with captured_templates(flask_app_client.application) as templates:
            url = '/oauth2/reddit_callback?state=0bd10e960b8e7a49f83383aa08f6de5015ebbc878c157e6cad73fc21b8f4315b&code=bad_code'
            response = flask_app_client.get(url)
            assert response.content_type == 'text/html; charset=utf-8'
            assert response.status_code == 200
            assertRenderedTemplate(templates, 'oauth_result.html')
            newToken = RefreshToken.query.first()
            assert newToken is None
            assert templates['templates'][0][1]['error']

def test_authorize_root(flask_app_client, redditApp):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get('/oauth2/reddit_callback')
        assert response.content_type == 'text/html; charset=utf-8'
        assert response.status_code == 200
        assertRenderedTemplate(templates, 'oauth_result.html')
        newToken = RefreshToken.query.first()
        assert newToken is None
        assert not templates['templates'][0][1]['success']