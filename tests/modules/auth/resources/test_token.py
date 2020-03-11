from base64 import b64encode

import pytest


def test_regular_user_can_login_with_token(flask_app_client, db, regular_user, regularUserApiToken):
    headers = {'X-API-KEY': regularUserApiToken.token}
    response = flask_app_client.get('/api/v1/users/me', headers=headers)

    assert response.status_code == 200

    # Clean up
    from app.modules.api_tokens.models import ApiToken
    with db.session.begin():
        assert ApiToken.query.filter(ApiToken.id == regularUserApiToken.id).delete()

def test_regular_user_cant_login_with_invalid_token(flask_app_client):
    headers = {'X-API-KEY': 'invalid_token'}
    response = flask_app_client.get('/api/v1/users/me', headers=headers)
    assert response.status_code == 401