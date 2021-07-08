import pytest

from app.modules.sentry_tokens.models import SentryToken
from tests.params import labels, users
from tests.response_statuses import assert201, assert403Create, assert422
from tests.utils import assert_created, assert_rendered_template, captured_templates

data = {"app_name": "sentry_token", "dsn": "https://1234asdf@sentry.jesassn.org/1"}


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_create_sentry_token(flask_app_client, login_as):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            "/sentry_tokens",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        assert201(response)
        assert_rendered_template(templates, "sentry_tokens.html")
        sentry_token = SentryToken.query.filter_by(app_name="sentry_token").first()
        assert_created(sentry_token, data)


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_create_sentry_token_profile(flask_app_client, login_as):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            f"/profile/sentry_tokens",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        assert201(response)
        assert_rendered_template(templates, "sentry_tokens.html")
        sentry_token = SentryToken.query.filter_by(app_name="sentry_token").first()
        assert sentry_token is not None
        assert sentry_token.id == 1


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_create_sentry_token_other_user(flask_app_client, login_as, regular_user):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            "/sentry_tokens",
            content_type="application/x-www-form-urlencoded",
            data={"owner": regular_user.id, **data},
        )
        if login_as.is_admin or login_as.is_internal:
            assert201(response)
            assert_rendered_template(templates, "sentry_tokens.html")
            sentry_token = SentryToken.query.filter_by(app_name="sentry_token").first()
            assert sentry_token is not None
            assert sentry_token.id == 1
            assert sentry_token.owner == regular_user
        else:
            assert403Create(response)
            sentry_token = SentryToken.query.filter_by(app_name="sentry_token").first()
            assert sentry_token is None


def test_create_sentry_token_bad_params(flask_app_client, regular_user_instance):
    data["dsn"] = None
    response = flask_app_client.post(
        "/sentry_tokens", content_type="application/x-www-form-urlencoded", data=data
    )
    assert response.status_code == 200
    sentry_token = SentryToken.query.filter_by(app_name="sentry_token").first()
    assert sentry_token is None


def test_create_sentry_token_bad_params_profile(
    flask_app_client, regular_user_instance
):
    data["dsn"] = None
    response = flask_app_client.post(
        "/profile/sentry_tokens",
        content_type="application/x-www-form-urlencoded",
        data=data,
    )
    assert422(response)
    sentry_token = SentryToken.query.filter_by(app_name="sentry_token").first()
    assert sentry_token is None
