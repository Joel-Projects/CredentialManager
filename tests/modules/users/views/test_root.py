import pytest

from tests.params import labels, users
from tests.response_statuses import assert200, assert403, assert404
from tests.utils import captured_templates


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_root(flask_app_client, login_as):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get("/users")
        if login_as.is_admin or login_as.is_internal:
            assert200(response)
        else:
            assert403(response, templates)


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_non_existent_item_view(flask_app_client, login_as):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get(f"/profile/non_existent")
        assert404(response, templates)
