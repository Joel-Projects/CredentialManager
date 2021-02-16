import pytest

from app.modules.sentry_tokens.models import SentryToken

testData = {"dsn": "https://12345@sentry.jesassn.org/1"}


@pytest.fixture()
def regularUserSentryToken(temp_db_instance_helper, regular_user):
    for _ in temp_db_instance_helper(
        SentryToken(
            app_name="regular_user_sentry_token", owner=regular_user, **testData
        )
    ):
        yield _


@pytest.fixture()
def adminUserSentryToken(temp_db_instance_helper, admin_user):
    for _ in temp_db_instance_helper(
        SentryToken(app_name="admin_user_sentry_token", owner=admin_user, **testData)
    ):
        yield _


@pytest.fixture()
def internalUserSentryToken(temp_db_instance_helper, internal_user):
    for _ in temp_db_instance_helper(
        SentryToken(
            app_name="internal_user_sentry_token", owner=internal_user, **testData
        )
    ):
        yield _
