import pytest

from tests.params import labels, users
from tests.responseStatuses import assert200, assert403, assert404
from tests.utils import assertRenderedTemplate, captured_templates, changeOwner


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_reddit_app_detail(flask_app_client, loginAs, regularUserRedditApp):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get(f"/reddit_apps/{regularUserRedditApp.id}")
        if loginAs.is_admin or loginAs.is_internal:
            assert200(response)
            assertRenderedTemplate(templates, "edit_reddit_app.html")
        else:
            assert403(response, templates)


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_reddit_app_detail_self(flask_app_client, db, loginAs, regularUserRedditApp):
    changeOwner(db, loginAs, regularUserRedditApp)
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get(f"/profile/reddit_apps")
        assert200(response)
        assertRenderedTemplate(templates, "reddit_apps.html")


def test_non_existant_reddit_app_detail(flask_app_client, regular_user):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get(f"/reddit_apps/1")
        assert404(response, templates)
