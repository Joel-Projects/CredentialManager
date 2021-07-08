import json

import pytest

from app.modules.user_verifications.models import UserVerification
from app.modules.user_verifications.schemas import DetailedUserVerificationSchema
from tests.params import labels, users
from tests.utils import assert403, assert409, assert422, assert_success

data = [
    {
        "op": "replace",
        "path": "/redditor",
        "value": "redditor",
    },
    {
        "op": "replace",
        "path": "/enabled",
        "value": False,
    },
]


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_modifying_user_verification(
    flask_app_client, regular_user_user_verification, login_as
):
    response = flask_app_client.patch(
        f"/api/v1/user_verifications/{regular_user_user_verification.id}",
        content_type="application/json",
        data=json.dumps(data),
    )

    if login_as.is_admin or login_as.is_internal:
        assert_success(
            response,
            regular_user_user_verification.owner,
            UserVerification,
            DetailedUserVerificationSchema,
        )
    else:
        assert403(
            response,
            UserVerification,
            action="patch",
            internal=True,
            old_item=regular_user_user_verification,
        )


def test_modifying_user_verification_by_self(
    flask_app_client, regular_user_instance, regular_user_user_verification
):
    regular_user_user_verification.owner = regular_user_instance
    response = flask_app_client.patch(
        f"/api/v1/user_verifications/{regular_user_user_verification.id}",
        content_type="application/json",
        data=json.dumps(data),
    )
    assert_success(
        response,
        regular_user_instance,
        UserVerification,
        DetailedUserVerificationSchema,
    )


def test_modifying_user_verification_info_with_invalid_format_must_fail(
    flask_app_client, regular_user_instance, regular_user_user_verification
):
    regular_user_user_verification.owner = regular_user_instance
    response = flask_app_client.patch(
        f"/api/v1/user_verifications/{regular_user_user_verification.id}",
        content_type="application/json",
        data=json.dumps(
            [
                {
                    "op": "test",
                    "path": "/redditor",
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
        UserVerification,
        [("1", {"_schema": ["value is required"]})],
        old_item=regular_user_user_verification,
        action="patch",
    )


def test_modifying_user_verification_info_with_conflict_data_must_fail(
    flask_app_client,
    regular_user_instance,
    regular_user_user_verification,
    admin_user_user_verification,
):
    regular_user_user_verification.owner = regular_user_instance
    admin_user_user_verification.owner = regular_user_instance
    response = flask_app_client.patch(
        f"/api/v1/user_verifications/{regular_user_user_verification.id}",
        content_type="application/json",
        data=json.dumps(
            [
                {
                    "op": "replace",
                    "path": "/user_id",
                    "value": admin_user_user_verification.user_id,
                }
            ]
        ),
    )

    assert409(
        response,
        UserVerification,
        "Failed to update User Verification details.",
        login_as=regular_user_instance,
        message_attrs=[("1", {"_schema": ["value is required"]})],
        old_item=regular_user_user_verification,
        action="patch",
    )
