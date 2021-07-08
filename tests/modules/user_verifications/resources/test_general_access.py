import pytest


@pytest.mark.parametrize(
    "method,path",
    (
        ("GET", "/api/v1/user_verifications/"),
        ("POST", "/api/v1/user_verifications/"),
        ("GET", "/api/v1/user_verifications/1"),
        ("PATCH", "/api/v1/user_verifications/1"),
        ("DELETE", "/api/v1/user_verifications/1"),
    ),
)
def test_unauthorized_access(
    method, path, flask_app_client, regular_user_user_verification
):
    response = flask_app_client.open(method=method, path=path)
    assert response.status_code == 401
