import pytest

from tests.params import labels, users
from tests.responseStatuses import assert200
from tests.utils import captured_templates


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_root(flask_app_client, loginAs):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get("/api_tokens")
        assert200(response)


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_root_profile(flask_app_client, loginAs):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get("/profile/api_tokens")
        assert200(response)


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_root_user_page(flask_app_client, loginAs, regularUserApiToken):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get(f"/u/{regularUserApiToken.owner}/api_tokens")
        assert200(response)
