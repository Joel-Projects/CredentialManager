import pytest

from app.modules.bots.models import Bot
from app.modules.bots.schemas import DetailedBotSchema
from tests.params import labels, users
from tests.response_statuses import assert422
from tests.utils import assert403, assert_success

path = "/api/v1/bots/"
base_data = {"app_name": "new_bot"}


@pytest.mark.parametrize("login_as", users, ids=labels)
@pytest.mark.parametrize("use_reddit_app", [True, False])
@pytest.mark.parametrize("use_sentry_token", [True, False])
@pytest.mark.parametrize("use_database_credential", [True, False])
def test_creating_bot(
    flask_app_client,
    login_as,
    reddit_app,
    sentry_token,
    database_credential,
    use_reddit_app,
    use_sentry_token,
    use_database_credential,
):
    data = {**base_data}
    reddit_app.owner = login_as
    sentry_token.owner = login_as
    database_credential.owner = login_as
    if use_reddit_app:
        data["reddit_app_id"] = reddit_app.id
    if use_sentry_token:
        data["sentry_token_id"] = sentry_token.id
    if use_database_credential:
        data["database_credential_id"] = database_credential.id
    response = flask_app_client.post(path, data=data)

    assert_success(response, login_as, Bot, DetailedBotSchema)


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_creating_bot_with_owner(
    flask_app_client,
    login_as,
    regular_user,
    reddit_app,
    sentry_token,
    database_credential,
):
    response = flask_app_client.post(
        path,
        data={
            "owner_id": regular_user.id,
            "reddit_app_id": reddit_app.id,
            "sentry_token_id": sentry_token.id,
            "database_credential_id": database_credential.id,
            **base_data,
        },
    )

    if login_as.is_admin or login_as.is_internal:
        assert_success(response, regular_user, Bot, DetailedBotSchema)
    else:
        assert403(response, Bot, action="create")


def test_creating_bot_for_self(
    flask_app_client,
    regular_user_instance,
    reddit_app,
    sentry_token,
    database_credential,
):
    reddit_app.owner = regular_user_instance
    response = flask_app_client.post(
        path,
        data={
            "reddit_app_id": reddit_app.id,
            "sentry_token_id": sentry_token.id,
            "database_credential_id": database_credential.id,
            **base_data,
        },
    )

    assert_success(response, regular_user_instance, Bot, DetailedBotSchema)


def test_creating_bot_for_self_with_owner(
    flask_app_client,
    regular_user_instance,
    reddit_app,
    sentry_token,
    database_credential,
):
    reddit_app.owner = regular_user_instance
    response = flask_app_client.post(
        path,
        data={
            "owner_id": regular_user_instance.id,
            "reddit_app_id": reddit_app.id,
            "sentry_token_id": sentry_token.id,
            "database_credential_id": database_credential.id,
            **base_data,
        },
    )

    assert_success(response, regular_user_instance, Bot, DetailedBotSchema)


def test_creating_bot_bad_name(
    flask_app_client,
    regular_user_instance,
    reddit_app,
    sentry_token,
    database_credential,
):
    reddit_app.owner = regular_user_instance
    response = flask_app_client.post(
        path,
        data={
            "reddit_app_id": reddit_app.id,
            "sentry_token_id": sentry_token.id,
            "database_credential_id": database_credential.id,
            "app_name": "bo",
        },
    )
    assert422(response)
