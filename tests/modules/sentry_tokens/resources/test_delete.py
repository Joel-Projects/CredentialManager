import pytest

from app.modules.sentry_tokens.models import SentryToken
from tests.params import labels, users
from tests.utils import assert403, assert_success

sentry_tokens_to_delete = [
    pytest.lazy_fixture("admin_user_sentry_token"),
    pytest.lazy_fixture("internal_user_sentry_token"),
    pytest.lazy_fixture("regular_user_sentry_token"),
]


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_deleting_user(flask_app_client, login_as, regular_user_sentry_token):
    response = flask_app_client.delete(
        f"/api/v1/sentry_tokens/{regular_user_sentry_token.id}"
    )

    if login_as.is_admin or login_as.is_internal:
        assert_success(
            response,
            None,
            SentryToken,
            None,
            delete_item_id=regular_user_sentry_token.id,
        )
    else:
        assert403(
            response,
            SentryToken,
            old_item=regular_user_sentry_token,
            internal=True,
            action="deleted",
        )


def test_deleting_self(
    flask_app_client, admin_user_instance, regular_user_sentry_token
):
    response = flask_app_client.delete(
        f"/api/v1/sentry_tokens/{regular_user_sentry_token.id}"
    )
    assert_success(
        response, None, SentryToken, None, delete_item_id=regular_user_sentry_token.id
    )
