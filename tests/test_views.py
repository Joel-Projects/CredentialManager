import pytest

from tests.utils import assert_rendered_template, captured_templates

users = [
    pytest.lazy_fixture("admin_user_instance"),
    pytest.lazy_fixture("anonymous_user_instance"),
]
labels = ["as_admin_user", "as_anonymous_user"]


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_root(flask_app_client, login_as, regular_user):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get("/", follow_redirects=True)
        if login_as.is_authenticated:
            assert response.status_code == 200
            assert response.mimetype == "text/html"
            assert_rendered_template(templates, "dash.html")
        else:
            assert response.status_code == 200
            assert response.mimetype == "text/html"
            assert_rendered_template(templates, "login.html")


def test_docs(flask_app_client):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get("/api/v1/docs", follow_redirects=True)
        assert response.status_code == 200
        assert_rendered_template(templates, "swagger-ui.html")
