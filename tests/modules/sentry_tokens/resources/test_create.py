import pytest

from app.modules.sentry_tokens.models import SentryToken
from app.modules.sentry_tokens.schemas import DetailedSentryTokenSchema
from tests.params import labels, users
from tests.utils import assert403, assert422, assert_success

path = "/api/v1/sentry_tokens/"
data = {"app_name": "test_token", "dsn": "https://1234@abcd.com/1"}


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_creating_sentry_token(flask_app_client, login_as, regular_user):
    response = flask_app_client.post(path, data={"owner_id": regular_user.id, **data})

    if login_as.is_admin or login_as.is_internal:
        assert_success(response, regular_user, SentryToken, DetailedSentryTokenSchema)
    else:
        assert403(response, SentryToken, action="create")


def test_creating_sentry_token_for_self(flask_app_client, regular_user_instance):
    response = flask_app_client.post(path, data=data)

    assert_success(
        response, regular_user_instance, SentryToken, DetailedSentryTokenSchema
    )


def test_creating_sentry_token_for_self_with_owner(
    flask_app_client, regular_user_instance
):
    response = flask_app_client.post(
        path, data={"owner_id": regular_user_instance.id, **data}
    )

    assert_success(
        response, regular_user_instance, SentryToken, DetailedSentryTokenSchema
    )


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_creating_sentry_token_with_bad_name(flask_app_client, login_as):
    response = flask_app_client.post(path, data={**data, "app_name": "to"})

    assert422(
        response,
        SentryToken,
        message_attrs=[("app_name", ["Name must be greater than 3 characters long."])],
    )
