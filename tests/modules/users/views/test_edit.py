import pytest

from app.modules.users.models import User
from tests.params import labels, users
from tests.response_statuses import assert202, assert400, assert403
from tests.utils import assert_message_flashed, assert_rendered_template, captured_templates


def assert202Profile(response):
    assert response.status_code == 202
    assert response.mimetype == "text/html"
    assert response.location == "http://localhost/profile"


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_user_detail_edit(flask_app_client, login_as, regular_user):
    data = {
        "item_type": "users",
        "item_id": "2",
        "username": "regular_user",
        "reddit_username": "reddit_username",
        "update_password": "y",
        "root[0][Setting]": "database_flavor",
        "root[0][Default Value]": "different",
        "password": "new_password",
        "is_admin": "y",
        "is_active": "y",
        "is_internal": "",
        "is_regular_user": "y",
        "save": "save",
    }
    old_user = regular_user
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            f"/u/{regular_user.username}",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        if login_as.is_admin or login_as.is_internal:
            assert202(response)
            assert_rendered_template(templates, "edit_user.html")
            assert_message_flashed(templates, "User 'regular_user' saved successfully!", "success")
            modified_user = User.query.get(old_user.id)
            assert modified_user.reddit_username == "reddit_username"
            assert modified_user.is_admin
            assert modified_user.password == "new_password"
            assert modified_user.default_settings["database_flavor"] == "different"
        else:
            assert403(response, templates)
            modified_user = User.query.get(old_user.id)
            assert modified_user == old_user


def test_user_detail_edit_without_update_password(flask_app_client, db, regular_user_instance):
    data = {
        "item_type": "users",
        "item_id": regular_user_instance.id,
        "username": regular_user_instance.username,
        "reddit_username": "",
        "password": "new_password",
        "is_admin": "",
        "is_active": "y",
        "is_internal": "",
        "is_regular_user": "y",
        "save": "save",
    }
    regular_user_instance.reddit_username = ""
    db.session.merge(regular_user_instance)
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post("/profile", content_type="application/x-www-form-urlencoded", data=data)
        assert202(response)
        assert_rendered_template(templates, "edit_user.html")
        modified_user = User.query.get(regular_user_instance.id)
        assert modified_user == regular_user_instance


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_user_detail_edit_self(flask_app_client, login_as):
    data = {
        "item_type": "users",
        "item_id": login_as.id,
        "username": login_as.username,
        "reddit_username": "reddit_username",
        "update_password": "y",
        "root[0][Setting]": "database_flavor",
        "root[0][Default Value]": "different",
        "password": "new_password",
        "is_admin": ("", "y")[login_as.is_admin],
        "is_active": "y",
        "is_internal": ("", "y")[login_as.is_internal],
        "is_regular_user": "y",
        "save": "save",
    }
    old_user = login_as
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post("/profile", data=data, follow_redirects=True)
        assert202(response)
        assert_rendered_template(templates, "edit_user.html")
        assert_message_flashed(templates, "User 'username' saved successfully!", "success")
        modified_user = User.query.get(old_user.id)
        assert modified_user.reddit_username == "reddit_username"
        assert modified_user.password == "new_password"
        assert modified_user.default_settings["database_flavor"] == "different"


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_user_detail_edit_set_is_internal(flask_app_client, login_as, regular_user):
    data = {
        "item_type": "users",
        "item_id": regular_user.id,
        "username": regular_user.username,
        "reddit_username": "",
        "password": "",
        "is_admin": "",
        "is_active": "y",
        "is_internal": "y",
        "is_regular_user": "y",
        "save": "save",
    }
    old_user = regular_user
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            f"/u/{regular_user.username}",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        modified_user = User.query.get(old_user.id)
        if login_as.is_internal:
            assert202(response)
            assert_rendered_template(templates, "edit_user.html")
            assert_message_flashed(templates, "User 'regular_user' saved successfully!", "success")
            assert modified_user.is_internal
        elif login_as.is_admin:
            assert400(response)
            assert_rendered_template(templates, "edit_user.html")
            assert_message_flashed(templates, "Failed to update User 'regular_user'", "error")
            assert modified_user == old_user
        else:
            assert403(response, templates)
            assert modified_user == old_user


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_user_detail_username(flask_app_client, login_as, regular_user):
    data = {
        "item_type": "users",
        "item_id": regular_user.id,
        "username": "regular_user_new",
        "reddit_username": "",
        "password": "",
        "is_admin": "",
        "is_active": "y",
        "is_internal": "",
        "is_regular_user": "y",
        "save": "save",
    }
    old_user = regular_user
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            f"/u/{regular_user.username}",
            content_type="application/x-www-form-urlencoded",
            data=data,
            follow_redirects=True,
        )
        if login_as.is_admin or login_as.is_internal:
            assert202(response)
            assert_message_flashed(templates, "User 'regular_user_new' saved successfully!", "success")
            assert response.location == "http://localhost/u/regular_user_new"
            modified_user = User.query.filter_by(username="regular_user_new").first()
            assert modified_user.username == "regular_user_new"
        else:
            assert403(response, templates)
            modified_user = User.query.get(old_user.id)
            assert modified_user == old_user


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_user_detail_self_username(flask_app_client, login_as):
    data = {
        "item_type": "users",
        "item_id": login_as.id,
        "username": "new_username",
        "reddit_username": "",
        "password": "",
        "is_admin": ("", "y")[login_as.is_admin],
        "is_active": "y",
        "is_internal": ("", "y")[login_as.is_internal],
        "is_regular_user": "y",
        "save": "save",
    }
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post("/profile", json=data, follow_redirects=True)
        assert202Profile(response)
        assert_message_flashed(templates, "User 'new_username' saved successfully!", "success")
        modified_user = User.query.filter_by(username="new_username").first()
        assert modified_user.username == "new_username"


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_user_detail_conflicting_username(flask_app_client, login_as, regular_user):
    data = {
        "item_type": "users",
        "item_id": login_as.id,
        "username": regular_user.username,
        "reddit_username": "",
        "password": "",
        "is_admin": ("", "y")[login_as.is_admin],
        "is_active": "y",
        "is_internal": ("", "y")[login_as.is_internal],
        "is_regular_user": "y",
        "save": "save",
    }
    original = login_as
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post("/profile", json=data, follow_redirects=True)
        assert response.status_code == 422
        assert response.mimetype == "text/html"
        assert_rendered_template(templates, "edit_user.html")
        assert templates["templates"][0][1]["users_form"].errors["username"][0] == "Already exists."
        modified_user = User.query.get(original.id)
        assert modified_user.username == original.username
