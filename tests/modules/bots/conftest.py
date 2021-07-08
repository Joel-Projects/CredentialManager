import pytest

from app.modules.bots.models import Bot
from app.modules.database_credentials.models import DatabaseCredential
from app.modules.reddit_apps.models import RedditApp
from app.modules.sentry_tokens.models import SentryToken

test_data = {"app_name": "bot"}


@pytest.fixture()
def regular_user_bot(
    temp_db_instance_helper, regular_user, reddit_app, sentry_token, database_credential
):
    reddit_app.owner = regular_user
    sentry_token.owner = regular_user
    database_credential.owner = regular_user
    for _ in temp_db_instance_helper(
        Bot(
            reddit_app=reddit_app,
            sentry_token=sentry_token,
            database_credential=database_credential,
            owner=regular_user,
            **test_data
        )
    ):
        yield _


@pytest.fixture()
def admin_user_bot(
    temp_db_instance_helper, admin_user, reddit_app, sentry_token, database_credential
):
    reddit_app.owner = admin_user
    sentry_token.owner = admin_user
    database_credential.owner = admin_user
    for _ in temp_db_instance_helper(
        Bot(
            reddit_app=reddit_app,
            sentry_token=sentry_token,
            database_credential=database_credential,
            owner=admin_user,
            **test_data
        )
    ):
        yield _


@pytest.fixture()
def internal_user_bot(
    temp_db_instance_helper,
    internal_user,
    reddit_app,
    sentry_token,
    database_credential,
):
    reddit_app.owner = internal_user
    sentry_token.owner = internal_user
    database_credential.owner = internal_user
    for _ in temp_db_instance_helper(
        Bot(
            reddit_app=reddit_app,
            sentry_token=sentry_token,
            database_credential=database_credential,
            owner=internal_user,
            **test_data
        )
    ):
        yield _


reddit_app_test_data = {
    "app_name": "reddit_app",
    "app_description": "app_description",
    "client_id": "client_id",
    "client_secret": "client_secret",
    "user_agent": "user_agent",
    "app_type": "web",
    "redirect_uri": "https://credmgr.jesassn.org/oauth2/reddit_callback",
}

reddit_app_test_data2 = {
    "app_name": "reddit_app2",
    "app_description": "app_description",
    "client_id": "client_id2",
    "client_secret": "client_secret",
    "user_agent": "user_agent",
    "app_type": "web",
    "redirect_uri": "https://credmgr.jesassn.org/oauth2/reddit_callback",
}

sentry_token_test_data = {
    "app_name": "sentry_token",
    "dsn": "https://12345@sentry.jesassn.org/1",
}

database_credential_test_data = {
    "app_name": "database_credential",
    "database_flavor": "postgres",
    "database_host": "localhost",
    "database_port": 5432,
    "database_username": "postgres",
    "database_password": "database_password",
    "database": "postgres",
    "use_ssh": True,
    "ssh_host": "ssh_host",
    "ssh_port": 22,
    "ssh_username": "root",
    "ssh_password": "pass",
    "use_ssh_key": True,
    "private_key": "private_key",
    "private_key_passphrase": "passphrase",
}


@pytest.fixture()
def reddit_app(temp_db_instance_helper, regular_user):
    for _ in temp_db_instance_helper(
        RedditApp(owner=regular_user, **reddit_app_test_data)
    ):
        yield _


@pytest.fixture()
def reddit_app2(temp_db_instance_helper, regular_user):
    for _ in temp_db_instance_helper(
        RedditApp(owner=regular_user, **reddit_app_test_data2)
    ):
        yield _


@pytest.fixture()
def sentry_token(temp_db_instance_helper, regular_user):
    for _ in temp_db_instance_helper(
        SentryToken(owner=regular_user, **sentry_token_test_data)
    ):
        yield _


@pytest.fixture()
def database_credential(temp_db_instance_helper, regular_user):
    for _ in temp_db_instance_helper(
        DatabaseCredential(owner=regular_user, **database_credential_test_data)
    ):
        yield _
