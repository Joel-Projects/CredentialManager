import pytest

from app.modules.user_verifications.models import UserVerification
from tests.params import labels, users
from tests.responseStatuses import assert201, assert422
from tests.utils import assertCreated, assertRenderedTemplate, captured_templates
from . import assert403Create


data = {
    'discord_id': 123456789012345678,
}

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_create_user_verification(flask_app_client, loginAs, regularUserRedditApp):
    with captured_templates(flask_app_client.application) as templates:
        regularUserRedditApp.owner = loginAs
        response = flask_app_client.post('/user_verifications', content_type='application/x-www-form-urlencoded', data=data)
        assert201(response)
        assertRenderedTemplate(templates, 'user_verifications.html')
        userVerification = UserVerification.query.filter_by(discord_id=123456789012345678).first()
        assertCreated(userVerification, data)

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_create_user_verification_with_extra_data(flask_app_client, loginAs, regularUserRedditApp):
    with captured_templates(flask_app_client.application) as templates:
        regularUserRedditApp.owner = loginAs
        response = flask_app_client.post('/user_verifications', content_type='application/x-www-form-urlencoded', data={'extra_data': '{"key": "value"}', **data})
        assert201(response)
        assertRenderedTemplate(templates, 'user_verifications.html')
        userVerification = UserVerification.query.filter_by(discord_id=123456789012345678).first()
        assertCreated(userVerification, data)
        assert userVerification.extra_data == {'key': 'value'}

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_create_user_verification_profile(flask_app_client, loginAs, regularUserRedditApp):
    with captured_templates(flask_app_client.application) as templates:
        regularUserRedditApp.owner = loginAs
        response = flask_app_client.post(f'/profile/user_verifications', content_type='application/x-www-form-urlencoded', data=data)
        assert201(response)
        assertRenderedTemplate(templates, 'user_verifications.html')
        userVerification = UserVerification.query.filter_by(discord_id=123456789012345678).first()
        assertCreated(userVerification, data)

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_create_other_user_user_verification(flask_app_client, loginAs, regular_user, regularUserRedditApp):
    regularUserRedditApp.owner = loginAs
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post('/user_verifications', content_type='application/x-www-form-urlencoded', data={'owner': str(regular_user.id), 'reddit_app': str(regularUserRedditApp.id), **data})
        if loginAs.is_admin or loginAs.is_internal:
            assert201(response)
            assertRenderedTemplate(templates, 'user_verifications.html')
            userVerification = UserVerification.query.filter_by(discord_id=123456789012345678).first()
            assertCreated(userVerification, data)
            assert userVerification.owner == regular_user
        else:
            assert403Create(response, templates)
            userVerification = UserVerification.query.filter_by(discord_id=123456789012345678).first()
            assert userVerification is None

def test_create_user_verification_bad_params(flask_app_client, regularUserInstance):
    with captured_templates(flask_app_client.application) as templates:
        data = {'extra_data': 'invalid data', 'discord_id': 123456789012345678}
        response = flask_app_client.post('/user_verifications', content_type='application/x-www-form-urlencoded', data=data)
        assert response.status_code == 200
        assert response.mimetype == 'application/json'
        userVerification = UserVerification.query.filter_by(discord_id=123456789012345678).first()
        assert userVerification is None

def test_create_user_verification_bad_params_profile(flask_app_client, regularUserInstance):
    with captured_templates(flask_app_client.application) as templates:
        data = {'extra_data': 'invalid data', 'discord_id': 123456789012345678}
        response = flask_app_client.post('/profile/user_verifications', content_type='application/x-www-form-urlencoded', data=data)
        assert422(response)
        userVerification = UserVerification.query.filter_by(discord_id=123456789012345678).first()
        assert userVerification is None