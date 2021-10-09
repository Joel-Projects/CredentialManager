import pytest

from app.modules.reddit_apps.models import RedditApp
from tests.params import labels, users
from tests.response_statuses import assert201, assert403Create, assert422
from tests.utils import assert_created, assert_rendered_template, captured_templates

data = {
    "app_name": "reddit_app",
    "client_id": "client_id",
    "client_secret": "client_secret",
    "user_agent": "user_agent",
    "app_type": "web",
}


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_create_reddit_app(flask_app_client, login_as):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post("/reddit_apps", content_type="application/x-www-form-urlencoded", data=data)
        assert201(response)
        assert_rendered_template(templates, "reddit_apps.html")
        reddit_app = RedditApp.query.filter_by(app_name="reddit_app").first()
        assert_created(reddit_app, data)


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_create_reddit_app_profile(flask_app_client, login_as):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            f"/profile/reddit_apps",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        assert201(response)
        assert_rendered_template(templates, "reddit_apps.html")
        reddit_app = RedditApp.query.filter_by(app_name="reddit_app").first()
        assert_created(reddit_app, data)


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_create_reddit_app_other_user(flask_app_client, login_as, regular_user):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            "/reddit_apps",
            content_type="application/x-www-form-urlencoded",
            data={"owner": regular_user.id, **data},
        )
        if login_as.is_admin or login_as.is_internal:
            assert201(response)
            assert_rendered_template(templates, "reddit_apps.html")
            reddit_app = RedditApp.query.filter_by(app_name="reddit_app").first()
            assert_created(reddit_app, data)
            assert reddit_app.owner == regular_user
        else:
            assert403Create(response)
            reddit_app = RedditApp.query.filter_by(app_name="reddit_app").first()
            assert reddit_app is None


def test_create_reddit_app_bad_params(flask_app_client, regular_user_instance):
    with captured_templates(flask_app_client.application) as templates:
        data = {"dsn": "invalid_url", "app_name": "reddit_app"}
        response = flask_app_client.post("/reddit_apps", content_type="application/x-www-form-urlencoded", data=data)
        assert response.status_code == 200
        assert response.mimetype == "application/json"
        reddit_app = RedditApp.query.filter_by(app_name="reddit_app").first()
        assert reddit_app is None


def test_create_reddit_app_bad_params_profile(flask_app_client, regular_user_instance):
    with captured_templates(flask_app_client.application) as templates:
        data = {"dsn": "invalid_url", "app_name": "reddit_app"}
        response = flask_app_client.post(
            "/profile/reddit_apps",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        assert422(response)
        reddit_app = RedditApp.query.filter_by(app_name="reddit_app").first()
        assert reddit_app is None
