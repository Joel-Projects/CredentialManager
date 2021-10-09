import pytest

from app.modules.user_verifications.models import UserVerification
from app.modules.user_verifications.schemas import DetailedUserVerificationSchema
from tests.params import labels, users
from tests.utils import assert403, assert422, assert_success

path = "/api/v1/user_verifications/"
data = {"user_id": 123456789012345678}


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_creating_user_verification(flask_app_client, login_as, regular_user, reddit_app):
    response = flask_app_client.post(path, data={"owner_id": regular_user.id, "reddit_app_id": reddit_app.id, **data})

    if login_as.is_admin or login_as.is_internal:
        assert_success(response, regular_user, UserVerification, DetailedUserVerificationSchema)
    else:
        assert403(response, UserVerification, action="create")


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_creating_user_verification_existing(
    flask_app_client, login_as, regular_user, reddit_app, regular_user_user_verification
):

    response = flask_app_client.post(
        path,
        data={
            "owner_id": regular_user.id,
            "reddit_app_id": reddit_app.id,
            "user_id": regular_user_user_verification.user_id,
        },
    )

    if login_as.is_admin or login_as.is_internal:
        assert_success(response, regular_user, UserVerification, DetailedUserVerificationSchema)
    else:
        assert403(response, UserVerification, action="create")


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_creating_user_verification_with_extra_data(flask_app_client, login_as, reddit_app):
    response = flask_app_client.post(
        path,
        data={"reddit_app_id": reddit_app.id, "extra_data": '{"key": "value"}', **data},
    )

    if login_as.is_admin or login_as.is_internal:
        assert_success(response, login_as, UserVerification, DetailedUserVerificationSchema)
    else:
        assert422(
            response,
            UserVerification,
            message_attrs=[
                (
                    "reddit_app_id",
                    ["You don't have the permission to create User Verifications with other users' Reddit Apps."],
                )
            ],
        )


def test_creating_user_verification_for_self(flask_app_client, regular_user_instance, reddit_app):
    reddit_app.owner = regular_user_instance
    response = flask_app_client.post(path, data={"reddit_app_id": reddit_app.id, **data})

    assert_success(
        response,
        regular_user_instance,
        UserVerification,
        DetailedUserVerificationSchema,
    )


def test_creating_user_verification_for_self_with_owner(flask_app_client, regular_user_instance, reddit_app):
    reddit_app.owner = regular_user_instance
    response = flask_app_client.post(
        path,
        data={
            "owner_id": regular_user_instance.id,
            "reddit_app_id": reddit_app.id,
            **data,
        },
    )

    assert_success(
        response,
        regular_user_instance,
        UserVerification,
        DetailedUserVerificationSchema,
    )
