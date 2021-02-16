import pytest


@pytest.mark.parametrize(
    "method,path",
    (
        ("GET", "/api/v1/bots/"),
        ("POST", "/api/v1/bots/"),
        ("GET", "/api/v1/bots/1"),
        ("PATCH", "/api/v1/bots/1"),
        ("DELETE", "/api/v1/bots/1"),
    ),
)
def test_unauthorized_access(method, path, flask_app_client, regularUserBot):
    response = flask_app_client.open(method=method, path=path)
    assert response.status_code == 401
