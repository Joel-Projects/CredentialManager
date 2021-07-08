import itertools

import pytest

from app.modules.api_tokens.models import ApiToken
from tests.params import labels, users
from tests.response_statuses import assert201, assert401, assert403Create, assert422
from tests.utils import assert_rendered_template, captured_templates


def assert_created(length):
    api_token = ApiToken.query.filter_by(name="api_token").first()
    assert api_token is not None
    assert len(api_token.token) == length
    assert api_token.length == length
    return api_token


@pytest.mark.parametrize("length", itertools.chain(range(16, 56, 8), [64]))
def test_create_api_token_length(flask_app_client, regular_user_instance, length):
    with captured_templates(flask_app_client.application) as templates:
        data = {"length": str(length), "name": "api_token"}
        response = flask_app_client.post(
            "/api_tokens", content_type="application/x-www-form-urlencoded", data=data
        )
        assert201(response)
        assert_rendered_template(templates, "api_tokens.html")
        assert_created(length)


@pytest.mark.parametrize("length", itertools.chain(range(16, 56, 8), [64]))
def test_create_api_token_length_profile(
    flask_app_client, regular_user_instance, length
):
    with captured_templates(flask_app_client.application) as templates:
        data = {"length": str(length), "name": "api_token"}
        response = flask_app_client.post(
            "/profile/api_tokens",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        assert201(response)
        assert_rendered_template(templates, "api_tokens.html")
        assert_created(length)


@pytest.mark.parametrize(
    "login_as",
    [
        pytest.lazy_fixture("admin_user"),
        pytest.lazy_fixture("internal_user"),
        pytest.lazy_fixture("regular_user"),
    ],
    ids=labels,
)
@pytest.mark.parametrize("enabled", ["y", ""])
def test_create_api_token_enabled(flask_app_client, flask_app, login_as, enabled):
    with captured_templates(flask_app_client.application) as templates:
        data = {"name": "api_token", "enabled": enabled}
        with flask_app_client.login(login_as) as client:
            response = client.post(
                f"/api_tokens",
                content_type="application/x-www-form-urlencoded",
                data=data,
            )
        assert201(response)
        api_token = assert_created(32)
        assert api_token.enabled == bool(enabled)
        response = flask_app.test_client().get(
            "/api/v1/users/me", headers={"X-API-TOKEN": api_token.token}
        )
        if enabled:
            assert response.status_code == 200
            assert response.mimetype == "application/json"
            assert response.json["username"] == login_as.username
        else:
            assert401(response)


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_create_api_token_other_user(flask_app_client, login_as, regular_user):
    with captured_templates(flask_app_client.application) as templates:
        data = {"name": "api_token", "owner": regular_user.id}
        response = flask_app_client.post(
            "/api_tokens", content_type="application/x-www-form-urlencoded", data=data
        )
        if login_as.is_admin or login_as.is_internal:
            assert201(response)
            assert_rendered_template(templates, "api_tokens.html")
            assert_created(32)
        else:
            assert403Create(response)
            api_token = ApiToken.query.filter_by(name="api_token").first()
            assert api_token is None


def test_create_api_token_bad_params(flask_app_client, regular_user_instance):
    with captured_templates(flask_app_client.application) as templates:
        data = {"name": "ap", "length": 500}
        response = flask_app_client.post(
            "/api_tokens", content_type="application/x-www-form-urlencoded", data=data
        )
        assert response.status_code == 200
        assert response.mimetype == "application/json"
        api_token = ApiToken.query.filter_by(name="api_token").first()
        assert api_token is None
        assert response.json["errors"]["length"][0] == "Not a valid choice"
        assert (
            response.json["errors"]["name"][0]
            == "Field must be at least 3 characters long."
        )


def test_create_api_token_bad_params_profile(flask_app_client, regular_user_instance):
    with captured_templates(flask_app_client.application) as templates:
        data = {"name": "ap", "length": 500}
        response = flask_app_client.post(
            "/profile/api_tokens",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        assert422(response)
        api_token = ApiToken.query.filter_by(name="api_token").first()
        assert api_token is None
        assert response.json["errors"]["length"][0] == "Not a valid choice"
        assert (
            response.json["errors"]["name"][0]
            == "Field must be at least 3 characters long."
        )
