import pytest


@pytest.mark.parametrize('method,path', (
        ('GET', '/api/v1/sentry_tokens/'),
        ('POST', '/api/v1/sentry_tokens/'),
        ('GET', '/api/v1/sentry_tokens/1'),
        ('PATCH', '/api/v1/sentry_tokens/1'),
        ('DELETE', '/api/v1/sentry_tokens/1'),
))
def test_unauthorized_access(method, path, flask_app_client, regularUserSentryToken):
    response = flask_app_client.open(method=method, path=path)
    assert response.status_code == 401