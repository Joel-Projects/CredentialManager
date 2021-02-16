from flask import request

from app.modules import auth


def test_loading_user_from_anonymous_request(flask_app):
    with flask_app.test_request_context("/"):
        assert auth.loadUserFromRequest(request) is None


def test_loading_user_from_request_with_api_token(flask_app, regularUserApiToken):
    with flask_app.test_request_context(
        path="/", headers={"X-API-TOKEN": regularUserApiToken.token}
    ):
        assert auth.loadUserFromRequest(request) == regularUserApiToken.owner
