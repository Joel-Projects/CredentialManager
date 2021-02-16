import pytest


@pytest.mark.parametrize(
    "method,path,code",
    (
        ("GET", "/api/v1/api_tokens/", 401),
        ("POST", "/api/v1/api_tokens/", 405),
    ),
)
def test_unauthorized_access(method, path, code, flask_app_client):
    response = flask_app_client.open(method=method, path=path)
    assert response.status_code == code
