import pytest

from tests.params import labels, users
from tests.responseStatuses import assert200, assert403, assert404
from tests.utils import assertRenderedTemplate, captured_templates, changeOwner


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_sentry_token_detail(flask_app_client, loginAs, regularUserSentryToken):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get(f"/sentry_tokens/{regularUserSentryToken.id}")
        if loginAs.is_admin or loginAs.is_internal:
            assert200(response)
            assertRenderedTemplate(templates, "edit_sentry_token.html")
        else:
            assert403(response, templates)


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_sentry_token_detail_self(
    flask_app_client, db, loginAs, regularUserSentryToken
):
    changeOwner(db, loginAs, regularUserSentryToken)
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get(f"/profile/sentry_tokens")
        assert200(response)
        assertRenderedTemplate(templates, "sentry_tokens.html")


def test_non_existant_sentry_token_detail(flask_app_client, regular_user):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get(f"/sentry_tokens/1")
        assert404(response, templates)
