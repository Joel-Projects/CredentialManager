import pytest

from app.modules.api_tokens.models import ApiToken
from tests.params import labels, users
from tests.response_statuses import assert202, assert403
from tests.utils import (
    assert_message_flashed,
    assert_rendered_template,
    captured_templates,
    change_owner,
)

api_tokens = [
    pytest.lazy_fixture("admin_user_api_token"),
    pytest.lazy_fixture("internal_user_api_token"),
    pytest.lazy_fixture("regular_user_api_token"),
]
api_token_labels = [
    "admin_user_api_token",
    "internal_user_api_token",
    "regular_user_api_token",
]


@pytest.mark.parametrize("login_as", users, ids=labels)
@pytest.mark.parametrize("api_token", api_tokens, ids=api_token_labels)
def test_api_token_detail_edit_for_other_user(flask_app_client, login_as, api_token):
    data = {
        "item_type": "api_tokens",
        "item_id": f"{api_token.id}",
        "name": "new_name",
        "token": api_token.token,
        "enabled": "y",
    }
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            f"/api_tokens/{api_token.id}",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        if api_token.owner.is_internal and not login_as.is_internal:
            assert403(response, templates)
            modified_api_token = ApiToken.query.filter_by(id=api_token.id).first()
            assert modified_api_token == api_token
        elif login_as.is_admin or login_as.is_internal:
            assert202(response)
            assert_rendered_template(templates, "edit_api_token.html")
            assert_message_flashed(
                templates, "API Token 'new_name' saved successfully!", "success"
            )
            modified_api_token = ApiToken.query.filter_by(id=api_token.id).first()
            assert modified_api_token.name == "new_name"
            assert modified_api_token.token == api_token.token
        else:
            assert403(response, templates)
            assert api_token == ApiToken.query.filter_by(id=api_token.id).first()


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_api_token_detail_edit(flask_app_client, login_as, regular_user_api_token):
    data = {
        "item_type": "api_tokens",
        "item_id": f"{regular_user_api_token.id}",
        "name": "new_name",
        "token": regular_user_api_token.token,
        "enabled": "",
    }
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            f"/api_tokens/{regular_user_api_token.id}",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        if login_as.is_admin or login_as.is_internal:
            assert202(response)
            assert_rendered_template(templates, "edit_api_token.html")
            assert_message_flashed(
                templates, "API Token 'new_name' saved successfully!", "success"
            )
            modified_api_token = ApiToken.query.filter_by(
                id=regular_user_api_token.id
            ).first()
            assert modified_api_token.name == "new_name"
        else:
            assert403(response, templates)
            assert (
                regular_user_api_token
                == ApiToken.query.filter_by(id=regular_user_api_token.id).first()
            )


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_api_token_detail_edit_self(
    flask_app_client, db, login_as, regular_user_api_token
):
    data = {
        "item_type": "api_tokens",
        "item_id": f"{regular_user_api_token.id}",
        "name": "new_name",
        "token": regular_user_api_token.token,
        "enabled": "",
    }
    regular_user_api_token = change_owner(db, login_as, regular_user_api_token)
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            f"/api_tokens/{regular_user_api_token.id}", data=data
        )
        assert202(response)
        assert_rendered_template(templates, "edit_api_token.html")
        assert_message_flashed(
            templates, "API Token 'new_name' saved successfully!", "success"
        )
        modified_api_token = ApiToken.query.filter_by(
            id=regular_user_api_token.id
        ).first()
        assert not modified_api_token.enabled
        assert modified_api_token.name == "new_name"


def test_api_token_detail_conflicting_name(
    flask_app_client,
    db,
    regular_user_instance,
    regular_user_api_token,
    admin_user_api_token,
):
    original = change_owner(db, regular_user_instance, admin_user_api_token)
    original.name = "original"
    to_be_modified = change_owner(db, regular_user_instance, regular_user_api_token)
    db.session.merge(original)
    data = {
        "item_type": "api_tokens",
        "item_id": to_be_modified.id,
        "name": "original",
        "token": to_be_modified.token,
        "enabled": "",
    }
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(f"/api_tokens/{to_be_modified.id}", json=data)
        assert response.status_code == 422
        assert response.mimetype == "text/html"
        assert_rendered_template(templates, "edit_api_token.html")
        assert (
            templates["templates"][0][1]["form"].errors["name"][0] == "Already exists."
        )
        assert (
            regular_user_api_token
            == ApiToken.query.filter_by(id=regular_user_api_token.id).first()
        )
