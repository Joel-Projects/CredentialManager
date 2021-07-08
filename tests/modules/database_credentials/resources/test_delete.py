import pytest

from app.modules.database_credentials.models import DatabaseCredential
from tests.params import labels, users
from tests.utils import assert403, assert_success

database_credentials_to_delete = [
    pytest.lazy_fixture("admin_user_database_credential"),
    pytest.lazy_fixture("internal_user_database_credential"),
    pytest.lazy_fixture("regular_user_database_credential"),
]


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_deleting_user(flask_app_client, login_as, regular_user_database_credential):
    response = flask_app_client.delete(
        f"/api/v1/database_credentials/{regular_user_database_credential.id}"
    )

    if login_as.is_admin or login_as.is_internal:
        assert_success(
            response,
            None,
            DatabaseCredential,
            None,
            delete_item_id=regular_user_database_credential.id,
        )
    else:
        assert403(
            response,
            DatabaseCredential,
            old_item=regular_user_database_credential,
            internal=True,
            action="deleted",
        )


def test_deleting_self(
    flask_app_client, admin_user_instance, regular_user_database_credential
):
    response = flask_app_client.delete(
        f"/api/v1/database_credentials/{regular_user_database_credential.id}"
    )
    assert_success(
        response,
        None,
        DatabaseCredential,
        None,
        delete_item_id=regular_user_database_credential.id,
    )
