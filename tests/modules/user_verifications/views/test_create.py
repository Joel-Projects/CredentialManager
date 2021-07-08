import pytest

from app.modules.user_verifications.models import UserVerification
from tests.params import labels, users
from tests.response_statuses import assert201, assert403Create, assert422
from tests.utils import assert_created, assert_rendered_template, captured_templates

data = {
    "user_id": "123456789012345678",
}


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_create_user_verification(flask_app_client, login_as, reddit_app):
    with captured_templates(flask_app_client.application) as templates:
        reddit_app.owner = login_as
        response = flask_app_client.post(
            "/user_verifications",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        assert201(response)
        assert_rendered_template(templates, "user_verifications.html")
        user_verification = UserVerification.query.filter_by(
            user_id="123456789012345678"
        ).first()
        assert_created(user_verification, data)


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_create_user_verification_with_extra_data(
    flask_app_client, login_as, reddit_app
):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            "/user_verifications",
            content_type="application/x-www-form-urlencoded",
            data={"extra_data": '{"key": "value"}', **data},
        )
        assert201(response)
        assert_rendered_template(templates, "user_verifications.html")
        user_verification = UserVerification.query.filter_by(
            user_id="123456789012345678"
        ).first()
        assert_created(user_verification, data)
        assert user_verification.extra_data == {"key": "value"}


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_create_user_verification_profile(flask_app_client, login_as, reddit_app):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            f"/profile/user_verifications",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        assert201(response)
        assert_rendered_template(templates, "user_verifications.html")
        user_verification = UserVerification.query.filter_by(
            user_id="123456789012345678"
        ).first()
        assert_created(user_verification, data)


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_create_user_verification_other_user(
    flask_app_client, login_as, regular_user, reddit_app
):
    with captured_templates(flask_app_client.application) as templates:
        if not (login_as.is_admin or login_as.is_internal):
            reddit_app.owner = login_as
        response = flask_app_client.post(
            "/user_verifications",
            content_type="application/x-www-form-urlencoded",
            data={
                "owner": str(regular_user.id),
                "reddit_app": str(reddit_app.id),
                **data,
            },
        )
        if login_as.is_admin or login_as.is_internal:
            assert201(response)
            assert_rendered_template(templates, "user_verifications.html")
            user_verification = UserVerification.query.filter_by(
                user_id="123456789012345678"
            ).first()
            assert_created(user_verification, data)
            assert user_verification.owner == regular_user
        else:
            assert403Create(response)
            user_verification = UserVerification.query.filter_by(
                user_id="123456789012345678"
            ).first()
            assert user_verification is None


def test_create_user_verification_bad_params(flask_app_client, regular_user_instance):
    with captured_templates(flask_app_client.application) as templates:
        data = {"extra_data": "invalid data", "user_id": "123456789012345678"}
        response = flask_app_client.post(
            "/user_verifications",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        assert response.status_code == 200
        assert response.mimetype == "application/json"
        user_verification = UserVerification.query.filter_by(
            user_id="123456789012345678"
        ).first()
        assert user_verification is None


def test_create_user_verification_empty_extra_data_profile(
    flask_app_client, regular_user_instance
):
    with captured_templates(flask_app_client.application) as templates:
        data = {"extra_data": "{}", "user_id": "123456789012345678"}
        response = flask_app_client.post(
            "/profile/user_verifications",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        assert422(response)
        user_verification = UserVerification.query.filter_by(
            user_id="123456789012345678"
        ).first()
        assert user_verification is None
