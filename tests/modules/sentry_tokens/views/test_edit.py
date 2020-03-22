import pytest

from app.modules.sentry_tokens.models import SentryToken
from tests.params import labels, users
from tests.responseStatuses import assert202, assert403
from tests.utils import assertMessageFlashed, assertRenderedTemplate, captured_templates, changeOwner


sentryTokens = [
    pytest.lazy_fixture('adminUserSentryToken'),
    pytest.lazy_fixture('internalUserSentryToken'),
    pytest.lazy_fixture('regularUserSentryToken')
]
sentryTokenLabels = [
    'admin_user_sentry_token',
    'internal_user_sentry_token',
    'regular_user_sentry_token'
]

@pytest.mark.parametrize('loginAs', users, ids=labels)
@pytest.mark.parametrize('sentryToken', sentryTokens, ids=sentryTokenLabels)
def test_sentry_token_detail_edit_for_other_user(flask_app_client, loginAs, sentryToken):
    data = {
        'itemType': 'sentry_tokens',
        'itemId': f'{sentryToken.id}',
        'enabled': 'n',
        'app_name': 'newName',
        'dsn': 'https://new@sentry.jesassn.org/1'
    }
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(f'/sentry_tokens/{sentryToken.id}', content_type='application/x-www-form-urlencoded', data=data)
        if sentryToken.owner.is_internal and not loginAs.is_internal:
            assert403(response, templates)
            modifiedSentryToken = SentryToken.query.filter_by(id=sentryToken.id).first()
            assert modifiedSentryToken == sentryToken
        elif loginAs.is_admin or loginAs.is_internal:
            assert202(response)
            assertRenderedTemplate(templates, 'edit_sentry_token.html')
            assertMessageFlashed(templates, "Sentry Token 'newName' saved successfully!", 'success')
            modifiedSentryToken = SentryToken.query.filter_by(id=sentryToken.id).first()
            assert modifiedSentryToken.app_name == 'newName'
            assert modifiedSentryToken.dsn == 'https://new@sentry.jesassn.org/1'
            assert modifiedSentryToken.enabled
        else:
            assert403(response, templates)
            modifiedSentryToken = SentryToken.query.filter_by(id=sentryToken.id).first()
            assert modifiedSentryToken == sentryToken

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_sentry_token_detail_edit(flask_app_client, loginAs, regularUserSentryToken):
    data = {
        'itemType': 'sentry_tokens',
        'itemId': f'{regularUserSentryToken.id}',
        'enabled': 'n',
        'app_name': 'newName',
        'dsn': 'https://new@sentry.jesassn.org/1'
    }
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(f'/sentry_tokens/{regularUserSentryToken.id}', content_type='application/x-www-form-urlencoded', data=data)
        if loginAs.is_admin or loginAs.is_internal:
            assert202(response)
            assertRenderedTemplate(templates, 'edit_sentry_token.html')
            assertMessageFlashed(templates, "Sentry Token 'newName' saved successfully!", 'success')
            modifiedSentryToken = SentryToken.query.filter_by(id=regularUserSentryToken.id).first()
            assert modifiedSentryToken == regularUserSentryToken
        else:
            assert403(response, templates)
            modifiedSentryToken = SentryToken.query.filter_by(id=regularUserSentryToken.id).first()
            assert modifiedSentryToken == regularUserSentryToken

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_sentry_token_detail_edit_self(flask_app_client, db, loginAs, regularUserSentryToken):
    data = {
        'itemType': 'sentry_tokens',
        'itemId': f'{regularUserSentryToken.id}',
        'enabled': '',
        'app_name': 'newName',
        'dsn': 'https://new@sentry.jesassn.org/1'
    }
    regularUserSentryToken = changeOwner(db, loginAs, regularUserSentryToken)
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(f'/sentry_tokens/{regularUserSentryToken.id}', data=data)
        assert202(response)
        assertRenderedTemplate(templates, 'edit_sentry_token.html')
        assertMessageFlashed(templates, "Sentry Token 'newName' saved successfully!", 'success')
        modifiedSentryToken = SentryToken.query.filter_by(id=regularUserSentryToken.id).first()
        assert not modifiedSentryToken.enabled
        assert modifiedSentryToken.app_name == 'newName'
        assert modifiedSentryToken.dsn == 'https://new@sentry.jesassn.org/1'

def test_sentry_token_detail_conflicting_app_name(flask_app_client, db, regularUserInstance, regularUserSentryToken, adminUserSentryToken):
    original = changeOwner(db, regularUserInstance, adminUserSentryToken)
    original.app_name = 'original'
    toBeModified = changeOwner(db, regularUserInstance, regularUserSentryToken)
    db.session.merge(original)
    data = {
        'itemType': 'sentry_tokens',
        'itemId': toBeModified.id,
        'enabled': 'n',
        'app_name': 'original',
        'dsn': 'https://new@sentry.jesassn.org/1'
    }
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(f'/sentry_tokens/{toBeModified.id}', json=data)
        assert response.status_code == 422
        assert response.mimetype == 'text/html'
        assertRenderedTemplate(templates, 'edit_sentry_token.html')
        assert templates['templates'][0][1]['form'].errors['app_name'][0] == 'Already exists.'
        modifiedSentryToken = SentryToken.query.filter_by(id=toBeModified.id).first()
        assert modifiedSentryToken.app_name == toBeModified.app_name