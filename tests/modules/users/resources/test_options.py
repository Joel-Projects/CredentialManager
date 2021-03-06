import pytest


@pytest.mark.parametrize(
    "path,status_code,expected_allowed_methods",
    (
        ("/api/v1/users/", 401, None),
        ("/api/v1/users/1", 401, None),
    ),
)
def test_users_options_unauthorized(path, status_code, expected_allowed_methods, flask_app_client):
    response = flask_app_client.options(path)

    assert response.status_code == status_code


@pytest.mark.parametrize(
    "path,test_user,expected_allowed_methods",
    (
        ("/api/v1/users/{id}", None, {"OPTIONS"}),
        ("/api/v1/users/{id}", "regular_user", {"OPTIONS", "PATCH", "GET"}),
    ),
)
def test_users_options_authorized(path, test_user, expected_allowed_methods, flask_app_client, regular_user):
    user_id = ""
    if test_user == "regular_user":
        user_id = regular_user.id
    with flask_app_client.login(regular_user):
        response = flask_app_client.options(path.format(id=user_id))

    assert response.status_code == 204
    assert set(response.headers["Allow"].split(", ")) == expected_allowed_methods
