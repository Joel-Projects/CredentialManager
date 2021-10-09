from flask import request

from app.modules import auth


def test_loading_user_from_anonymous_request(flask_app):
    with flask_app.test_request_context("/"):
        assert auth.load_user_from_request(request) is None


def test_loading_user_from_request_with_api_token(flask_app, regular_user_api_token):
    with flask_app.test_request_context(path="/", headers={"X-API-TOKEN": regular_user_api_token.token}):
        assert auth.load_user_from_request(request) == regular_user_api_token.owner


def test_loading_user_from_request_with_bad_api_token(flask_app, regular_user_api_token):
    with flask_app.test_request_context(path="/", headers={"X-API-TOKEN": "1234"}):
        assert not auth.load_user_from_request(request) == regular_user_api_token.owner
