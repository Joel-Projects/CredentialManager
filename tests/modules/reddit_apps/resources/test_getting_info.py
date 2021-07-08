import pytest

from tests.params import labels, users

content_type = "application/json"


def assert_content(response):
    assert response.content_type == content_type
    assert set(response.json.keys()) >= {"status", "message"}


def assert403(response):
    assert response.status_code == 403
    assert_content(response)


def test_getting_list_of_reddit_apps_by_anonymous_user(flask_app_client):
    response = flask_app_client.get("/api/v1/reddit_apps/")

    assert response.status_code == 401
    assert_content(response)


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_getting_list_of_reddit_apps(
    flask_app_client,
    login_as,
    regular_user_reddit_app,
    admin_user_reddit_app,
    internal_user_reddit_app,
):
    if not (login_as.is_admin and login_as.is_internal):
        regular_user_reddit_app.owner = login_as
    response = flask_app_client.get("/api/v1/reddit_apps/")

    assert response.status_code == 200
    assert response.content_type == content_type
    assert isinstance(response.json, list)
    if not (login_as.is_admin or login_as.is_internal):
        assert len(response.json) == 1
    elif login_as.is_internal:
        assert len(response.json) == 3
    else:
        assert len(response.json) == 2
    assert set(response.json[0].keys()) >= {"id", "app_name"}


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_getting_list_of_reddit_apps_owner_id(
    flask_app_client, login_as, regular_user_reddit_app, admin_user_reddit_app
):

    response = flask_app_client.get("/api/v1/reddit_apps/?owner_id=2")
    if not (login_as.is_admin or login_as.is_internal):
        assert403(response)
    else:
        assert response.status_code == 200
        assert response.content_type == content_type
        assert isinstance(response.json, list)
        assert len(response.json) == 1
        assert set(response.json[0].keys()) >= {"id", "app_name"}
        assert response.json[0]["app_name"] == regular_user_reddit_app.app_name


def test_getting_reddit_app_info_by_unauthorized_user_must_fail(
    flask_app_client, regular_user_instance, regular_user_reddit_app
):
    response = flask_app_client.get(f"/api/v1/reddit_apps/{regular_user_reddit_app.id}")

    assert403(response)


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_getting_reddit_app_info(flask_app_client, login_as, regular_user_reddit_app):
    response = flask_app_client.get(f"/api/v1/reddit_apps/{regular_user_reddit_app.id}")

    if login_as.is_admin or login_as.is_internal:
        assert response.status_code == 200
        assert response.content_type == content_type
        assert set(response.json.keys()) >= {"id", "app_name"}
        assert response.json["id"] == regular_user_reddit_app.id
        assert response.json["app_name"] == regular_user_reddit_app.app_name
    else:
        assert403(response)


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_getting_refresh_token_from_redditor(
    flask_app_client, login_as, regular_user_reddit_app, regular_user_refresh_token
):
    if not (login_as.is_admin and login_as.is_internal):
        regular_user_reddit_app.owner = regular_user_refresh_token.owner = login_as
    response = flask_app_client.post(
        f"/api/v1/reddit_apps/{regular_user_reddit_app.id}",
        data={"redditor": "redditor"},
    )

    assert response.status_code == 200
    assert response.content_type == content_type
    assert set(response.json.keys()) >= {
        "id",
        "reddit_app_id",
        "redditor",
        "refresh_token",
    }
    assert response.json["reddit_app_id"] == regular_user_reddit_app.id
    assert response.json["redditor"] == regular_user_refresh_token.redditor
    assert response.json["refresh_token"] == regular_user_refresh_token.refresh_token


def test_getting_refresh_token_from_non_existant_redditor(
    flask_app_client, regular_user_instance, regular_user_reddit_app
):
    regular_user_reddit_app.owner = regular_user_instance
    response = flask_app_client.post(
        f"/api/v1/reddit_apps/{regular_user_reddit_app.id}",
        data={"redditor": "redditor"},
    )

    assert response.status_code == 404
