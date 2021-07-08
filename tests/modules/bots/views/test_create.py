import pytest

from app.modules.bots.models import Bot
from tests.params import labels, users
from tests.response_statuses import assert201, assert403Create, assert422
from tests.utils import assert_created, assert_rendered_template, captured_templates

data = {
    "app_name": "bot",
    "reddit_app": "1",
    "sentry_token": "1",
    "database_credential": "1",
}


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_create_bot(
    flask_app_client, login_as, reddit_app, sentry_token, database_credential
):
    with captured_templates(flask_app_client.application) as templates:
        reddit_app.owner = login_as
        sentry_token.owner = login_as
        database_credential.owner = login_as
        response = flask_app_client.post(
            "/bots", content_type="application/x-www-form-urlencoded", data=data
        )
        assert201(response)
        assert_rendered_template(templates, "bots.html")
        bot = Bot.query.filter_by(app_name="bot").first()
        assert_created(bot, data)


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_create_bot_profile(
    flask_app_client, login_as, reddit_app, sentry_token, database_credential
):
    with captured_templates(flask_app_client.application) as templates:
        reddit_app.owner = login_as
        sentry_token.owner = login_as
        database_credential.owner = login_as
        response = flask_app_client.post(
            f"/profile/bots",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        assert201(response)
        assert_rendered_template(templates, "bots.html")
        bot = Bot.query.filter_by(app_name="bot").first()
        assert_created(bot, data)


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_create_bot_other_user(
    flask_app_client,
    login_as,
    regular_user,
    reddit_app,
    sentry_token,
    database_credential,
):
    with captured_templates(flask_app_client.application) as templates:
        if not (login_as.is_admin or login_as.is_internal):
            reddit_app.owner = login_as
            sentry_token.owner = login_as
            database_credential.owner = login_as
        response = flask_app_client.post(
            "/bots",
            content_type="application/x-www-form-urlencoded",
            data={"owner": str(regular_user.id), **data},
        )
        if login_as.is_admin or login_as.is_internal:
            assert201(response)
            assert_rendered_template(templates, "bots.html")
            bot = Bot.query.filter_by(app_name="bot").first()
            assert_created(bot, data)
            assert bot.owner == regular_user
        else:
            assert403Create(response)
            bot = Bot.query.filter_by(app_name="bot").first()
            assert bot is None


def test_create_bot_bad_params(flask_app_client, regular_user_instance):
    response = flask_app_client.post(
        "/bots",
        content_type="application/x-www-form-urlencoded",
        data={"app_name": "bo", **data},
    )
    assert response.status_code == 200
    assert response.mimetype == "application/json"
    bot = Bot.query.filter_by(app_name="bot").first()
    assert bot is None
