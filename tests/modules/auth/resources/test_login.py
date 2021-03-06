from base64 import b64encode


def test_regular_user_can_login_with_token(flask_app_client, db, regular_user, regular_user_api_token):
    headers = {"X-API-TOKEN": regular_user_api_token.token}
    response = flask_app_client.get("/api/v1/users/me", headers=headers)

    assert response.status_code == 200

    # Clean up
    from app.modules.api_tokens.models import ApiToken

    with db.session.begin():
        assert ApiToken.query.filter(ApiToken.id == regular_user_api_token.id).delete()


def test_regular_user_cant_login_with_invalid_token(flask_app_client):
    headers = {"X-API-TOKEN": "invalid_token"}
    response = flask_app_client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 401


def test_regular_user_can_login_with_password(flask_app_client, regular_user):
    headers = {
        "Authorization": f'Basic {b64encode(f"{regular_user.username}:{regular_user.password_secret}".encode()).decode("ascii")}'
    }
    response = flask_app_client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 200


def test_regular_user_cant_login_with_invalid_password(flask_app_client, regular_user):
    headers = {
        "Authorization": f'Basic {b64encode(f"{regular_user.username}:invalid_password".encode()).decode("ascii")}'
    }
    response = flask_app_client.get("/api/v1/users/me", headers=headers)
