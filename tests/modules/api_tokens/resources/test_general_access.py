import pytest


@pytest.mark.parametrize('http_method,http_path', (
        ('GET', '/api/v1/api_tokens/'),
        ('POST', '/api/v1/api_tokens/'),
))
def test_unauthorized_access(http_method, http_path, flask_app_client):
    response = flask_app_client.open(method=http_method, path=http_path)
    assert response.status_code == 401