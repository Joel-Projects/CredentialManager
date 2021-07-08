import pytest

from app.modules.user_verifications.models import UserVerification
from tests.params import labels, users
from tests.response_statuses import assert202, assert403
from tests.utils import (
    assert_message_flashed,
    assert_modified,
    assert_rendered_template,
    captured_templates,
    change_owner,
)

user_verifications = [
    pytest.lazy_fixture("admin_user_user_verification"),
    pytest.lazy_fixture("internal_user_user_verification"),
    pytest.lazy_fixture("regular_user_user_verification"),
]
user_verification_labels = [
    "admin_user_user_verification+reddit_app",
    "internal_user_user_verification+reddit_app",
    "regular_user_user_verification+reddit_app",
]


@pytest.mark.parametrize("login_as", users, ids=labels)
@pytest.mark.parametrize(
    "user_verification", user_verifications, ids=user_verification_labels
)
def test_user_verification_detail_edit_for_other_user(
    flask_app_client, login_as, user_verification, reddit_app
):
    reddit_app.owner = login_as
    data = {
        "item_type": "user_verifications",
        "item_id": f"{user_verification.id}",
        "reddit_app": f"{reddit_app.id}",
        "enabled": "y",
        "user_id": "123456789012345679",
        "redditor": "redditor",
    }
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            f"/user_verifications/{user_verification.id}",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        if login_as.is_internal:
            assert202(response)
            assert_rendered_template(templates, "edit_user_verification.html")
            assert_message_flashed(
                templates,
                "User Verification for User ID 123456789012345679 saved successfully!",
                "success",
            )
            modified_user_verification = UserVerification.query.filter_by(
                id=user_verification.id
            ).first()
            assert_modified(data, modified_user_verification)
        elif login_as.is_admin:
            if reddit_app.owner.is_internal or user_verification.owner.is_internal:
                assert403(response, templates)
                modified_user_verification = UserVerification.query.filter_by(
                    id=user_verification.id
                ).first()
                assert modified_user_verification == user_verification
            else:
                assert202(response)
                assert_rendered_template(templates, "edit_user_verification.html")
                assert_message_flashed(
                    templates,
                    "User Verification for User ID 123456789012345679 saved successfully!",
                    "success",
                )
                modified_user_verification = UserVerification.query.filter_by(
                    id=user_verification.id
                ).first()
                assert_modified(data, modified_user_verification)
        else:
            assert403(response, templates)
            modified_user_verification = UserVerification.query.filter_by(
                id=user_verification.id
            ).first()
            assert modified_user_verification == user_verification


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_user_verification_detail_edit(
    flask_app_client, login_as, regular_user_user_verification, reddit_app
):
    reddit_app.owner = login_as
    data = {
        "item_type": "user_verifications",
        "item_id": f"{regular_user_user_verification.id}",
        "reddit_app": f"{reddit_app.id}",
        "enabled": "y",
        "user_id": "123456789012345679",
        "redditor": "redditor",
    }
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            f"/user_verifications/{regular_user_user_verification.id}",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        if login_as.is_admin or login_as.is_internal:
            assert202(response)
            assert_rendered_template(templates, "edit_user_verification.html")
            assert_message_flashed(
                templates,
                "User Verification for User ID 123456789012345679 saved successfully!",
                "success",
            )
            modified_user_verification = UserVerification.query.filter_by(
                id=regular_user_user_verification.id
            ).first()
            assert_modified(data, modified_user_verification)

        else:
            assert403(response, templates)
            modified_user_verification = UserVerification.query.filter_by(
                id=regular_user_user_verification.id
            ).first()
            assert modified_user_verification == regular_user_user_verification


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_user_verification_detail_edit_self(
    flask_app_client, db, login_as, regular_user_user_verification, reddit_app
):
    reddit_app.owner = login_as
    data = {
        "item_type": "user_verifications",
        "item_id": f"{regular_user_user_verification.id}",
        "reddit_app": f"{reddit_app.id}",
        "enabled": "y",
        "user_id": "123456789012345679",
        "redditor": "redditor",
    }
    regular_user_user_verification = change_owner(
        db, login_as, regular_user_user_verification
    )
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            f"/user_verifications/{regular_user_user_verification.id}", data=data
        )
        assert202(response)
        assert_rendered_template(templates, "edit_user_verification.html")
        assert_message_flashed(
            templates,
            "User Verification for User ID 123456789012345679 saved successfully!",
            "success",
        )
        modified_user_verification = UserVerification.query.filter_by(
            id=regular_user_user_verification.id
        ).first()
        assert_modified(data, modified_user_verification)


def test_user_verification_detail_conflicting_user_id(
    flask_app_client,
    db,
    regular_user_instance,
    regular_user_user_verification,
    admin_user_user_verification,
):
    original = change_owner(db, regular_user_instance, admin_user_user_verification)
    original.user_id = "123456789012345679"
    db.session.merge(original)
    to_be_modified = change_owner(
        db, regular_user_instance, regular_user_user_verification
    )
    db.session.merge(to_be_modified)
    data = {
        "item_type": "user_verifications",
        "item_id": f"{regular_user_user_verification.id}",
        "enabled": "y",
        "user_id": "123456789012345679",
        "redditor": "redditor",
    }
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            f"/user_verifications/{to_be_modified.id}", json=data
        )
        assert response.status_code == 422
        assert response.mimetype == "text/html"
        assert_rendered_template(templates, "edit_user_verification.html")
        assert (
            templates["templates"][0][1]["form"].errors["user_id"][0]
            == "Already exists."
        )
        modified_user_verification = UserVerification.query.filter_by(
            id=to_be_modified.id
        ).first()
        assert modified_user_verification.user_id == to_be_modified.user_id
