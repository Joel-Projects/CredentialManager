import pytest

from tests.params import labels, users

contentType = "application/json"


def assertContent(response):
    assert response.content_type == contentType
    assert set(response.json.keys()) >= {"status", "message"}


def assert403(response):
    assert response.status_code == 403
    assertContent(response)


def test_getting_list_of_refresh_tokens_by_anonymous_user(flask_app_client):
    response = flask_app_client.get("/api/v1/refresh_tokens/")

    assert response.status_code == 401
    assertContent(response)


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_getting_list_of_refresh_tokens(
    flask_app_client,
    loginAs,
    regularUserRefreshToken,
    adminUserRefreshToken,
    internalUserRefreshToken,
):
    if not (loginAs.is_admin and loginAs.is_internal):
        regularUserRefreshToken.owner = loginAs
    response = flask_app_client.get("/api/v1/refresh_tokens/")

    assert response.status_code == 200
    assert response.content_type == contentType
    assert isinstance(response.json, list)
    if not (loginAs.is_admin or loginAs.is_internal):
        assert len(response.json) == 1
    elif loginAs.is_internal:
        assert len(response.json) == 3
    else:
        assert len(response.json) == 2
    assert set(response.json[0].keys()) >= {"id", "redditor", "refresh_token"}


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_getting_list_of_refresh_tokens_owner_id(
    flask_app_client, loginAs, regularUserRefreshToken, adminUserRefreshToken
):

    response = flask_app_client.get("/api/v1/refresh_tokens/?owner_id=2")
    if not (loginAs.is_admin or loginAs.is_internal):
        assert403(response)
    else:
        assert response.status_code == 200
        assert response.content_type == contentType
        assert isinstance(response.json, list)
        assert len(response.json) == 1
        assert set(response.json[0].keys()) >= {"id", "redditor", "refresh_token"}
        assert response.json[0]["redditor"] == regularUserRefreshToken.redditor
        assert (
            response.json[0]["refresh_token"] == regularUserRefreshToken.refresh_token
        )


def test_getting_refresh_token_info_by_unauthorized_user_must_fail(
    flask_app_client, regularUserInstance, regularUserRefreshToken
):
    response = flask_app_client.get(
        f"/api/v1/refresh_tokens/{regularUserRefreshToken.id}"
    )

    assert403(response)


def assertSuccess(token, response):
    assert response.status_code == 200
    assert response.content_type == contentType
    assert set(response.json.keys()) >= {"id", "redditor", "refresh_token"}
    assert response.json["id"] == token.id
    assert response.json["redditor"] == token.redditor
    assert response.json["refresh_token"] == token.refresh_token


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_getting_refresh_token_info(flask_app_client, loginAs, regularUserRefreshToken):
    response = flask_app_client.get(
        f"/api/v1/refresh_tokens/{regularUserRefreshToken.id}"
    )

    if loginAs.is_admin or loginAs.is_internal:
        assertSuccess(regularUserRefreshToken, response)
    else:
        assert403(response)


refreshTokens = [
    pytest.lazy_fixture("adminUserRefreshToken"),
    pytest.lazy_fixture("internalUserRefreshToken"),
    pytest.lazy_fixture("regularUserRefreshToken"),
]


@pytest.mark.parametrize("loginAs", users, ids=labels)
@pytest.mark.parametrize("refreshToken", refreshTokens)
def test_getting_refresh_token_info_by_redditor(
    flask_app_client, loginAs, refreshToken
):
    response = flask_app_client.post(
        f"/api/v1/refresh_tokens/by_redditor",
        data={
            "reddit_app_id": refreshToken.reddit_app.id,
            "redditor": refreshToken.redditor,
        },
    )

    if loginAs.is_internal or loginAs == refreshToken.owner:
        assertSuccess(refreshToken, response)
    elif loginAs.is_admin:
        if refreshToken.owner.is_internal:
            assert403(response)
        else:
            assertSuccess(refreshToken, response)
    else:
        assert403(response)


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_getting_refresh_token_info_by_redditor_by_self(
    flask_app_client, loginAs, regularUserRefreshToken
):
    regularUserRefreshToken.owner = loginAs
    regularUserRefreshToken.reddit_app.owner = loginAs
    response = flask_app_client.post(
        f"/api/v1/refresh_tokens/by_redditor",
        data={
            "reddit_app_id": regularUserRefreshToken.reddit_app.id,
            "redditor": regularUserRefreshToken.redditor,
        },
    )

    assertSuccess(regularUserRefreshToken, response)
