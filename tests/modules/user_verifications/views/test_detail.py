import pytest

from tests.params import labels, users
from tests.responseStatuses import assert200, assert403, assert404
from tests.utils import assertRenderedTemplate, captured_templates, changeOwner


@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_user_verification_detail(flask_app_client, loginAs, regularUserUserVerification):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get(f'/user_verifications/{regularUserUserVerification.id}')
        if loginAs.is_admin or loginAs.is_internal:
            assert200(response)
            assertRenderedTemplate(templates, 'edit_user_verification.html')
        else:
            assert403(response, templates)

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_user_verification_detail_self(flask_app_client, db, loginAs, regularUserUserVerification):
    changeOwner(db, loginAs, regularUserUserVerification)
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get(f'/profile/user_verifications')
        assert200(response)
        assertRenderedTemplate(templates, 'user_verifications.html')

def test_non_existant_user_verification_detail(flask_app_client, regular_user):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get(f'/user_verifications/1')
        assert404(response, templates)