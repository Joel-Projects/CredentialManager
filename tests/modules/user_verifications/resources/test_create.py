import pytest

from app.modules.user_verifications.models import UserVerification
from app.modules.user_verifications.schemas import DetailedUserVerificationSchema
from tests.params import labels, users
from tests.utils import assert403, assert422, assertSuccess


path = '/api/v1/user_verifications/'
data = {
    'user_id': 123456789012345678
}

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_creating_user_verification(flask_app_client, loginAs, regular_user, redditApp):
    response = flask_app_client.post(path, data={'owner_id': regular_user.id, 'reddit_app_id': redditApp.id, **data})

    if loginAs.is_admin or loginAs.is_internal:
        assertSuccess(response, regular_user, UserVerification, DetailedUserVerificationSchema)
    else:
        assert403(response, UserVerification, action='create')

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_creating_user_verification_existing(flask_app_client, loginAs, regular_user, redditApp, regularUserUserVerification):

    response = flask_app_client.post(path, data={'owner_id': regular_user.id, 'reddit_app_id': redditApp.id, 'user_id': regularUserUserVerification.user_id})

    if loginAs.is_admin or loginAs.is_internal:
        assertSuccess(response, regular_user, UserVerification, DetailedUserVerificationSchema)
    else:
        assert403(response, UserVerification, action='create')

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_creating_user_verification_with_extra_data(flask_app_client, loginAs, redditApp):
    response = flask_app_client.post(path, data={'reddit_app_id': redditApp.id, 'extra_data': '{"key": "value"}', **data})

    if loginAs.is_admin or loginAs.is_internal:
        assertSuccess(response, loginAs, UserVerification, DetailedUserVerificationSchema)
    else:
        assert422(response, UserVerification, messageAttrs=[('reddit_app_id', ['You don\'t have the permission to create User Verifications with other users\' Reddit Apps.'])])

def test_creating_user_verification_for_self(flask_app_client, regularUserInstance, redditApp):
    redditApp.owner = regularUserInstance
    response = flask_app_client.post(path, data={'reddit_app_id': redditApp.id, **data})

    assertSuccess(response, regularUserInstance, UserVerification, DetailedUserVerificationSchema)

def test_creating_user_verification_for_self_with_owner(flask_app_client, regularUserInstance, redditApp):
    redditApp.owner = regularUserInstance
    response = flask_app_client.post(path, data={'owner_id': regularUserInstance.id, 'reddit_app_id': redditApp.id, **data})

    assertSuccess(response, regularUserInstance, UserVerification, DetailedUserVerificationSchema)