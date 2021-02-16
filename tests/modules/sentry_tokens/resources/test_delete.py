import pytest

from app.modules.sentry_tokens.models import SentryToken
from tests.params import labels, users
from tests.utils import assert403, assertSuccess


sentryTokensToDelete = [
    pytest.lazy_fixture("adminUserSentryToken"),
    pytest.lazy_fixture("internalUserSentryToken"),
    pytest.lazy_fixture("regularUserSentryToken"),
]


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_deleting_user(flask_app_client, loginAs, regularUserSentryToken):
    response = flask_app_client.delete(
        f"/api/v1/sentry_tokens/{regularUserSentryToken.id}"
    )

    if loginAs.is_admin or loginAs.is_internal:
        assertSuccess(
            response, None, SentryToken, None, deleteItemId=regularUserSentryToken.id
        )
    else:
        assert403(
            response,
            SentryToken,
            oldItem=regularUserSentryToken,
            internal=True,
            action="deleted",
        )


def test_deleting_self(flask_app_client, adminUserInstance, regularUserSentryToken):
    response = flask_app_client.delete(
        f"/api/v1/sentry_tokens/{regularUserSentryToken.id}"
    )
    assertSuccess(
        response, None, SentryToken, None, deleteItemId=regularUserSentryToken.id
    )
