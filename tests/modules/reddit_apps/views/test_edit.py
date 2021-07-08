import pytest

from app.modules.reddit_apps.models import RedditApp
from tests.params import labels, users
from tests.response_statuses import assert202, assert403
from tests.utils import (
    assert_message_flashed,
    assert_modified,
    assert_rendered_template,
    captured_templates,
    change_owner,
)

reddit_apps = [
    pytest.lazy_fixture("admin_user_reddit_app"),
    pytest.lazy_fixture("internal_user_reddit_app"),
    pytest.lazy_fixture("regular_user_reddit_app"),
]
reddit_app_labels = [
    "admin_user_reddit_app",
    "internal_user_reddit_app",
    "regular_user_reddit_app",
]


@pytest.mark.parametrize("login_as", users, ids=labels)
@pytest.mark.parametrize("reddit_app", reddit_apps, ids=reddit_app_labels)
def test_reddit_app_detail_edit_for_other_user(flask_app_client, login_as, reddit_app):
    data = {
        "item_type": "reddit_apps",
        "item_id": f"{reddit_app.id}",
        "enabled": "y",
        "app_name": "new_name",
        "client_id": "client_id_new",
        "client_secret": "client_secret_new",
        "user_agent": "user_agent_new",
        "app_type": "script",
    }
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            f"/reddit_apps/{reddit_app.id}",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        if reddit_app.owner.is_internal and not login_as.is_internal:
            assert403(response, templates)
            modified_reddit_app = RedditApp.query.filter_by(id=reddit_app.id).first()
            assert modified_reddit_app == reddit_app
        elif login_as.is_admin or login_as.is_internal:
            assert202(response)
            assert_rendered_template(templates, "edit_reddit_app.html")
            assert_message_flashed(
                templates, "Reddit App 'new_name' saved successfully!", "success"
            )
            modified_reddit_app = RedditApp.query.filter_by(id=reddit_app.id).first()
            assert_modified(data, modified_reddit_app)
        else:
            assert403(response, templates)
            modified_reddit_app = RedditApp.query.filter_by(id=reddit_app.id).first()
            assert modified_reddit_app == reddit_app


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_reddit_app_detail_edit(flask_app_client, login_as, regular_user_reddit_app):
    data = {
        "item_type": "reddit_apps",
        "item_id": f"{regular_user_reddit_app.id}",
        "enabled": "y",
        "app_name": "new_name",
        "client_id": "client_id_new",
        "client_secret": "client_secret_new",
        "user_agent": "user_agent_new",
        "app_type": "script",
    }
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            f"/reddit_apps/{regular_user_reddit_app.id}",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        if login_as.is_admin or login_as.is_internal:
            assert202(response)
            assert_rendered_template(templates, "edit_reddit_app.html")
            assert_message_flashed(
                templates, "Reddit App 'new_name' saved successfully!", "success"
            )
            modified_reddit_app = RedditApp.query.filter_by(
                id=regular_user_reddit_app.id
            ).first()
            assert_modified(data, modified_reddit_app)

        else:
            assert403(response, templates)
            modified_reddit_app = RedditApp.query.filter_by(
                id=regular_user_reddit_app.id
            ).first()
            assert modified_reddit_app == regular_user_reddit_app


@pytest.mark.parametrize("login_as", users, ids=labels)
def test_reddit_app_detail_edit_self(
    flask_app_client, db, login_as, regular_user_reddit_app
):
    data = {
        "item_type": "reddit_apps",
        "item_id": f"{regular_user_reddit_app.id}",
        "enabled": "",
        "app_name": "new_name",
        "client_id": "client_id_new",
        "client_secret": "client_secret_new",
        "user_agent": "user_agent_new",
        "app_type": "script",
    }
    regular_user_reddit_app = change_owner(db, login_as, regular_user_reddit_app)
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            f"/reddit_apps/{regular_user_reddit_app.id}", data=data
        )
        assert202(response)
        assert_rendered_template(templates, "edit_reddit_app.html")
        assert_message_flashed(
            templates, "Reddit App 'new_name' saved successfully!", "success"
        )
        modified_reddit_app = RedditApp.query.filter_by(
            id=regular_user_reddit_app.id
        ).first()
        assert_modified(data, modified_reddit_app)


def test_reddit_app_detail_conflicting_client_id(
    flask_app_client,
    db,
    regular_user_instance,
    regular_user_reddit_app,
    admin_user_reddit_app,
):
    original = change_owner(db, regular_user_instance, admin_user_reddit_app)
    original.client_id = "client_id_new"
    db.session.merge(original)
    to_be_modified = change_owner(db, regular_user_instance, regular_user_reddit_app)
    db.session.merge(to_be_modified)
    data = {
        "item_type": "reddit_apps",
        "item_id": to_be_modified.id,
        "enabled": "y",
        "app_name": "original",
        "client_id": "client_id_new",
        "client_secret": "client_secret_new",
        "user_agent": "user_agent_new",
        "app_type": "script",
    }
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(f"/reddit_apps/{to_be_modified.id}", json=data)
        assert response.status_code == 422
        assert response.mimetype == "text/html"
        assert_rendered_template(templates, "edit_reddit_app.html")
        assert (
            templates["templates"][0][1]["form"].errors["client_id"][0]
            == "Already exists."
        )
        modified_reddit_app = RedditApp.query.filter_by(id=to_be_modified.id).first()
        assert modified_reddit_app.app_name == to_be_modified.app_name
