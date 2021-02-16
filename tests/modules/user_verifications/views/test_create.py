import pytest

from app.modules.user_verifications.models import UserVerification
from tests.params import labels, users
from tests.responseStatuses import assert201, assert403Create, assert422
from tests.utils import assertCreated, assertRenderedTemplate, captured_templates


data = {
    "user_id": "123456789012345678",
}


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_create_user_verification(flask_app_client, loginAs, redditApp):
    with captured_templates(flask_app_client.application) as templates:
        redditApp.owner = loginAs
        response = flask_app_client.post(
            "/user_verifications",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        assert201(response)
        assertRenderedTemplate(templates, "user_verifications.html")
        userVerification = UserVerification.query.filter_by(
            user_id="123456789012345678"
        ).first()
        assertCreated(userVerification, data)


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_create_user_verification_with_extra_data(flask_app_client, loginAs, redditApp):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            "/user_verifications",
            content_type="application/x-www-form-urlencoded",
            data={"extra_data": '{"key": "value"}', **data},
        )
        assert201(response)
        assertRenderedTemplate(templates, "user_verifications.html")
        userVerification = UserVerification.query.filter_by(
            user_id="123456789012345678"
        ).first()
        assertCreated(userVerification, data)
        assert userVerification.extra_data == {"key": "value"}


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_create_user_verification_profile(flask_app_client, loginAs, redditApp):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            f"/profile/user_verifications",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        assert201(response)
        assertRenderedTemplate(templates, "user_verifications.html")
        userVerification = UserVerification.query.filter_by(
            user_id="123456789012345678"
        ).first()
        assertCreated(userVerification, data)


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_create_user_verification_other_user(
    flask_app_client, loginAs, regular_user, redditApp
):
    with captured_templates(flask_app_client.application) as templates:
        if not (loginAs.is_admin or loginAs.is_internal):
            redditApp.owner = loginAs
        response = flask_app_client.post(
            "/user_verifications",
            content_type="application/x-www-form-urlencoded",
            data={
                "owner": str(regular_user.id),
                "reddit_app": str(redditApp.id),
                **data,
            },
        )
        if loginAs.is_admin or loginAs.is_internal:
            assert201(response)
            assertRenderedTemplate(templates, "user_verifications.html")
            userVerification = UserVerification.query.filter_by(
                user_id="123456789012345678"
            ).first()
            assertCreated(userVerification, data)
            assert userVerification.owner == regular_user
        else:
            assert403Create(response)
            userVerification = UserVerification.query.filter_by(
                user_id="123456789012345678"
            ).first()
            assert userVerification is None


def test_create_user_verification_bad_params(flask_app_client, regularUserInstance):
    with captured_templates(flask_app_client.application) as templates:
        data = {"extra_data": "invalid data", "user_id": "123456789012345678"}
        response = flask_app_client.post(
            "/user_verifications",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        assert response.status_code == 200
        assert response.mimetype == "application/json"
        userVerification = UserVerification.query.filter_by(
            user_id="123456789012345678"
        ).first()
        assert userVerification is None


def test_create_user_verification_empty_extra_data_profile(
    flask_app_client, regularUserInstance
):
    with captured_templates(flask_app_client.application) as templates:
        data = {"extra_data": "{}", "user_id": "123456789012345678"}
        response = flask_app_client.post(
            "/profile/user_verifications",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        assert422(response)
        userVerification = UserVerification.query.filter_by(
            user_id="123456789012345678"
        ).first()
        assert userVerification is None
