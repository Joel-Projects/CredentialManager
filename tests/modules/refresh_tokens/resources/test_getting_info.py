import pytest

from tests.params import labels, users

content_type = "application/json"


def assert_content(response):
    assert response.content_type == content_type
    assert set(response.json.keys()) >= {"status", "message"}


def assert403(response):
    assert response.status_code == 403
    assert_content(response)


def test_getting_list_of_refresh_tokens_by_anonymous_user(flask_app_client):
    response = flask_app_client.get("/api/v1/refresh_tokens/")

    assert response.status_code == 401
    assert_content(response)


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_getting_list_of_refresh_tokens(
    flask_app_client,
    login_as,
    regular_user_refresh_token,
    admin_user_refresh_token,
    internal_user_refresh_token,
):
    if not (login_as.is_admin and login_as.is_internal):
        regular_user_refresh_token.owner = login_as
    response = flask_app_client.get("/api/v1/refresh_tokens/")

    assert response.status_code == 200
    assert response.content_type == content_type
    assert isinstance(response.json, list)
    if not (login_as.is_admin or login_as.is_internal):
        assert len(response.json) == 1
    elif login_as.is_internal:
        assert len(response.json) == 3
    else:
        assert len(response.json) == 2
    assert set(response.json[0].keys()) >= {"id", "redditor", "refresh_token"}


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_getting_list_of_refresh_tokens_owner_id(
    flask_app_client, login_as, regular_user_refresh_token, admin_user_refresh_token
):

    response = flask_app_client.get("/api/v1/refresh_tokens/?owner_id=2")
    if not (login_as.is_admin or login_as.is_internal):
        assert403(response)
    else:
        assert response.status_code == 200
        assert response.content_type == content_type
        assert isinstance(response.json, list)
        assert len(response.json) == 1
        assert set(response.json[0].keys()) >= {"id", "redditor", "refresh_token"}
        assert response.json[0]["redditor"] == regular_user_refresh_token.redditor
        assert response.json[0]["refresh_token"] == regular_user_refresh_token.refresh_token


def test_getting_refresh_token_info_by_unauthorized_user_must_fail(
    flask_app_client, regular_user_instance, regular_user_refresh_token
):
    response = flask_app_client.get(f"/api/v1/refresh_tokens/{regular_user_refresh_token.id}")

    assert403(response)


def assert_success(token, response):
    assert response.status_code == 200
    assert response.content_type == content_type
    assert set(response.json.keys()) >= {"id", "redditor", "refresh_token"}
    assert response.json["id"] == token.id
    assert response.json["redditor"] == token.redditor
    assert response.json["refresh_token"] == token.refresh_token


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_getting_refresh_token_info(flask_app_client, login_as, regular_user_refresh_token):
    response = flask_app_client.get(f"/api/v1/refresh_tokens/{regular_user_refresh_token.id}")

    if login_as.is_admin or login_as.is_internal:
        assert_success(regular_user_refresh_token, response)
    else:
        assert403(response)


refresh_tokens = [
    pytest.lazy_fixture("admin_user_refresh_token"),
    pytest.lazy_fixture("internal_user_refresh_token"),
    pytest.lazy_fixture("regular_user_refresh_token"),
]


@pytest.mark.parametrize("login_as", users, ids=labels)
@pytest.mark.parametrize("refresh_token", refresh_tokens)
def test_getting_refresh_token_info_by_redditor(flask_app_client, login_as, refresh_token):
    response = flask_app_client.post(
        f"/api/v1/refresh_tokens/by_redditor",
        data={
            "reddit_app_id": refresh_token.reddit_app.id,
            "redditor": refresh_token.redditor,
        },
    )

    if login_as.is_internal or login_as == refresh_token.owner:
        assert_success(refresh_token, response)
    elif login_as.is_admin:
        if refresh_token.owner.is_internal:
            assert403(response)
        else:
            assert_success(refresh_token, response)
    else:
        assert403(response)


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_getting_refresh_token_info_by_redditor_by_self(flask_app_client, login_as, regular_user_refresh_token):
    regular_user_refresh_token.owner = login_as
    regular_user_refresh_token.reddit_app.owner = login_as
    response = flask_app_client.post(
        f"/api/v1/refresh_tokens/by_redditor",
        data={
            "reddit_app_id": regular_user_refresh_token.reddit_app.id,
            "redditor": regular_user_refresh_token.redditor,
        },
    )

    assert_success(regular_user_refresh_token, response)
