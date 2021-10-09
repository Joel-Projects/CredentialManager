import pytest

from app.modules.sentry_tokens.models import SentryToken
from tests.params import labels, users
from tests.response_statuses import assert202, assert403
from tests.utils import assert_message_flashed, assert_rendered_template, captured_templates, change_owner

sentry_tokens = [
    pytest.lazy_fixture("admin_user_sentry_token"),
    pytest.lazy_fixture("internal_user_sentry_token"),
    pytest.lazy_fixture("regular_user_sentry_token"),
]
sentry_token_labels = [
    "admin_user_sentry_token",
    "internal_user_sentry_token",
    "regular_user_sentry_token",
]


@pytest.mark.parametrize("login_as", users, ids=labels)
@pytest.mark.parametrize("sentry_token", sentry_tokens, ids=sentry_token_labels)
def test_sentry_token_detail_edit_for_other_user(flask_app_client, login_as, sentry_token):
    data = {
        "item_type": "sentry_tokens",
        "item_id": f"{sentry_token.id}",
        "enabled": "n",
        "app_name": "new_name",
        "dsn": "https://new@sentry.jesassn.org/1",
    }
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            f"/sentry_tokens/{sentry_token.id}",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        if sentry_token.owner.is_internal and not login_as.is_internal:
            assert403(response, templates)
            modified_sentry_token = SentryToken.query.filter_by(id=sentry_token.id).first()
            assert modified_sentry_token == sentry_token
        elif login_as.is_admin or login_as.is_internal:
            assert202(response)
            assert_rendered_template(templates, "edit_sentry_token.html")
            assert_message_flashed(templates, "Sentry Token 'new_name' saved successfully!", "success")
            modified_sentry_token = SentryToken.query.filter_by(id=sentry_token.id).first()
            assert modified_sentry_token.app_name == "new_name"
            assert modified_sentry_token.dsn == "https://new@sentry.jesassn.org/1"
            assert modified_sentry_token.enabled
        else:
            assert403(response, templates)
            modified_sentry_token = SentryToken.query.filter_by(id=sentry_token.id).first()
            assert modified_sentry_token == sentry_token


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_sentry_token_detail_edit(flask_app_client, login_as, regular_user_sentry_token):
    data = {
        "item_type": "sentry_tokens",
        "item_id": f"{regular_user_sentry_token.id}",
        "enabled": "n",
        "app_name": "new_name",
        "dsn": "https://new@sentry.jesassn.org/1",
    }
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            f"/sentry_tokens/{regular_user_sentry_token.id}",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        if login_as.is_admin or login_as.is_internal:
            assert202(response)
            assert_rendered_template(templates, "edit_sentry_token.html")
            assert_message_flashed(templates, "Sentry Token 'new_name' saved successfully!", "success")
            modified_sentry_token = SentryToken.query.filter_by(id=regular_user_sentry_token.id).first()
            assert modified_sentry_token == regular_user_sentry_token
        else:
            assert403(response, templates)
            modified_sentry_token = SentryToken.query.filter_by(id=regular_user_sentry_token.id).first()
            assert modified_sentry_token == regular_user_sentry_token


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_sentry_token_detail_edit_self(flask_app_client, db, login_as, regular_user_sentry_token):
    data = {
        "item_type": "sentry_tokens",
        "item_id": f"{regular_user_sentry_token.id}",
        "enabled": "",
        "app_name": "new_name",
        "dsn": "https://new@sentry.jesassn.org/1",
    }
    regular_user_sentry_token = change_owner(db, login_as, regular_user_sentry_token)
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(f"/sentry_tokens/{regular_user_sentry_token.id}", data=data)
        assert202(response)
        assert_rendered_template(templates, "edit_sentry_token.html")
        assert_message_flashed(templates, "Sentry Token 'new_name' saved successfully!", "success")
        modified_sentry_token = SentryToken.query.filter_by(id=regular_user_sentry_token.id).first()
        assert not modified_sentry_token.enabled
        assert modified_sentry_token.app_name == "new_name"
        assert modified_sentry_token.dsn == "https://new@sentry.jesassn.org/1"


def test_sentry_token_detail_conflicting_app_name(
    flask_app_client,
    db,
    regular_user_instance,
    regular_user_sentry_token,
    admin_user_sentry_token,
):
    original = change_owner(db, regular_user_instance, admin_user_sentry_token)
    original.app_name = "original"
    to_be_modified = change_owner(db, regular_user_instance, regular_user_sentry_token)
    db.session.merge(original)
    data = {
        "item_type": "sentry_tokens",
        "item_id": to_be_modified.id,
        "enabled": "n",
        "app_name": "original",
        "dsn": "https://new@sentry.jesassn.org/1",
    }
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(f"/sentry_tokens/{to_be_modified.id}", json=data)
        assert response.status_code == 422
        assert response.mimetype == "text/html"
        assert_rendered_template(templates, "edit_sentry_token.html")
        assert templates["templates"][0][1]["form"].errors["app_name"][0] == "Already exists."
        modified_sentry_token = SentryToken.query.filter_by(id=to_be_modified.id).first()
        assert modified_sentry_token.app_name == to_be_modified.app_name
