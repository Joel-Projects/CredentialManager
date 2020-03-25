import pytest

from app.modules.reddit_apps.models import RedditApp
from tests.params import labels, users
from tests.responseStatuses import assert202, assert403
from tests.utils import assertMessageFlashed, assertModified, assertRenderedTemplate, captured_templates, changeOwner


redditApps = [
    pytest.lazy_fixture('adminUserRedditApp'),
    pytest.lazy_fixture('internalUserRedditApp'),
    pytest.lazy_fixture('regularUserRedditApp')
]
redditAppLabels = [
    'admin_user_reddit_app',
    'internal_user_reddit_app',
    'regular_user_reddit_app'
]

@pytest.mark.parametrize('loginAs', users, ids=labels)
@pytest.mark.parametrize('redditApp', redditApps, ids=redditAppLabels)
def test_reddit_app_detail_edit_for_other_user(flask_app_client, loginAs, redditApp):
    data = {
        'itemType': 'reddit_apps',
        'itemId': f'{redditApp.id}',
        'enabled': 'y',
        'app_name': 'newName',
        'client_id': 'client_idNew',
        'client_secret': 'client_secretNew',
        'user_agent': 'user_agentNew',
        'app_type': 'script'
    }
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(f'/reddit_apps/{redditApp.id}', content_type='application/x-www-form-urlencoded', data=data)
        if redditApp.owner.is_internal and not loginAs.is_internal:
            assert403(response, templates)
            modifiedRedditApp = RedditApp.query.filter_by(id=redditApp.id).first()
            assert modifiedRedditApp == redditApp
        elif loginAs.is_admin or loginAs.is_internal:
            assert202(response)
            assertRenderedTemplate(templates, 'edit_reddit_app.html')
            assertMessageFlashed(templates, "Reddit App 'newName' saved successfully!", 'success')
            modifiedRedditApp = RedditApp.query.filter_by(id=redditApp.id).first()
            assertModified(data, modifiedRedditApp)
        else:
            assert403(response, templates)
            modifiedRedditApp = RedditApp.query.filter_by(id=redditApp.id).first()
            assert modifiedRedditApp == redditApp

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_reddit_app_detail_edit(flask_app_client, loginAs, regularUserRedditApp):
    data = {
        'itemType': 'reddit_apps',
        'itemId': f'{regularUserRedditApp.id}',
        'enabled': 'y',
        'app_name': 'newName',
        'client_id': 'client_idNew',
        'client_secret': 'client_secretNew',
        'user_agent': 'user_agentNew',
        'app_type': 'script'
    }
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(f'/reddit_apps/{regularUserRedditApp.id}', content_type='application/x-www-form-urlencoded', data=data)
        if loginAs.is_admin or loginAs.is_internal:
            assert202(response)
            assertRenderedTemplate(templates, 'edit_reddit_app.html')
            assertMessageFlashed(templates, "Reddit App 'newName' saved successfully!", 'success')
            modifiedRedditApp = RedditApp.query.filter_by(id=regularUserRedditApp.id).first()
            assertModified(data, modifiedRedditApp)

        else:
            assert403(response, templates)
            modifiedRedditApp = RedditApp.query.filter_by(id=regularUserRedditApp.id).first()
            assert modifiedRedditApp == regularUserRedditApp

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_reddit_app_detail_edit_self(flask_app_client, db, loginAs, regularUserRedditApp):
    data = {
        'itemType': 'reddit_apps',
        'itemId': f'{regularUserRedditApp.id}',
        'enabled': '',
        'app_name': 'newName',
        'client_id': 'client_idNew',
        'client_secret': 'client_secretNew',
        'user_agent': 'user_agentNew',
        'app_type': 'script'
    }
    regularUserRedditApp = changeOwner(db, loginAs, regularUserRedditApp)
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(f'/reddit_apps/{regularUserRedditApp.id}', data=data)
        assert202(response)
        assertRenderedTemplate(templates, 'edit_reddit_app.html')
        assertMessageFlashed(templates, "Reddit App 'newName' saved successfully!", 'success')
        modifiedRedditApp = RedditApp.query.filter_by(id=regularUserRedditApp.id).first()
        assertModified(data, modifiedRedditApp)

def test_reddit_app_detail_conflicting_client_id(flask_app_client, db, regularUserInstance, regularUserRedditApp, adminUserRedditApp):
    original = changeOwner(db, regularUserInstance, adminUserRedditApp)
    original.client_id = 'client_idNew'
    db.session.merge(original)
    toBeModified = changeOwner(db, regularUserInstance, regularUserRedditApp)
    db.session.merge(toBeModified)
    data = {
        'itemType': 'reddit_apps',
        'itemId': toBeModified.id,
        'enabled': 'y',
        'app_name': 'original',
        'client_id': 'client_idNew',
        'client_secret': 'client_secretNew',
        'user_agent': 'user_agentNew',
        'app_type': 'script'
    }
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(f'/reddit_apps/{toBeModified.id}', json=data)
        assert response.status_code == 422
        assert response.mimetype == 'text/html'
        assertRenderedTemplate(templates, 'edit_reddit_app.html')
        assert templates['templates'][0][1]['form'].errors['client_id'][0] == 'Already exists.'
        modifiedRedditApp = RedditApp.query.filter_by(id=toBeModified.id).first()
        assert modifiedRedditApp.app_name == toBeModified.app_name