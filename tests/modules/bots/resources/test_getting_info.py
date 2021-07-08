import pytest

from tests.params import labels, users

content_type = "application/json"


def assert_content(response):
    assert response.content_type == content_type
    assert set(response.json.keys()) >= {"status", "message"}


def assert403(response):
    assert response.status_code == 403
    assert_content(response)


def test_getting_list_of_bots_by_anonymous_user(flask_app_client):
    response = flask_app_client.get("/api/v1/bots/")

    assert response.status_code == 401
    assert_content(response)


def test_getting_list_of_bots_by_authorized_user(
    flask_app_client, regular_user, regular_user_bot, admin_user_bot
):
    with flask_app_client.login(regular_user):
        response = flask_app_client.get("/api/v1/bots/")

    assert response.status_code == 200
    assert response.content_type == content_type
    assert isinstance(response.json, list)
    assert len(response.json) == 1
    assert set(response.json[0].keys()) >= {"id", "app_name"}
    assert response.json[0]["app_name"] == regular_user_bot.app_name


def test_getting_bot_info_by_unauthorized_user_must_fail(
    flask_app_client, regular_user_instance, regular_user_bot
):
    response = flask_app_client.get(f"/api/v1/bots/{regular_user_bot.id}")

    assert403(response)


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_getting_bot_info(flask_app_client, login_as, regular_user_bot):
    response = flask_app_client.get(f"/api/v1/bots/{regular_user_bot.id}")

    if login_as.is_admin or login_as.is_internal:
        assert response.status_code == 200
        assert response.content_type == content_type
        assert set(response.json.keys()) >= {"id", "app_name"}
        assert response.json["id"] == regular_user_bot.id
        assert response.json["app_name"] == regular_user_bot.app_name
    else:
        assert403(response)


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_getting_bot_info_disabled(flask_app_client, login_as, regular_user_bot):
    regular_user_bot.enabled = False
    response = flask_app_client.get(f"/api/v1/bots/{regular_user_bot.id}")

    if login_as.is_admin or login_as.is_internal:
        assert response.status_code == 424
    else:
        assert403(response)


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_getting_bot_info_disabled_apps(flask_app_client, login_as, regular_user_bot):
    regular_user_bot.enabled = True
    regular_user_bot.reddit_app.enabled = False
    if not (login_as.is_admin or login_as.is_internal):
        regular_user_bot.owner = login_as
    response = flask_app_client.get(f"/api/v1/bots/{regular_user_bot.id}")

    assert response.status_code == 424


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_getting_bot_info_by_name(flask_app_client, login_as, regular_user_bot):
    response = flask_app_client.post(
        f"/api/v1/bots/by_name", data={"app_name": regular_user_bot.app_name}
    )

    if login_as.is_admin or login_as.is_internal:
        assert response.status_code == 200
        assert response.content_type == content_type
        assert set(response.json.keys()) >= {"id", "app_name"}
        assert response.json["id"] == regular_user_bot.id
        assert response.json["app_name"] == regular_user_bot.app_name
    else:
        assert response.status_code == 404
