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


def filterAccessToken(interaction, current_cassette):  # pragma: no cover
    response = interaction.data["response"]
    body = response["body"]["string"]
    try:
        accessToken = json.loads(body)["access_token"]
    except (KeyError, TypeError, ValueError):
        return
    accessTokenPlaceholder = betamax.cassette.cassette.Placeholder(
        placeholder="<ACCESS_TOKEN>", replace=accessToken
    )
    current_cassette.placeholders.append(accessTokenPlaceholder)


def filterRefreshToken(interaction, current_cassette):  # pragma: no cover
    response = interaction.data["response"]
    body = response["body"]["string"]
    try:
        refreshToken = json.loads(body)["refresh_token"]
    except (KeyError, TypeError, ValueError):
        return
    refreshTokenPlaceholder = betamax.cassette.cassette.Placeholder(
        placeholder="<REFRESH_TOKEN>", replace=refreshToken
    )
    current_cassette.placeholders.append(refreshTokenPlaceholder)


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
    config.before_record(callback=filterAccessToken)
    config.before_record(callback=filterRefreshToken)
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
def regularUserRefreshToken(temp_db_instance_helper, redditApp, regular_user):
    redditApp.owner = regular_user
    for _ in temp_db_instance_helper(
        RefreshToken(
            redditor="regularRedditor",
            refresh_token="regular",
            reddit_app=redditApp,
            owner=regular_user,
        )
    ):
        yield _


@pytest.fixture()
def adminUserRefreshToken(temp_db_instance_helper, redditApp, admin_user):
    redditApp.owner = admin_user
    for _ in temp_db_instance_helper(
        RefreshToken(
            redditor="adminRedditor",
            refresh_token="admin",
            reddit_app=redditApp,
            owner=admin_user,
        )
    ):
        yield _


@pytest.fixture()
def internalUserRefreshToken(temp_db_instance_helper, redditApp, internal_user):
    redditApp.owner = internal_user
    for _ in temp_db_instance_helper(
        RefreshToken(
            redditor="internalRedditor",
            refresh_token="internal",
            reddit_app=redditApp,
            owner=internal_user,
        )
    ):
        yield _


redditAppData = {
    "app_description": "app_description",
    "client_id": "client_id",
    "client_secret": "client_secret",
    "user_agent": "user_agent",
    "app_type": "web",
    "redirect_uri": "https://credmgr.jesassn.org/oauth2/reddit_callback",
}


@pytest.fixture()
def redditApp(temp_db_instance_helper, regular_user):
    for _ in temp_db_instance_helper(
        RedditApp(
            app_name="regular_user_reddit_app", owner=regular_user, **redditAppData
        )
    ):
        yield _


@pytest.fixture()
def regularUserUserVerification(temp_db_instance_helper, regular_user, redditApp):
    for _ in temp_db_instance_helper(
        UserVerification(
            reddit_app=redditApp, owner=regular_user, user_id="123456789012345678"
        )
    ):
        yield _
