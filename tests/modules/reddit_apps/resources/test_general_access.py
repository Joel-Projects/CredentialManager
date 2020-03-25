import pytest


@pytest.mark.parametrize('http_method,http_path', (
        ('GET', '/api/v1/reddit_apps/'),
        ('POST', '/api/v1/reddit_apps/'),
        ('GET', '/api/v1/reddit_apps/1'),
        ('PATCH', '/api/v1/reddit_apps/1'),
        ('DELETE', '/api/v1/reddit_apps/1'),
))
def test_unauthorized_access(http_method, http_path, flask_app_client, regularUserRedditApp):
    response = flask_app_client.open(method=http_method, path=http_path)
    assert response.status_code == 401