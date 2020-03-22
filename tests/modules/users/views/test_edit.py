import pytest

from app.modules.users.models import User
from tests.params import labels, users
from tests.responseStatuses import assert200, assert202, assert400, assert403
from tests.utils import assertMessageFlashed, assertRenderedTemplate, captured_templates
from . import assert202Profile

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_user_detail_edit(flask_app_client, loginAs, regular_user):
    data = {
        'itemType': 'users',
        'itemId': '2',
        'username': 'regular_user',
        'reddit_username': 'redditUsername',
        'updatePassword': 'y',
        'root[0][Setting]': 'database_flavor',
        'root[0][Default Value]': 'different',
        'password': 'newPassword',
        'is_admin': 'y',
        'is_active': 'y',
        'is_internal': '',
        'is_regular_user': 'y',
        'save': 'save'
    }
    oldUser = regular_user
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(f'/u/{regular_user.username}', content_type='application/x-www-form-urlencoded', data=data)
        if loginAs.is_admin or loginAs.is_internal:
            assert202(response)
            assertRenderedTemplate(templates, 'edit_user.html')
            assertMessageFlashed(templates, "User 'regular_user' saved successfully!", 'success')
            modifiedUser = User.query.get(oldUser.id)
            assert modifiedUser.reddit_username == 'redditUsername'
            assert modifiedUser.is_admin
            assert modifiedUser.password == 'newPassword'
            assert modifiedUser.default_settings['database_flavor'] == 'different'
        else:
            assert403(response, templates)
            modifiedUser = User.query.get(oldUser.id)
            assert modifiedUser == oldUser

def test_user_detail_edit_without_update_password(flask_app_client, regularUserInstance):
    data = {
        'itemType': 'users',
        'itemId': regularUserInstance.id,
        'username': regularUserInstance.username,
        'reddit_username': '',
        'password': 'newPassword',
        'is_admin': '',
        'is_active': 'y',
        'is_internal': '',
        'is_regular_user': 'y',
        'save': 'save'
    }
    oldUser = regularUserInstance
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post('/profile', content_type='application/x-www-form-urlencoded', data=data)
        assert200(response)
        assertRenderedTemplate(templates, 'edit_user.html')
        modifiedUser = User.query.get(oldUser.id)
        assert modifiedUser == oldUser

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_user_detail_edit_self(flask_app_client, loginAs):
    data = {
        'itemType': 'users',
        'itemId': loginAs.id,
        'username': loginAs.username,
        'reddit_username': 'redditUsername',
        'updatePassword': 'y',
        'root[0][Setting]': 'database_flavor',
        'root[0][Default Value]': 'different',
        'password': 'newPassword',
        'is_admin': ('', 'y')[loginAs.is_admin],
        'is_active': 'y',
        'is_internal': ('', 'y')[loginAs.is_internal],
        'is_regular_user': 'y',
        'save': 'save'
    }
    oldUser = loginAs
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post('/profile', data=data, follow_redirects=True)
        assert202(response)
        assertRenderedTemplate(templates, 'edit_user.html')
        assertMessageFlashed(templates, "User 'username' saved successfully!", 'success')
        modifiedUser = User.query.get(oldUser.id)
        assert modifiedUser.reddit_username == 'redditUsername'
        assert modifiedUser.password == 'newPassword'
        assert modifiedUser.default_settings['database_flavor'] == 'different'

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_user_detail_edit_set_is_internal(flask_app_client, loginAs, regular_user):
    data = {
        'itemType': 'users',
        'itemId': regular_user.id,
        'username': regular_user.username,
        'reddit_username': '',
        'password': '',
        'is_admin': '',
        'is_active': 'y',
        'is_internal': 'y',
        'is_regular_user': 'y',
        'save': 'save'
    }
    oldUser = regular_user
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(f'/u/{regular_user.username}', content_type='application/x-www-form-urlencoded', data=data)
        modifiedUser = User.query.get(oldUser.id)
        if loginAs.is_internal:
            assert202(response)
            assertRenderedTemplate(templates, 'edit_user.html')
            assertMessageFlashed(templates, "User 'regular_user' saved successfully!", 'success')
            assert modifiedUser.is_internal
        elif loginAs.is_admin:
            assert400(response)
            assertRenderedTemplate(templates, 'edit_user.html')
            assertMessageFlashed(templates, "Failed to update User 'regular_user'", 'error')
            assert modifiedUser == oldUser
        else:
            assert403(response, templates)
            assert modifiedUser == oldUser

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_user_detail_username(flask_app_client, loginAs, regular_user):
    data = {
        'itemType': 'users',
        'itemId': regular_user.id,
        'username': 'regular_userNew',
        'reddit_username': '',
        'password': '',
        'is_admin': '',
        'is_active': 'y',
        'is_internal': '',
        'is_regular_user': 'y',
        'save': 'save'
    }
    oldUser = regular_user
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(f'/u/{regular_user.username}', content_type='application/x-www-form-urlencoded', data=data, follow_redirects=True)
        if loginAs.is_admin or loginAs.is_internal:
            assert202(response)
            assertMessageFlashed(templates, "User 'regular_userNew' saved successfully!", 'success')
            assert response.location == 'http://localhost/u/regular_userNew'
            modifiedUser = User.query.filter_by(username='regular_userNew').first()
            assert modifiedUser.username == 'regular_userNew'
        else:
            assert403(response, templates)
            modifiedUser = User.query.get(oldUser.id)
            assert modifiedUser == oldUser

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_user_detail_self_username(flask_app_client, loginAs):
    data = {
        'itemType': 'users',
        'itemId': loginAs.id,
        'username': 'newUsername',
        'reddit_username': '',
        'password': '',
        'is_admin': ('', 'y')[loginAs.is_admin],
        'is_active': 'y',
        'is_internal': ('', 'y')[loginAs.is_internal],
        'is_regular_user': 'y',
        'save': 'save'
    }
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post('/profile', json=data, follow_redirects=True)
        assert202Profile(response)
        assertMessageFlashed(templates, "User 'newUsername' saved successfully!", 'success')
        modifiedUser = User.query.filter_by(username='newUsername').first()
        assert modifiedUser.username == 'newUsername'

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_user_detail_conflicting_username(flask_app_client, loginAs, regular_user):
    data = {
        'itemType': 'users',
        'itemId': loginAs.id,
        'username': regular_user.username,
        'reddit_username': '',
        'password': '',
        'is_admin': ('', 'y')[loginAs.is_admin],
        'is_active': 'y',
        'is_internal': ('', 'y')[loginAs.is_internal],
        'is_regular_user': 'y',
        'save': 'save'
    }
    original = loginAs
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post('/profile', json=data, follow_redirects=True)
        assert response.status_code == 422
        assert response.mimetype == 'text/html'
        assertRenderedTemplate(templates, 'edit_user.html')
        assert templates['templates'][0][1]['usersForm'].errors['username'][0] == 'Already exists.'
        modifiedUser = User.query.get(original.id)
        assert modifiedUser.username == original.username