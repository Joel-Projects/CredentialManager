import pytest

from app.modules.sentry_tokens.models import SentryToken

test_data = {"dsn": "https://12345@sentry.jesassn.org/1"}


@pytest.fixture()
def regular_user_sentry_token(temp_db_instance_helper, regular_user):
    for _ in temp_db_instance_helper(
        SentryToken(
            app_name="regular_user_sentry_token", owner=regular_user, **test_data
        )
    ):
        yield _


@pytest.fixture()
def admin_user_sentry_token(temp_db_instance_helper, admin_user):
    for _ in temp_db_instance_helper(
        SentryToken(app_name="admin_user_sentry_token", owner=admin_user, **test_data)
    ):
        yield _


@pytest.fixture()
def internal_user_sentry_token(temp_db_instance_helper, internal_user):
    for _ in temp_db_instance_helper(
        SentryToken(
            app_name="internal_user_sentry_token", owner=internal_user, **test_data
        )
    ):
        yield _
