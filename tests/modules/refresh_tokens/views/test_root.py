import pytest

from tests.params import labels, users
from tests.responseStatuses import assert200
from tests.utils import assertRenderedTemplate, captured_templates


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_root(flask_app_client, loginAs):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get("/refresh_tokens")
        assert200(response)
        assertRenderedTemplate(templates, "refresh_tokens.html")


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_root_profile(flask_app_client, loginAs):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get("/profile/refresh_tokens")
        assert200(response)
        assertRenderedTemplate(templates, "refresh_tokens.html")


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_root_user_page(flask_app_client, loginAs, regular_user):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get(f"/u/{regular_user}/refresh_tokens")
        assert200(response)
        assertRenderedTemplate(templates, "refresh_tokens.html")


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_root_show_all(flask_app_client, loginAs, regular_user):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get(
            f"/u/{regular_user}/refresh_tokens?showOld=true"
        )
        assert200(response)
        assertRenderedTemplate(templates, "refresh_tokens.html")
