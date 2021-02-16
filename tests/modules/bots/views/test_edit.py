import pytest

from app.modules.bots.models import Bot
from tests.params import labels, users
from tests.responseStatuses import assert202, assert403
from tests.utils import (
    assertMessageFlashed,
    assertModified,
    assertRenderedTemplate,
    captured_templates,
    changeOwner,
)


bots = [
    pytest.lazy_fixture("adminUserBot"),
    pytest.lazy_fixture("internalUserBot"),
    pytest.lazy_fixture("regularUserBot"),
]
botLabels = [
    "admin_user_bot+reddit_app",
    "internal_user_bot+reddit_app",
    "regular_user_bot+reddit_app",
]


@pytest.mark.parametrize("loginAs", users, ids=labels)
@pytest.mark.parametrize("bot", bots, ids=botLabels)
def test_bot_detail_edit_for_other_user(
    flask_app_client, loginAs, bot, redditApp, sentryToken, databaseCredential
):
    data = {
        "itemType": "bots",
        "itemId": f"{bot.id}",
        "app_name": "newName",
        "reddit_app": f"{redditApp.id}",
        "sentry_token": f"{sentryToken.id}",
        "database_credential": f"{databaseCredential.id}",
        "enabled": "y",
        "owner": f"{bot.owner.id}",
    }
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            f"/bots/{bot.id}",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        if loginAs.is_internal:
            assert202(response)
            assertRenderedTemplate(templates, "edit_bot.html")
            assertMessageFlashed(
                templates, "Bot 'newName' saved successfully!", "success"
            )
            modifiedBot = Bot.query.filter_by(id=bot.id).first()
            assertModified(data, modifiedBot)
        elif loginAs.is_admin:
            if redditApp.owner.is_internal or bot.owner.is_internal:
                assert403(response, templates)
                modifiedBot = Bot.query.filter_by(id=bot.id).first()
                assert modifiedBot == bot
            else:
                assert202(response)
                assertRenderedTemplate(templates, "edit_bot.html")
                assertMessageFlashed(
                    templates, "Bot 'newName' saved successfully!", "success"
                )
                modifiedBot = Bot.query.filter_by(id=bot.id).first()
                assertModified(data, modifiedBot)
        else:
            assert403(response, templates)
            modifiedBot = Bot.query.filter_by(id=bot.id).first()
            assert modifiedBot == bot


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_bot_detail_edit(
    flask_app_client,
    loginAs,
    regularUserBot,
    redditApp,
    redditApp2,
    sentryToken,
    databaseCredential,
):
    data = {
        "itemType": "bots",
        "itemId": f"{regularUserBot.id}",
        "app_name": "newName",
        "reddit_app": f"{redditApp2.id}",
        "sentry_token": f"{sentryToken.id}",
        "database_credential": f"{databaseCredential.id}",
        "owner": f"{regularUserBot.owner.id}",
    }
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            f"/bots/{regularUserBot.id}",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        if loginAs.is_admin or loginAs.is_internal:
            assert202(response)
            assertRenderedTemplate(templates, "edit_bot.html")
            assertMessageFlashed(
                templates, "Bot 'newName' saved successfully!", "success"
            )
            modifiedBot = Bot.query.filter_by(id=regularUserBot.id).first()
            assertModified(data, modifiedBot)

        else:
            assert403(response, templates)
            modifiedBot = Bot.query.filter_by(id=regularUserBot.id).first()
            assert modifiedBot == regularUserBot


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_bot_detail_edit_self(
    flask_app_client,
    db,
    loginAs,
    regularUserBot,
    redditApp,
    sentryToken,
    databaseCredential,
):
    data = {
        "itemType": "bots",
        "itemId": f"{regularUserBot.id}",
        "app_name": "newName",
        "reddit_app": f"{redditApp.id}",
        "sentry_token": f"{sentryToken.id}",
        "database_credential": f"{databaseCredential.id}",
        "owner": f"{loginAs.id}",
    }
    regularUserBot.owner = loginAs
    redditApp.owner = loginAs
    sentryToken.owner = loginAs
    databaseCredential.owner = loginAs
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(f"/bots/{regularUserBot.id}", data=data)
        assert202(response)
        assertRenderedTemplate(templates, "edit_bot.html")
        assertMessageFlashed(templates, "Bot 'newName' saved successfully!", "success")
        modifiedBot = Bot.query.filter_by(id=regularUserBot.id).first()
        assertModified(data, modifiedBot)


def test_bot_detail_conflicting_name(
    flask_app_client,
    db,
    regularUserInstance,
    regularUserBot,
    adminUserBot,
    redditApp,
    sentryToken,
    databaseCredential,
):
    original = changeOwner(db, regularUserInstance, adminUserBot)
    original.app_name = "oldBot"
    db.session.merge(original)
    toBeModified = changeOwner(db, regularUserInstance, regularUserBot)
    db.session.merge(toBeModified)
    data = {
        "itemType": "bots",
        "itemId": f"{regularUserBot.id}",
        "app_name": f"{original.app_name}",
        "reddit_app": f"{redditApp.id}",
        "sentry_token": f"{sentryToken.id}",
        "database_credential": f"{databaseCredential.id}",
    }
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(f"/bots/{toBeModified.id}", json=data)
        assert response.status_code == 422
        assert response.mimetype == "text/html"
        assertRenderedTemplate(templates, "edit_bot.html")
        assert (
            templates["templates"][0][1]["form"].errors["app_name"][0]
            == "Already exists."
        )
        modifiedBot = Bot.query.filter_by(id=toBeModified.id).first()
        assert modifiedBot.app_name == toBeModified.app_name
