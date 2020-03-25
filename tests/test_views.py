import pytest

from tests.utils import assertRenderedTemplate, captured_templates


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
        if loginAs.is_authenticated:
            assert response.status_code == 200
            assert response.mimetype == 'text/html'
            assertRenderedTemplate(templates, 'dash.html')
        else:
            assert response.status_code == 200
            assert response.mimetype == 'text/html'
            assertRenderedTemplate(templates, 'login.html')

def test_docs(flask_app_client):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get('/api/v1/docs', follow_redirects=True)
        assert response.status_code == 200
        assertRenderedTemplate(templates, 'swagger-ui.html')