import pytest

from tests.params import labels, users
from tests.response_statuses import assert200
from tests.utils import captured_templates


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_root(flask_app_client, login_as):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get("/reddit_apps")
        assert200(response)


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_root_profile(flask_app_client, login_as):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get("/profile/reddit_apps")
        assert200(response)


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_root_user_page(flask_app_client, login_as, regular_user):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get(f"/u/{regular_user}/reddit_apps")
        assert200(response)
