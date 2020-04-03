import pytest

from tests.params import labels, users
from tests.responseStatuses import assert200, assert403, assert404
from tests.utils import assertRenderedTemplate, captured_templates, changeOwner


@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_refresh_token_detail(flask_app_client, loginAs, regularUserRefreshToken):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get(f'/refresh_tokens/{regularUserRefreshToken.id}')
        if loginAs.is_admin or loginAs.is_internal:
            assert200(response)
            assertRenderedTemplate(templates, 'edit_refresh_token.html')
        else:
            assert403(response, templates)

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_refresh_token_detail_self(flask_app_client, db, loginAs, regularUserRefreshToken):
    changeOwner(db, loginAs, regularUserRefreshToken)
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get(f'/profile/refresh_tokens')
        assert200(response)
        assertRenderedTemplate(templates, 'refresh_tokens.html')

def test_non_existant_refresh_token_detail(flask_app_client, regular_user):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get(f'/refresh_tokens/1')
        assert404(response, templates)