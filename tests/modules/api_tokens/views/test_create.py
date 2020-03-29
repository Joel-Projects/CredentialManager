import itertools

import pytest

from app.modules.api_tokens.models import ApiToken
from tests.params import labels, users
from tests.responseStatuses import assert201, assert401, assert422, assert403Create
from tests.utils import assertRenderedTemplate, captured_templates


def assertCreated(length):
    apiToken = ApiToken.query.filter_by(name='api_token').first()
    assert apiToken is not None
    assert len(apiToken.token) == length
    assert apiToken.length == length
    return apiToken

@pytest.mark.parametrize('length', itertools.chain(range(16, 56, 8), [64]))
def test_create_api_token_length(flask_app_client, regularUserInstance, length):
    with captured_templates(flask_app_client.application) as templates:
        data = {'length': str(length), 'name': 'api_token'}
        response = flask_app_client.post('/api_tokens', content_type='application/x-www-form-urlencoded', data=data)
        assert201(response)
        assertRenderedTemplate(templates, 'api_tokens.html')
        assertCreated(length)

@pytest.mark.parametrize('length', itertools.chain(range(16, 56, 8), [64]))
def test_create_api_token_length_profile(flask_app_client, regularUserInstance, length):
    with captured_templates(flask_app_client.application) as templates:
        data = {'length': str(length), 'name': 'api_token'}
        response = flask_app_client.post('/profile/api_tokens', content_type='application/x-www-form-urlencoded', data=data)
        assert201(response)
        assertRenderedTemplate(templates, 'api_tokens.html')
        assertCreated(length)

@pytest.mark.parametrize('loginAs', [pytest.lazy_fixture('admin_user'), pytest.lazy_fixture('internal_user'), pytest.lazy_fixture('regular_user')], ids=labels)
@pytest.mark.parametrize('enabled', ['y', ''])
def test_create_api_token_enabled(flask_app_client, flask_app, loginAs, enabled):
    with captured_templates(flask_app_client.application) as templates:
        data = {'name': 'api_token', 'enabled': enabled}
        with flask_app_client.login(loginAs) as client:
            response = client.post(f'/api_tokens', content_type='application/x-www-form-urlencoded', data=data)
        assert201(response)
        apiToken = assertCreated(32)
        assert apiToken.enabled == bool(enabled)
        response = flask_app.test_client().get('/api/v1/users/me', headers={'X-API-KEY': apiToken.token})
        if enabled:
            assert response.status_code == 200
            assert response.mimetype == 'application/json'
            assert response.json['username'] == loginAs.username
        else:
            assert401(response)

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_create_api_token_other_user(flask_app_client, loginAs, regular_user):
    with captured_templates(flask_app_client.application) as templates:
        data = {'name': 'api_token', 'owner': regular_user.id}
        response = flask_app_client.post('/api_tokens', content_type='application/x-www-form-urlencoded', data=data)
        if loginAs.is_admin or loginAs.is_internal:
            assert201(response)
            assertRenderedTemplate(templates, 'api_tokens.html')
            assertCreated(32)
        else:
            assert403Create(response)
            apiToken = ApiToken.query.filter_by(name='api_token').first()
            assert apiToken is None

def test_create_api_token_bad_params(flask_app_client, regularUserInstance):
    with captured_templates(flask_app_client.application) as templates:
        data = {'name': 'ap', 'length': 500}
        response = flask_app_client.post('/api_tokens', content_type='application/x-www-form-urlencoded', data=data)
        assert response.status_code == 200
        assert response.mimetype == 'application/json'
        apiToken = ApiToken.query.filter_by(name='api_token').first()
        assert apiToken is None
        assert response.json['errors']['length'][0] == 'Not a valid choice'
        assert response.json['errors']['name'][0] == 'Field must be at least 3 characters long.'

def test_create_api_token_bad_params_profile(flask_app_client, regularUserInstance):
    with captured_templates(flask_app_client.application) as templates:
        data = {'name': 'ap', 'length': 500}
        response = flask_app_client.post('/profile/api_tokens', content_type='application/x-www-form-urlencoded', data=data)
        assert422(response)
        apiToken = ApiToken.query.filter_by(name='api_token').first()
        assert apiToken is None
        assert response.json['errors']['length'][0] == 'Not a valid choice'
        assert response.json['errors']['name'][0] == 'Field must be at least 3 characters long.'