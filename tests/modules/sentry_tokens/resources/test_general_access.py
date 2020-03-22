import pytest


@pytest.mark.parametrize('http_method,http_path', (
        ('GET', '/api/v1/sentry_tokens/'),
        ('POST', '/api/v1/sentry_tokens/'),
        ('GET', '/api/v1/sentry_tokens/1'),
        ('PATCH', '/api/v1/sentry_tokens/1'),
        ('DELETE', '/api/v1/sentry_tokens/1'),
))
def test_unauthorized_access(http_method, http_path, flask_app_client, regularUserSentryToken):
    response = flask_app_client.open(method=http_method, path=http_path)
    assert response.status_code == 401