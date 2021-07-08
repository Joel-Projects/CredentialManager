import pytest

from app.modules.bots.models import Bot
from tests.params import labels, users
from tests.response_statuses import assert202, assert403
from tests.utils import (
    assert_message_flashed,
    assert_modified,
    assert_rendered_template,
    captured_templates,
    change_owner,
)

bots = [
    pytest.lazy_fixture("admin_user_bot"),
    pytest.lazy_fixture("internal_user_bot"),
    pytest.lazy_fixture("regular_user_bot"),
]
bot_labels = [
    "admin_user_bot+reddit_app",
    "internal_user_bot+reddit_app",
    "regular_user_bot+reddit_app",
]


@pytest.mark.parametrize("login_as", users, ids=labels)
@pytest.mark.parametrize("bot", bots, ids=bot_labels)
def test_bot_detail_edit_for_other_user(
    flask_app_client, login_as, bot, reddit_app, sentry_token, database_credential
):
    data = {
        "item_type": "bots",
        "item_id": f"{bot.id}",
        "app_name": "new_name",
        "reddit_app": f"{reddit_app.id}",
        "sentry_token": f"{sentry_token.id}",
        "database_credential": f"{database_credential.id}",
        "enabled": "y",
        "owner": f"{bot.owner.id}",
    }
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            f"/bots/{bot.id}",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        if login_as.is_internal:
            assert202(response)
            assert_rendered_template(templates, "edit_bot.html")
            assert_message_flashed(
                templates, "Bot 'new_name' saved successfully!", "success"
            )
            modified_bot = Bot.query.filter_by(id=bot.id).first()
            assert_modified(data, modified_bot)
        elif login_as.is_admin:
            if reddit_app.owner.is_internal or bot.owner.is_internal:
                assert403(response, templates)
                modified_bot = Bot.query.filter_by(id=bot.id).first()
                assert modified_bot == bot
            else:
                assert202(response)
                assert_rendered_template(templates, "edit_bot.html")
                assert_message_flashed(
                    templates, "Bot 'new_name' saved successfully!", "success"
                )
                modified_bot = Bot.query.filter_by(id=bot.id).first()
                assert_modified(data, modified_bot)
        else:
            assert403(response, templates)
            modified_bot = Bot.query.filter_by(id=bot.id).first()
            assert modified_bot == bot


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_bot_detail_edit(
    flask_app_client,
    login_as,
    regular_user_bot,
    reddit_app,
    reddit_app2,
    sentry_token,
    database_credential,
):
    data = {
        "item_type": "bots",
        "item_id": f"{regular_user_bot.id}",
        "app_name": "new_name",
        "reddit_app": f"{reddit_app2.id}",
        "sentry_token": f"{sentry_token.id}",
        "database_credential": f"{database_credential.id}",
        "owner": f"{regular_user_bot.owner.id}",
    }
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            f"/bots/{regular_user_bot.id}",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        if login_as.is_admin or login_as.is_internal:
            assert202(response)
            assert_rendered_template(templates, "edit_bot.html")
            assert_message_flashed(
                templates, "Bot 'new_name' saved successfully!", "success"
            )
            modified_bot = Bot.query.filter_by(id=regular_user_bot.id).first()
            assert_modified(data, modified_bot)

        else:
            assert403(response, templates)
            modified_bot = Bot.query.filter_by(id=regular_user_bot.id).first()
            assert modified_bot == regular_user_bot


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_bot_detail_edit_self(
    flask_app_client,
    db,
    login_as,
    regular_user_bot,
    reddit_app,
    sentry_token,
    database_credential,
):
    data = {
        "item_type": "bots",
        "item_id": f"{regular_user_bot.id}",
        "app_name": "new_name",
        "reddit_app": f"{reddit_app.id}",
        "sentry_token": f"{sentry_token.id}",
        "database_credential": f"{database_credential.id}",
        "owner": f"{login_as.id}",
    }
    regular_user_bot.owner = login_as
    reddit_app.owner = login_as
    sentry_token.owner = login_as
    database_credential.owner = login_as
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(f"/bots/{regular_user_bot.id}", data=data)
        assert202(response)
        assert_rendered_template(templates, "edit_bot.html")
        assert_message_flashed(
            templates, "Bot 'new_name' saved successfully!", "success"
        )
        modified_bot = Bot.query.filter_by(id=regular_user_bot.id).first()
        assert_modified(data, modified_bot)


def test_bot_detail_conflicting_name(
    flask_app_client,
    db,
    regular_user_instance,
    regular_user_bot,
    admin_user_bot,
    reddit_app,
    sentry_token,
    database_credential,
):
    original = change_owner(db, regular_user_instance, admin_user_bot)
    original.app_name = "old_bot"
    db.session.merge(original)
    to_be_modified = change_owner(db, regular_user_instance, regular_user_bot)
    db.session.merge(to_be_modified)
    data = {
        "item_type": "bots",
        "item_id": f"{regular_user_bot.id}",
        "app_name": f"{original.app_name}",
        "reddit_app": f"{reddit_app.id}",
        "sentry_token": f"{sentry_token.id}",
        "database_credential": f"{database_credential.id}",
    }
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(f"/bots/{to_be_modified.id}", json=data)
        assert response.status_code == 422
        assert response.mimetype == "text/html"
        assert_rendered_template(templates, "edit_bot.html")
        assert (
            templates["templates"][0][1]["form"].errors["app_name"][0]
            == "Already exists."
        )
        modified_bot = Bot.query.filter_by(id=to_be_modified.id).first()
        assert modified_bot.app_name == to_be_modified.app_name
