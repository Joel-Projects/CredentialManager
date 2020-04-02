import pytest

from tests.params import labels, users
from tests.responseStatuses import assert200, assert403, assert404
from tests.utils import assertRenderedTemplate, captured_templates, changeOwner


@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_bot_detail(flask_app_client, loginAs, regularUserBot):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get(f'/bots/{regularUserBot.id}')
        if loginAs.is_admin or loginAs.is_internal:
            assert200(response)
            assertRenderedTemplate(templates, 'edit_bot.html')
        else:
            assert403(response, templates)

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_bot_detail_self(flask_app_client, db, loginAs, regularUserBot):
    changeOwner(db, loginAs, regularUserBot)
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get(f'/profile/bots')
        assert200(response)
        assertRenderedTemplate(templates, 'bots.html')

def test_non_existant_bot_detail(flask_app_client, regular_user):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get(f'/bots/1')
        assert404(response, templates)