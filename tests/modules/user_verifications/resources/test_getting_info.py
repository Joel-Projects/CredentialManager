import pytest

from tests.params import labels, users

content_type = "application/json"


def assert_content(response):
    assert response.content_type == content_type
    assert set(response.json.keys()) >= {"status", "message"}


def assert403(response):
    assert response.status_code == 403
    assert_content(response)


def test_getting_list_of_user_verifications_by_anonymous_user(flask_app_client):
    response = flask_app_client.get("/api/v1/user_verifications/")

    assert response.status_code == 401
    assert_content(response)


def test_getting_list_of_user_verifications_by_authorized_user(
    flask_app_client,
    regular_user,
    regular_user_user_verification,
    admin_user_user_verification,
):
    with flask_app_client.login(regular_user):
        response = flask_app_client.get("/api/v1/user_verifications/")
    assert response.status_code == 200
    assert response.content_type == content_type
    assert isinstance(response.json, list)
    assert len(response.json) == 1
    assert set(response.json[0].keys()) >= {"id", "user_id"}
    assert response.json[0]["user_id"] == regular_user_user_verification.user_id


def test_getting_user_verification_info_by_unauthorized_user_must_fail(
    flask_app_client, regular_user_instance, regular_user_user_verification
):
    response = flask_app_client.get(f"/api/v1/user_verifications/{regular_user_user_verification.id}")

    assert403(response)


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_getting_user_verification_info(flask_app_client, login_as, regular_user_user_verification):
    response = flask_app_client.get(f"/api/v1/user_verifications/{regular_user_user_verification.id}")

    if login_as.is_admin or login_as.is_internal:
        assert response.status_code == 200
        assert response.content_type == content_type
        assert set(response.json.keys()) >= {"id", "user_id"}
        assert response.json["id"] == regular_user_user_verification.id
        assert response.json["user_id"] == regular_user_user_verification.user_id
    else:
        assert403(response)


def test_getting_redditor_from_user_id(flask_app_client, regular_user_instance, admin_user_user_verification):
    response = flask_app_client.post(
        "/api/v1/user_verifications/get_redditor",
        data={"user_id": "123456789012345679"},
    )

    assert response.status_code == 200
    assert response.content_type == content_type
    assert set(response.json.keys()) >= {"id", "redditor"}
    assert response.json["redditor"] == admin_user_user_verification.redditor


def test_getting_redditor_from_user_id_disabled(flask_app_client, regular_user_instance, admin_user_user_verification):
    admin_user_user_verification.enabled = False
    response = flask_app_client.post(
        "/api/v1/user_verifications/get_redditor",
        data={"user_id": "123456789012345679"},
    )

    assert response.status_code == 424


def test_getting_redditor_from_user_id_with_reddit_app(
    flask_app_client, regular_user_instance, admin_user_user_verification, reddit_app
):
    admin_user_user_verification.reddit_app = reddit_app
    response = flask_app_client.post(
        "/api/v1/user_verifications/get_redditor",
        data={"user_id": "123456789012345679", "reddit_app_id": reddit_app.id},
    )

    assert response.status_code == 200
    assert response.content_type == content_type
    assert set(response.json.keys()) >= {"id", "redditor"}
    assert response.json["redditor"] == admin_user_user_verification.redditor


def test_getting_redditor_from_non_existent_redditor_with_bad_reddit_app(
    flask_app_client, regular_user_instance, admin_user_user_verification, reddit_app
):
    admin_user_user_verification.reddit_app = reddit_app
    response = flask_app_client.post(
        "/api/v1/user_verifications/get_redditor",
        data={"user_id": "123456789012345679", "reddit_app_id": 2},
    )

    assert response.status_code == 404


def test_getting_redditor_from_non_existent_user_id(flask_app_client, regular_user_instance):
    response = flask_app_client.post(
        "/api/v1/user_verifications/get_redditor",
        data={"user_id": "123456789012345678"},
    )

    assert response.status_code == 404
