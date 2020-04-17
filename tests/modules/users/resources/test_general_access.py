import pytest


@pytest.mark.parametrize('method,path', (
        ('GET', '/api/v1/users/'),
        ('GET', '/api/v1/users/1'),
        ('PATCH', '/api/v1/users/1'),
        ('DELETE', '/api/v1/users/1'),
        ('GET', '/api/v1/users/me'),
))
def test_unauthorized_access(method, path, flask_app_client, regular_user):
    response = flask_app_client.open(method=method, path=path)
    assert response.status_code == 401