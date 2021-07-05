import pytest

from app.modules.sentry_tokens.models import SentryToken
from app.modules.sentry_tokens.schemas import DetailedSentryTokenSchema
from tests.params import labels, users
from tests.utils import assert403, assert422, assertSuccess

path = "/api/v1/sentry_tokens/"
data = {"app_name": "testToken", "dsn": "https://1234@abcd.com/1"}


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_creating_sentry_token(flask_app_client, loginAs, regular_user):
    response = flask_app_client.post(path, data={"owner_id": regular_user.id, **data})

    if loginAs.is_admin or loginAs.is_internal:
        assertSuccess(response, regular_user, SentryToken, DetailedSentryTokenSchema)
    else:
        assert403(response, SentryToken, action="create")


def test_creating_sentry_token_for_self(flask_app_client, regularUserInstance):
    response = flask_app_client.post(path, data=data)

    assertSuccess(response, regularUserInstance, SentryToken, DetailedSentryTokenSchema)


def test_creating_sentry_token_for_self_with_owner(
    flask_app_client, regularUserInstance
):
    response = flask_app_client.post(
        path, data={"owner_id": regularUserInstance.id, **data}
    )

    assertSuccess(response, regularUserInstance, SentryToken, DetailedSentryTokenSchema)


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_creating_sentry_token_with_bad_name(flask_app_client, loginAs):
    response = flask_app_client.post(path, data={**data, "app_name": "to"})

    assert422(
        response,
        SentryToken,
        messageAttrs=[("app_name", ["Name must be greater than 3 characters long."])],
    )
