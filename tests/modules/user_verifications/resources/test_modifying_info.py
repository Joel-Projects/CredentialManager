import json

import pytest

from app.modules.user_verifications.models import UserVerification
from app.modules.user_verifications.schemas import DetailedUserVerificationSchema
from tests.params import labels, users
from tests.utils import assert403, assert409, assert422, assertSuccess

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


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_modifying_user_verification(
    flask_app_client, regularUserUserVerification, loginAs
):
    response = flask_app_client.patch(
        f"/api/v1/user_verifications/{regularUserUserVerification.id}",
        content_type="application/json",
        data=json.dumps(data),
    )

    if loginAs.is_admin or loginAs.is_internal:
        assertSuccess(
            response,
            regularUserUserVerification.owner,
            UserVerification,
            DetailedUserVerificationSchema,
        )
    else:
        assert403(
            response,
            UserVerification,
            action="patch",
            internal=True,
            oldItem=regularUserUserVerification,
        )


def test_modifying_user_verification_by_self(
    flask_app_client, regularUserInstance, regularUserUserVerification
):
    regularUserUserVerification.owner = regularUserInstance
    response = flask_app_client.patch(
        f"/api/v1/user_verifications/{regularUserUserVerification.id}",
        content_type="application/json",
        data=json.dumps(data),
    )
    assertSuccess(
        response, regularUserInstance, UserVerification, DetailedUserVerificationSchema
    )


def test_modifying_user_verification_info_with_invalid_format_must_fail(
    flask_app_client, regularUserInstance, regularUserUserVerification
):
    regularUserUserVerification.owner = regularUserInstance
    response = flask_app_client.patch(
        f"/api/v1/user_verifications/{regularUserUserVerification.id}",
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
        oldItem=regularUserUserVerification,
        action="patch",
    )


def test_modifying_user_verification_info_with_conflict_data_must_fail(
    flask_app_client,
    regularUserInstance,
    regularUserUserVerification,
    adminUserUserVerification,
):
    regularUserUserVerification.owner = regularUserInstance
    adminUserUserVerification.owner = regularUserInstance
    response = flask_app_client.patch(
        f"/api/v1/user_verifications/{regularUserUserVerification.id}",
        content_type="application/json",
        data=json.dumps(
            [
                {
                    "op": "replace",
                    "path": "/user_id",
                    "value": adminUserUserVerification.user_id,
                }
            ]
        ),
    )

    assert409(
        response,
        UserVerification,
        "Failed to update User Verification details.",
        loginAs=regularUserInstance,
        messageAttrs=[("1", {"_schema": ["value is required"]})],
        oldItem=regularUserUserVerification,
        action="patch",
    )
