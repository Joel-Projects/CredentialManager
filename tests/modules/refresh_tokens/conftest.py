import json
import os
import socket
from base64 import b64encode
from sys import platform

import betamax
import pytest
from betamax import Betamax
from betamax.cassette.cassette import dispatch_hooks
from betamax_serializers import pretty_json
from praw import Reddit

from app.modules.reddit_apps.models import RedditApp
from app.modules.refresh_tokens.models import RefreshToken
from app.modules.user_verifications.models import UserVerification


def b64_string(input_string):
    return b64encode(input_string.encode("utf-8")).decode("utf-8")


def env_default(key):
    return os.environ.get(f"test_{key}", f"placeholder_{key}")


def filter_access_token(interaction, current_cassette):  # pragma: no cover
    response = interaction.data["response"]
    body = response["body"]["string"]
    try:
        access_token = json.loads(body)["access_token"]
    except (KeyError, TypeError, ValueError):
        return
    access_token_placeholder = betamax.cassette.cassette.Placeholder(
        placeholder="<ACCESS_TOKEN>", replace=access_token
    )
    current_cassette.placeholders.append(access_token_placeholder)


def filter_refresh_token(interaction, current_cassette):  # pragma: no cover
    response = interaction.data["response"]
    body = response["body"]["string"]
    try:
        refresh_token = json.loads(body)["refresh_token"]
    except (KeyError, TypeError, ValueError):
        return
    refresh_token_placeholder = betamax.cassette.cassette.Placeholder(
        placeholder="<REFRESH_TOKEN>", replace=refresh_token
    )
    current_cassette.placeholders.append(refresh_token_placeholder)


os.environ["praw_check_for_updates"] = "False"

placeholders = {
    x: env_default(x)
    for x in [
        "auth_code",
        "client_id",
        "client_secret",
        "password",
        "redirect_uri",
        "test_subreddit",
        "user_agent",
        "username",
        "refresh_token",
    ]
}

placeholders["basic_auth"] = b64_string(
    f'{placeholders["client_id"]}:{placeholders["client_secret"]}'
)

betamax.Betamax.register_serializer(pretty_json.PrettyJSONSerializer)
with betamax.Betamax.configure() as config:
    config.cassette_library_dir = f"{os.path.dirname(__file__)}/cassettes"
    config.default_cassette_options["serialize_with"] = "prettyjson"
    config.before_record(callback=filter_access_token)
    config.before_record(callback=filter_refresh_token)
    for key, value in placeholders.items():
        config.define_cassette_placeholder(f"<{key.upper()}>", value)


class Placeholders:
    def __init__(self, _dict):
        self.__dict__ = _dict


def pytest_configure():
    pytest.placeholders = Placeholders(placeholders)


if platform == "darwin":
    socket.gethostbyname = lambda x: "127.0.0.1"


@pytest.fixture()
def reddit():
    kwargs = {
        "client_id": pytest.placeholders.client_id,
        "client_secret": pytest.placeholders.client_secret,
        "redirect_uri": pytest.placeholders.redirect_uri,
        "user_agent": pytest.placeholders.user_agent,
        "username": None,
    }
    yield Reddit(**kwargs)


@pytest.fixture()
def recorder(reddit):
    http = reddit._core._requestor._http
    http.headers["Accept-Encoding"] = "identity"
    yield Betamax(http)


test_data = {
    "refresh_token": "refresh_token",
    "scopes": [
        "edit",
        "vote",
        "modwiki",
        "modflair",
        "creddits",
        "modconfig",
        "history",
        "modtraffic",
        "modmail",
        "modposts",
        "read",
        "identity",
        "report",
        "privatemessages",
        "modothers",
        "modlog",
        "structuredstyles",
        "wikiedit",
        "subscribe",
        "modself",
        "save",
        "submit",
        "flair",
        "wikiread",
        "account",
        "mysubreddits",
        "livemanage",
        "modcontributors",
    ],
}


@pytest.fixture()
def regular_user_refresh_token(temp_db_instance_helper, reddit_app, regular_user):
    reddit_app.owner = regular_user
    for _ in temp_db_instance_helper(
        RefreshToken(
            redditor="regular_redditor",
            refresh_token="regular",
            reddit_app=reddit_app,
            owner=regular_user,
        )
    ):
        yield _


@pytest.fixture()
def admin_user_refresh_token(temp_db_instance_helper, reddit_app, admin_user):
    reddit_app.owner = admin_user
    for _ in temp_db_instance_helper(
        RefreshToken(
            redditor="admin_redditor",
            refresh_token="admin",
            reddit_app=reddit_app,
            owner=admin_user,
        )
    ):
        yield _


@pytest.fixture()
def internal_user_refresh_token(temp_db_instance_helper, reddit_app, internal_user):
    reddit_app.owner = internal_user
    for _ in temp_db_instance_helper(
        RefreshToken(
            redditor="internal_redditor",
            refresh_token="internal",
            reddit_app=reddit_app,
            owner=internal_user,
        )
    ):
        yield _


reddit_app_data = {
    "app_description": "app_description",
    "client_id": "client_id",
    "client_secret": "client_secret",
    "user_agent": "user_agent",
    "app_type": "web",
    "redirect_uri": "https://credmgr.jesassn.org/oauth2/reddit_callback",
}


@pytest.fixture()
def reddit_app(temp_db_instance_helper, regular_user):
    for _ in temp_db_instance_helper(
        RedditApp(
            app_name="regular_user_reddit_app", owner=regular_user, **reddit_app_data
        )
    ):
        yield _


@pytest.fixture()
def regular_user_user_verification(temp_db_instance_helper, regular_user, reddit_app):
    for _ in temp_db_instance_helper(
        UserVerification(
            reddit_app=reddit_app, owner=regular_user, user_id="123456789012345678"
        )
    ):
        yield _
