import pytest

from app.modules.database_credentials.models import DatabaseCredential
from app.modules.reddit_apps.models import RedditApp
from app.modules.bots.models import Bot
from app.modules.sentry_tokens.models import SentryToken


test_data = {
    'app_name': 'bot'
}

@pytest.fixture()
def regularUserBot(temp_db_instance_helper, regular_user, redditApp, sentryToken, databaseCredential):
    redditApp.owner = regular_user
    sentryToken.owner = regular_user
    databaseCredential.owner = regular_user
    for _ in temp_db_instance_helper(Bot(reddit_app=redditApp, sentry_token=sentryToken, database_credential=databaseCredential, owner=regular_user, **test_data)):
        yield _

@pytest.fixture()
def adminUserBot(temp_db_instance_helper, admin_user, redditApp, sentryToken, databaseCredential):
    redditApp.owner = admin_user
    sentryToken.owner = admin_user
    databaseCredential.owner = admin_user
    for _ in temp_db_instance_helper(Bot(reddit_app=redditApp, sentry_token=sentryToken, database_credential=databaseCredential, owner=admin_user, **test_data)):
        yield _

@pytest.fixture()
def internalUserBot(temp_db_instance_helper, internal_user, redditApp, sentryToken, databaseCredential):
    redditApp.owner = internal_user
    sentryToken.owner = internal_user
    databaseCredential.owner = internal_user
    for _ in temp_db_instance_helper(Bot(reddit_app=redditApp, sentry_token=sentryToken, database_credential=databaseCredential, owner=internal_user, **test_data)):
        yield _

redditAppTestData = {
    'app_name': 'reddit_app',
    'app_description': 'app_description',
    'client_id': 'client_id',
    'client_secret': 'client_secret',
    'user_agent': 'user_agent',
    'app_type': 'web',
    'redirect_uri': 'https://credmgr.jesassn.org/oauth2/reddit_callback'
}

redditAppTestData2 = {
    'app_name': 'reddit_app2',
    'app_description': 'app_description',
    'client_id': 'client_id2',
    'client_secret': 'client_secret',
    'user_agent': 'user_agent',
    'app_type': 'web',
    'redirect_uri': 'https://credmgr.jesassn.org/oauth2/reddit_callback'
}

sentryTokenTestData = {
    'app_name': 'sentry_token',
    'dsn': 'https://12345@sentry.jesassn.org/1'
}

databaseCredentialTestData = {
    'app_name': 'database_credential',
    'database_flavor': 'postgres',
    'database_host': 'localhost',
    'database_port': 5432,
    'database_username': 'postgres',
    'database_password': 'database_password',
    'database': 'postgres',
    'use_ssh': True,
    'ssh_host': 'ssh_host',
    'ssh_port': 22,
    'ssh_username': 'root',
    'ssh_password': 'pass',
    'use_ssh_key': True,
    'private_key': 'private_key',
    'private_key_passphrase': 'passphrase'
}

@pytest.fixture()
def redditApp(temp_db_instance_helper, regular_user):
    for _ in temp_db_instance_helper(RedditApp(owner=regular_user, **redditAppTestData)):
        yield _

@pytest.fixture()
def redditApp2(temp_db_instance_helper, regular_user):
    for _ in temp_db_instance_helper(RedditApp(owner=regular_user, **redditAppTestData2)):
        yield _

@pytest.fixture()
def sentryToken(temp_db_instance_helper, regular_user):
    for _ in temp_db_instance_helper(SentryToken(owner=regular_user, **sentryTokenTestData)):
        yield _

@pytest.fixture()
def databaseCredential(temp_db_instance_helper, regular_user):
    for _ in temp_db_instance_helper(DatabaseCredential(owner=regular_user, **databaseCredentialTestData)):
        yield _
