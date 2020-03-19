import pytest, json
from app.modules.users.models import User

from tests.utils import captured_templates, assertRenderedTemplate


users = [
    pytest.lazy_fixture('adminUserInstance'),
    pytest.lazy_fixture('anonymousUserInstance'),
]
labels = [
    'as_admin_user',
    'as_anonymous_user'
]

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_root(flask_app_client, loginAs, regular_user):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get('/', follow_redirects=True)
        if loginAs.is_authenticated :
            assert response.status_code == 200
            assert response.mimetype == 'text/html'
            assertRenderedTemplate(templates, 'dash.html')
        else:
            assert response.status_code == 200
            assert response.mimetype == 'text/html'
            assertRenderedTemplate(templates, 'login.html')