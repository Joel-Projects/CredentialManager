import json

import pytest

from app.modules.users.models import User
from tests.params import labels, users
from tests.responseStatuses import assert201, assert403
from tests.utils import assertRenderedTemplate, captured_templates


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_create_user(flask_app_client, loginAs):
    with captured_templates(flask_app_client.application) as templates:
        data = {
            "is_admin": True,
            "is_internal": False,
            "is_regular_user": False,
            "is_active": True,
            "username": "test",
            "password": "test",
            "reddit_username": "test",
            "default_settings": json.dumps(
                [{"key": "database_flavor", "value": "test"}]
            ),
        }
        response = flask_app_client.post(
            "/users", content_type="application/x-www-form-urlencoded", data=data
        )
        if loginAs.is_admin or loginAs.is_internal:
            assert201(response)
            assertRenderedTemplate(templates, "users.html")
            user = User.query.filter_by(username="test").first()
            assert user is not None
        else:
            assert403(response, templates)
            user = User.query.filter_by(username="test").first()
            assert user is None


def test_create_user_bad_params(flask_app_client, adminUserInstance):
    with captured_templates(flask_app_client.application) as templates:
        data = {
            "is_admin": True,
            "is_internal": False,
            "is_regular_user": False,
            "is_active": True,
            "username": "test",
            "password": "",
            "reddit_username": "test",
            "default_settings": json.dumps(
                [{"key": "database_flavor", "value": "test"}]
            ),
        }
        response = flask_app_client.post(
            "/users", content_type="application/x-www-form-urlencoded", data=data
        )
        assert response.status_code == 200
        assert response.mimetype == "application/json"
        user = User.query.filter_by(username="test").first()
        assert user is None
