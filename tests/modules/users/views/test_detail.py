import pytest

from tests.params import labels, users
from tests.responseStatuses import assert200, assert403
from tests.utils import assertRenderedTemplate, captured_templates


@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_user_detail(flask_app_client, loginAs, regular_user):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get(f'/u/{regular_user.username}')
        if loginAs.is_admin or loginAs.is_internal:
            assert200(response)
            assertRenderedTemplate(templates, 'edit_user.html')
        else:
            assert403(response, templates)

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_user_detail_self(flask_app_client, loginAs):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get(f'/profile', follow_redirects=True)
        assert200(response)
        assertRenderedTemplate(templates, 'edit_user.html')