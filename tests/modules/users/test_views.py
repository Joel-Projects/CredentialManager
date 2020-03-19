import pytest, json
from app.modules.users.models import User

from tests.utils import captured_templates, assertRenderedTemplate


users = [
    pytest.lazy_fixture('adminUserInstance'),
    pytest.lazy_fixture('internalUserInstance'),
    pytest.lazy_fixture('regularUserInstance')
]
labels = [
    'as_admin_user',
    'as_internal_user',
    'as_regular_user'
]

def assert403(response, templates):
    assert response.status_code == 403
    assert response.mimetype == 'text/html'
    assertRenderedTemplate(templates, 'errors/403.html')

def assert200(response):
    assert response.status_code == 200
    assert response.mimetype == 'text/html'

def assert201(response):
    assert response.status_code == 201
    assert response.mimetype == 'text/html'

def assert202(response):
    assert response.status_code == 202
    assert response.mimetype == 'text/html'

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_root(flask_app_client, loginAs):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get('/users')
        if loginAs.is_admin or loginAs.is_internal:
            assert200(response)
        else:
            assert403(response, templates)

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_create_user(flask_app_client, loginAs):
    with captured_templates(flask_app_client.application) as templates:
        data = {'is_admin': True, 'is_internal': False, 'is_regular_user': False, 'is_active': True, 'username': 'test', 'password': 'test', 'reddit_username': 'test', 'default_settings': json.dumps([{'key': 'database_flavor', 'value': 'test'}])}
        response = flask_app_client.post('/users', content_type='application/x-www-form-urlencoded', data=data)
        if loginAs.is_admin or loginAs.is_internal:
            assert201(response)
            assertRenderedTemplate(templates, 'users.html')
            user = User.query.filter_by(username='test').first()
            assert user is not None
        else:
            assert403(response, templates)
            user = User.query.filter_by(username='test').first()
            assert user is None

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_user_detail(flask_app_client, loginAs, regular_user):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get(f'/u/{regular_user.username}')
        if loginAs.is_admin or loginAs.is_internal:
            assert200(response)
            assertRenderedTemplate(templates, 'edit_user.html')
        else:
            assert403(response, templates)

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_user_detail_self(flask_app_client, loginAs):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get(f'/profile', follow_redirects=True)
        assert200(response)
        assertRenderedTemplate(templates, 'edit_user.html')

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
        'password': 'newPass',
        'is_admin': 'f',
        'is_active': 'y',
        'save': 'save'
    }
    if loginAs.is_internal:
        data['is_active'] = 'y'
        data['is_internal'] = 'y'
        data['is_regular_user'] = 'y'
    elif loginAs.is_admin:
        data['is_active'] = 'y'
        data['is_admin'] = 'y'
    else:
        data['is_admin'] = 'f'
    oldUser = regular_user
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(f'/u/{regular_user.username}', content_type='application/x-www-form-urlencoded', data=data)
        if loginAs.is_admin or loginAs.is_internal:
            assert202(response)
            assertRenderedTemplate(templates, 'edit_user.html')
            modifiedUser = User.query.get(oldUser.id)
            assert modifiedUser.reddit_username == 'redditUsername'
            assert modifiedUser.is_admin
            assert modifiedUser.password == 'newPass'
            assert modifiedUser.default_settings['database_flavor'] == 'different'
        else:
            assert403(response, templates)
            modifiedUser = User.query.get(oldUser.id)
            assert modifiedUser == oldUser

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_user_detail_edit_self(flask_app_client, loginAs):
    data = {
        'itemType': 'users',
        'itemId': '2',
        'username': 'username',
        'reddit_username': 'redditUsername',
        'updatePassword': 'y',
        'root[0][Setting]': 'database_flavor',
        'root[0][Default Value]': 'different',
        'password': 'newPassword',
        'save': 'save'
    }
    oldUser = loginAs
    if loginAs.is_internal:
        data['is_active'] = 'y'
        data['is_internal'] = 'y'
        data['is_regular_user'] = 'y'
    elif loginAs.is_admin:
        data['is_active'] = 'y'
        data['is_admin'] = 'y'
    else:
        data['is_admin'] = 'f'
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(f'/profile', data=data, follow_redirects=True)
        assert202(response)
        assertRenderedTemplate(templates, 'edit_user.html')
        modifiedUser = User.query.get(oldUser.id)
        assert modifiedUser.reddit_username == 'redditUsername'
        assert modifiedUser.password == 'newPassword'
        assert modifiedUser.default_settings['database_flavor'] == 'different'

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_user_detail_edit_set_is_internal(flask_app_client, loginAs, regular_user):
    data = {
        'itemType': 'users',
        'itemId': '2',
        'username': 'regular_user',
        'reddit_username': '',
        'password': '',
        'is_admin': 'f',
        'is_active': 'y',
        'is_internal': 'y',
        'save': 'save'
    }
    oldUser = regular_user
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(f'/u/{regular_user.username}', content_type='application/x-www-form-urlencoded', data=data)
        modifiedUser = User.query.get(oldUser.id)
        if loginAs.is_internal:
            assert202(response)
            assertRenderedTemplate(templates, 'edit_user.html')
            assert modifiedUser.is_internal
        elif loginAs.is_admin:
            assert202(response)
            assertRenderedTemplate(templates, 'edit_user.html')
            assert modifiedUser == oldUser
        else:
            assert403(response, templates)
            assert modifiedUser == oldUser

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_user_detail_username(flask_app_client, loginAs, regular_user):
    data = {
        'itemType': 'users',
        'itemId': '2',
        'username': 'regular_userNew',
        'reddit_username': '',
        'password': '',
        'is_admin': 'f',
        'is_active': 'y',
        'save': 'save'
    }
    if loginAs.is_internal:
        data['is_active'] = 'y'
        data['is_internal'] = 'y'
        data['is_regular_user'] = 'y'
    elif loginAs.is_admin:
        data['is_active'] = 'y'
        data['is_admin'] = 'y'
    else:
        data['is_admin'] = 'f'
    oldUser = regular_user
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(f'/u/{regular_user.username}', content_type='application/x-www-form-urlencoded', data=data, follow_redirects=True)
        if loginAs.is_admin or loginAs.is_internal:
            assert202(response)
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
        'itemId': '2',
        'username': 'newUsername',
        'reddit_username': '',
        'password': '',
        'save': 'save'
    }
    if loginAs.is_internal:
        data['is_active'] = 'y'
        data['is_internal'] = 'y'
        data['is_regular_user'] = 'y'
    elif loginAs.is_admin:
        data['is_active'] = 'y'
        data['is_admin'] = 'y'
    else:
        data['is_admin'] = 'f'
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(f'/profile', json=data, follow_redirects=True)
        assert202Profile(response)
        modifiedUser = User.query.filter_by(username='newUsername').first()
        assert modifiedUser.username == 'newUsername'

def assert202Profile(response):
    assert response.status_code == 202
    assert response.mimetype == 'text/html'
    assert response.location == 'http://localhost/profile'

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_user_detail_conflicting_username(flask_app_client, loginAs, regular_user):
    data = {
        'itemType': 'users',
        'itemId': '1',
        'username': 'regular_user',
        'reddit_username': '',
        'password': '',
        'save': 'save'
    }
    if loginAs.is_internal:
        data['is_active'] = 'y'
        data['is_internal'] = 'y'
        data['is_regular_user'] = 'y'
    elif loginAs.is_admin:
        data['is_active'] = 'y'
        data['is_admin'] = 'y'
    else:
        data['is_admin'] = 'f'
    original = loginAs
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(f'/profile', json=data, follow_redirects=True)
        assert response.status_code == 422
        assert response.mimetype == 'text/html'
        assertRenderedTemplate(templates, 'edit_user.html')
        modifiedUser = User.query.get(original.id)
        assert modifiedUser.username == original.username