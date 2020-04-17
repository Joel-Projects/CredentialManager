import pytest


@pytest.mark.parametrize('method,path', (
        ('GET', '/api/v1/refresh_tokens/'),
        ('GET', '/api/v1/refresh_tokens/1'),
        ('DELETE', '/api/v1/refresh_tokens/1'),
))
def test_unauthorized_access(method, path, flask_app_client, regularUserRefreshToken):
    response = flask_app_client.open(method=method, path=path)
    assert response.status_code == 401