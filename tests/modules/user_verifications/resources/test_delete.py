import pytest

from app.modules.user_verifications.models import UserVerification
from tests.params import labels, users
from tests.utils import assert403, assert_success

UserVerificationsToDelete = [
    pytest.lazy_fixture("admin_user_user_verification"),
    pytest.lazy_fixture("internal_user_user_verification"),
    pytest.lazy_fixture("regular_user_user_verification"),
]


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_deleting_user(flask_app_client, login_as, regular_user_user_verification):
    response = flask_app_client.delete(
        f"/api/v1/user_verifications/{regular_user_user_verification.id}"
    )

    if login_as.is_admin or login_as.is_internal:
        assert_success(
            response,
            None,
            UserVerification,
            None,
            delete_item_id=regular_user_user_verification.id,
        )
    else:
        assert403(
            response,
            UserVerification,
            old_item=regular_user_user_verification,
            internal=True,
            action="deleted",
        )


def test_deleting_self(
    flask_app_client, admin_user_instance, regular_user_user_verification
):
    response = flask_app_client.delete(
        f"/api/v1/user_verifications/{regular_user_user_verification.id}"
    )
    assert_success(
        response,
        None,
        UserVerification,
        None,
        delete_item_id=regular_user_user_verification.id,
    )
