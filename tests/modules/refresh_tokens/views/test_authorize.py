import pytest

from app.modules.refresh_tokens.models import RefreshToken
from tests.utils import assert_rendered_template, captured_templates


def test_authorize(db, flask_app_client, reddit_app, mocker, reddit, recorder):
    reddit_app.client_id = pytest.placeholders.client_id
    reddit_app.client_secret = pytest.placeholders.client_secret
    reddit_app.redirect_uri = pytest.placeholders.redirect_uri
    reddit_app.user_agent = pytest.placeholders.user_agent
    db.session.merge(reddit_app)
    mocker.patch(
        "app.modules.reddit_apps.models.RedditApp.reddit_instance",
        new_callable=mocker.PropertyMock,
        return_value=reddit,
    )
    with recorder.use_cassette("RefreshTokens.test_authorize"):
        with captured_templates(flask_app_client.application) as templates:
            url = f"/oauth2/reddit_callback?state={reddit_app.state}&code={pytest.placeholders.auth_code}"
            response = flask_app_client.get(url)
            assert response.content_type == "text/html; charset=utf-8"
            assert response.status_code == 200
            assert_rendered_template(templates, "oauth_result.html")
            new_token = RefreshToken.query.first()
            assert new_token.redditor == templates["templates"][0][1]["user"]
            assert templates["templates"][0][1]["user"] == "Lil_SpazJoekp"
            assert templates["templates"][0][1]["header"] == "Reddit Authorization Complete"
            assert templates["templates"][0][1]["success"]


def test_authorize_temp(db, flask_app_client, reddit_app, mocker, reddit, recorder):
    reddit_app.client_id = pytest.placeholders.client_id
    reddit_app.client_secret = pytest.placeholders.client_secret
    reddit_app.redirect_uri = pytest.placeholders.redirect_uri
    reddit_app.user_agent = pytest.placeholders.user_agent
    db.session.merge(reddit_app)
    mocker.patch(
        "app.modules.reddit_apps.models.RedditApp.reddit_instance",
        new_callable=mocker.PropertyMock,
        return_value=reddit,
    )
    with recorder.use_cassette("RefreshTokens.test_authorize_temp"):
        with captured_templates(flask_app_client.application) as templates:
            url = f"/oauth2/reddit_callback?state={reddit_app.state}&code={pytest.placeholders.auth_code}"
            response = flask_app_client.get(url)
            assert response.content_type == "text/html; charset=utf-8"
            assert response.status_code == 200
            assert_rendered_template(templates, "oauth_result.html")
            new_token = RefreshToken.query.first()
            assert new_token is None
            assert templates["templates"][0][1]["user"] == "Lil_SpazJoekp"
            assert templates["templates"][0][1]["header"] == "Reddit Verification Complete"
            assert templates["templates"][0][1]["success"]


def test_authorize_exisiting(
    db,
    flask_app_client,
    reddit_app,
    mocker,
    reddit,
    recorder,
    regular_user_refresh_token,
):
    reddit_app.client_id = pytest.placeholders.client_id
    reddit_app.client_secret = pytest.placeholders.client_secret
    reddit_app.redirect_uri = pytest.placeholders.redirect_uri
    reddit_app.user_agent = pytest.placeholders.user_agent
    db.session.merge(reddit_app)
    mocker.patch(
        "app.modules.reddit_apps.models.RedditApp.reddit_instance",
        new_callable=mocker.PropertyMock,
        return_value=reddit,
    )
    with recorder.use_cassette("RefreshTokens.test_authorize"):
        with captured_templates(flask_app_client.application) as templates:
            url = f"/oauth2/reddit_callback?state={reddit_app.state}&code={pytest.placeholders.auth_code}"
            response = flask_app_client.get(url)
            assert response.content_type == "text/html; charset=utf-8"
            assert response.status_code == 200
            assert_rendered_template(templates, "oauth_result.html")
            new_token = RefreshToken.query.filter_by(redditor="Lil_SpazJoekp").first()
            assert new_token.redditor == templates["templates"][0][1]["user"]
            assert templates["templates"][0][1]["user"] == "Lil_SpazJoekp"
            assert templates["templates"][0][1]["header"] == "Reddit Authorization Complete"
            assert templates["templates"][0][1]["success"]


def test_authorize_user_id(
    db,
    flask_app_client,
    reddit_app,
    mocker,
    reddit,
    recorder,
    regular_user_user_verification,
):
    reddit_app.client_id = pytest.placeholders.client_id
    reddit_app.client_secret = pytest.placeholders.client_secret
    reddit_app.redirect_uri = pytest.placeholders.redirect_uri
    reddit_app.user_agent = pytest.placeholders.user_agent
    db.session.merge(reddit_app)
    mocker.patch(
        "app.modules.reddit_apps.models.RedditApp.reddit_instance",
        new_callable=mocker.PropertyMock,
        return_value=reddit,
    )
    state = reddit_app.gen_auth_url(["identity"], "permanent", user_verification=regular_user_user_verification).split(
        "state="
    )[1]
    with recorder.use_cassette("RefreshTokens.test_authorize"):
        with captured_templates(flask_app_client.application) as templates:
            url = f"/oauth2/reddit_callback?state={state}&code={pytest.placeholders.auth_code}"
            response = flask_app_client.get(url)
            assert response.content_type == "text/html; charset=utf-8"
            assert response.status_code == 200
            assert_rendered_template(templates, "oauth_result.html")
            new_token = RefreshToken.query.first()
            assert new_token.redditor == templates["templates"][0][1]["user"]
            assert templates["templates"][0][1]["user"] == "Lil_SpazJoekp"
            assert templates["templates"][0][1]["success"]


def test_authorize_bad_code(flask_app_client, reddit_app, mocker, reddit, recorder):
    reddit_app.client_id = pytest.placeholders.client_id
    reddit_app.client_secret = pytest.placeholders.client_secret
    reddit_app.redirect_uri = pytest.placeholders.redirect_uri
    reddit_app.user_agent = pytest.placeholders.user_agent
    mocker.patch(
        "app.modules.reddit_apps.models.RedditApp.reddit_instance",
        new_callable=mocker.PropertyMock,
        return_value=reddit,
    )
    with recorder.use_cassette("RefreshTokens.test_authorize"):
        with captured_templates(flask_app_client.application) as templates:
            url = "/oauth2/reddit_callback?state=0bd10e960b8e7a49f83383aa08f6de5015ebbc878c157e6cad73fc21b8f4315b&code=bad_code"
            response = flask_app_client.get(url)
            assert response.content_type == "text/html; charset=utf-8"
            assert response.status_code == 200
            assert_rendered_template(templates, "oauth_result.html")
            new_token = RefreshToken.query.first()
            assert new_token is None
            assert templates["templates"][0][1]["error"]


def test_authorize_root(flask_app_client, reddit_app):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get("/oauth2/reddit_callback")
        assert response.content_type == "text/html; charset=utf-8"
        assert response.status_code == 200
        assert_rendered_template(templates, "oauth_result.html")
        new_token = RefreshToken.query.first()
        assert new_token is None
        assert not templates["templates"][0][1]["success"]
