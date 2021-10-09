import pytest


@pytest.mark.parametrize(
    "path,status_code",
    (
        ("/api/v1/bots/", 401),
        ("/api/v1/bots/1", 401),
    ),
)
def test_bots_options_unauthorized(path, status_code, flask_app_client):
    response = flask_app_client.options(path)

    assert response.status_code == status_code


@pytest.mark.parametrize(
    "path,expected_allowed_methods",
    (
        ("/api/v1/bots/", {"GET", "POST", "OPTIONS"}),
        ("/api/v1/bots/1", {"GET", "OPTIONS", "PATCH", "DELETE"}),
        ("/api/v1/bots/2", {"OPTIONS"}),
    ),
)
def test_bots_options_authorized(
    path,
    expected_allowed_methods,
    flask_app_client,
    regular_user,
    regular_user_bot,
    admin_user_bot,
):
    with flask_app_client.login(regular_user):
        response = flask_app_client.options(path)

    assert response.status_code == 204
    assert set(response.headers["Allow"].split(", ")) == expected_allowed_methods


@pytest.mark.parametrize("path,expected_allowed_methods", (("/api/v1/bots/", {"GET", "POST", "OPTIONS"}),))
def test_preflight_options_request(path, expected_allowed_methods, flask_app_client):
    response = flask_app_client.open(method="OPTIONS", path=path, headers={"Access-Control-Request-Method": "post"})
    assert response.status_code == 200
    assert set(response.headers["Access-Control-Allow-Methods"].split(", ")) == expected_allowed_methods
