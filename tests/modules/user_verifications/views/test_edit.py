import pytest

from app.modules.user_verifications.models import UserVerification
from tests.params import labels, users
from tests.responseStatuses import assert202, assert403
from tests.utils import (
    assertMessageFlashed,
    assertModified,
    assertRenderedTemplate,
    captured_templates,
    changeOwner,
)


userVerifications = [
    pytest.lazy_fixture("adminUserUserVerification"),
    pytest.lazy_fixture("internalUserUserVerification"),
    pytest.lazy_fixture("regularUserUserVerification"),
]
userVerificationLabels = [
    "admin_user_user_verification+reddit_app",
    "internal_user_user_verification+reddit_app",
    "regular_user_user_verification+reddit_app",
]


@pytest.mark.parametrize("loginAs", users, ids=labels)
@pytest.mark.parametrize(
    "userVerification", userVerifications, ids=userVerificationLabels
)
def test_user_verification_detail_edit_for_other_user(
    flask_app_client, loginAs, userVerification, redditApp
):
    redditApp.owner = loginAs
    data = {
        "itemType": "user_verifications",
        "itemId": f"{userVerification.id}",
        "reddit_app": f"{redditApp.id}",
        "enabled": "y",
        "user_id": "123456789012345679",
        "redditor": "redditor",
    }
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            f"/user_verifications/{userVerification.id}",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        if loginAs.is_internal:
            assert202(response)
            assertRenderedTemplate(templates, "edit_user_verification.html")
            assertMessageFlashed(
                templates,
                "User Verification for User ID 123456789012345679 saved successfully!",
                "success",
            )
            modifiedUserVerification = UserVerification.query.filter_by(
                id=userVerification.id
            ).first()
            assertModified(data, modifiedUserVerification)
        elif loginAs.is_admin:
            if redditApp.owner.is_internal or userVerification.owner.is_internal:
                assert403(response, templates)
                modifiedUserVerification = UserVerification.query.filter_by(
                    id=userVerification.id
                ).first()
                assert modifiedUserVerification == userVerification
            else:
                assert202(response)
                assertRenderedTemplate(templates, "edit_user_verification.html")
                assertMessageFlashed(
                    templates,
                    "User Verification for User ID 123456789012345679 saved successfully!",
                    "success",
                )
                modifiedUserVerification = UserVerification.query.filter_by(
                    id=userVerification.id
                ).first()
                assertModified(data, modifiedUserVerification)
        else:
            assert403(response, templates)
            modifiedUserVerification = UserVerification.query.filter_by(
                id=userVerification.id
            ).first()
            assert modifiedUserVerification == userVerification


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_user_verification_detail_edit(
    flask_app_client, loginAs, regularUserUserVerification, redditApp
):
    redditApp.owner = loginAs
    data = {
        "itemType": "user_verifications",
        "itemId": f"{regularUserUserVerification.id}",
        "reddit_app": f"{redditApp.id}",
        "enabled": "y",
        "user_id": "123456789012345679",
        "redditor": "redditor",
    }
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            f"/user_verifications/{regularUserUserVerification.id}",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        if loginAs.is_admin or loginAs.is_internal:
            assert202(response)
            assertRenderedTemplate(templates, "edit_user_verification.html")
            assertMessageFlashed(
                templates,
                "User Verification for User ID 123456789012345679 saved successfully!",
                "success",
            )
            modifiedUserVerification = UserVerification.query.filter_by(
                id=regularUserUserVerification.id
            ).first()
            assertModified(data, modifiedUserVerification)

        else:
            assert403(response, templates)
            modifiedUserVerification = UserVerification.query.filter_by(
                id=regularUserUserVerification.id
            ).first()
            assert modifiedUserVerification == regularUserUserVerification


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_user_verification_detail_edit_self(
    flask_app_client, db, loginAs, regularUserUserVerification, redditApp
):
    redditApp.owner = loginAs
    data = {
        "itemType": "user_verifications",
        "itemId": f"{regularUserUserVerification.id}",
        "reddit_app": f"{redditApp.id}",
        "enabled": "y",
        "user_id": "123456789012345679",
        "redditor": "redditor",
    }
    regularUserUserVerification = changeOwner(db, loginAs, regularUserUserVerification)
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            f"/user_verifications/{regularUserUserVerification.id}", data=data
        )
        assert202(response)
        assertRenderedTemplate(templates, "edit_user_verification.html")
        assertMessageFlashed(
            templates,
            "User Verification for User ID 123456789012345679 saved successfully!",
            "success",
        )
        modifiedUserVerification = UserVerification.query.filter_by(
            id=regularUserUserVerification.id
        ).first()
        assertModified(data, modifiedUserVerification)


def test_user_verification_detail_conflicting_user_id(
    flask_app_client,
    db,
    regularUserInstance,
    regularUserUserVerification,
    adminUserUserVerification,
):
    original = changeOwner(db, regularUserInstance, adminUserUserVerification)
    original.user_id = "123456789012345679"
    db.session.merge(original)
    toBeModified = changeOwner(db, regularUserInstance, regularUserUserVerification)
    db.session.merge(toBeModified)
    data = {
        "itemType": "user_verifications",
        "itemId": f"{regularUserUserVerification.id}",
        "enabled": "y",
        "user_id": "123456789012345679",
        "redditor": "redditor",
    }
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            f"/user_verifications/{toBeModified.id}", json=data
        )
        assert response.status_code == 422
        assert response.mimetype == "text/html"
        assertRenderedTemplate(templates, "edit_user_verification.html")
        assert (
            templates["templates"][0][1]["form"].errors["user_id"][0]
            == "Already exists."
        )
        modifiedUserVerification = UserVerification.query.filter_by(
            id=toBeModified.id
        ).first()
        assert modifiedUserVerification.user_id == toBeModified.user_id
