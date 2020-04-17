import pytest


@pytest.mark.parametrize('method,path', (
        ('GET', '/api/v1/reddit_apps/'),
        ('POST', '/api/v1/reddit_apps/'),
        ('GET', '/api/v1/reddit_apps/1'),
        ('PATCH', '/api/v1/reddit_apps/1'),
        ('DELETE', '/api/v1/reddit_apps/1'),
))
def test_unauthorized_access(method, path, flask_app_client, regularUserRedditApp):
    response = flask_app_client.open(method=method, path=path)
    assert response.status_code == 401