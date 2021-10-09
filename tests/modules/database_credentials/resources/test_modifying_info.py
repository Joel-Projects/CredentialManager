import json

import pytest

from app.modules.database_credentials.models import DatabaseCredential
from app.modules.database_credentials.schemas import DetailedDatabaseCredentialSchema
from tests.params import labels, users
from tests.utils import assert403, assert409, assert422, assert_success

data = [
    {
        "op": "replace",
        "path": "/app_name",
        "value": "new_name",
    },
    {
        "op": "replace",
        "path": "/enabled",
        "value": False,
    },
]


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_modifying_database_credential(flask_app_client, regular_user_database_credential, login_as):
    response = flask_app_client.patch(
        f"/api/v1/database_credentials/{regular_user_database_credential.id}",
        content_type="application/json",
        data=json.dumps(data),
    )

    if login_as.is_admin or login_as.is_internal:
        assert_success(
            response,
            regular_user_database_credential.owner,
            DatabaseCredential,
            DetailedDatabaseCredentialSchema,
        )
    else:
        assert403(
            response,
            DatabaseCredential,
            action="patch",
            internal=True,
            old_item=regular_user_database_credential,
        )


def test_modifying_database_credential_by_self(
    flask_app_client, regular_user_instance, regular_user_database_credential
):
    regular_user_database_credential.owner = regular_user_instance
    response = flask_app_client.patch(
        f"/api/v1/database_credentials/{regular_user_database_credential.id}",
        content_type="application/json",
        data=json.dumps(data),
    )

    assert_success(
        response,
        regular_user_database_credential.owner,
        DatabaseCredential,
        DetailedDatabaseCredentialSchema,
    )


def test_modifying_database_credential_info_with_invalid_format_must_fail(
    flask_app_client, regular_user_instance, regular_user_database_credential
):
    regular_user_database_credential.owner = regular_user_instance
    response = flask_app_client.patch(
        f"/api/v1/database_credentials/{regular_user_instance.id}",
        content_type="application/json",
        data=json.dumps(
            [
                {
                    "op": "test",
                    "path": "/app_name",
                    "value": "",
                },
                {
                    "op": "replace",
                    "path": "/enabled",
                },
            ]
        ),
    )
    assert422(
        response,
        DatabaseCredential,
        [("1", {"_schema": ["value is required"]})],
        old_item=regular_user_database_credential,
        action="patch",
    )


def test_modifying_database_credential_info_with_conflict_data_must_fail(
    flask_app_client,
    regular_user_instance,
    regular_user_database_credential,
    admin_user_database_credential,
):
    regular_user_database_credential.owner = regular_user_instance
    admin_user_database_credential.app_name = "different_name"
    admin_user_database_credential.owner = regular_user_instance
    response = flask_app_client.patch(
        f"/api/v1/database_credentials/{regular_user_database_credential.id}",
        content_type="application/json",
        data=json.dumps(
            [
                {
                    "op": "replace",
                    "path": "/app_name",
                    "value": admin_user_database_credential.app_name,
                }
            ]
        ),
    )

    assert409(
        response,
        DatabaseCredential,
        "Failed to update Database Credential details.",
        login_as=regular_user_instance,
        message_attrs=[("1", {"_schema": ["value is required"]})],
        old_item=regular_user_database_credential,
        action="patch",
    )
