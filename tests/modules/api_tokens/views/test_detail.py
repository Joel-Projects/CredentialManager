import pytest

from tests.params import labels, users
from tests.responseStatuses import assert200, assert403, assert404
from tests.utils import assertRenderedTemplate, captured_templates, changeOwner


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_api_token_detail(flask_app_client, loginAs, regularUserApiToken):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get(f"/api_tokens/{regularUserApiToken.id}")
        if loginAs.is_admin or loginAs.is_internal:
            assert200(response)
            assertRenderedTemplate(templates, "edit_api_token.html")
        else:
            assert403(response, templates)


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_api_token_detail_self(flask_app_client, db, loginAs, regularUserApiToken):
    changeOwner(db, loginAs, regularUserApiToken)
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get(f"/profile/api_tokens")
        assert200(response)
        assertRenderedTemplate(templates, "api_tokens.html")


def test_non_existant_api_token_detail(flask_app_client, regular_user):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get(f"/api_tokens/1")
        assert404(response, templates)
