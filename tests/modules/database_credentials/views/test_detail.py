import pytest

from tests.params import labels, users
from tests.responseStatuses import assert200, assert403, assert404
from tests.utils import assertRenderedTemplate, captured_templates, changeOwner


@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_database_credential_detail(flask_app_client, loginAs, regularUserDatabaseCredential):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get(f'/database_credentials/{regularUserDatabaseCredential.id}')
        if loginAs.is_admin or loginAs.is_internal:
            assert200(response)
            assertRenderedTemplate(templates, 'edit_database_credential.html')
        else:
            assert403(response, templates)

@pytest.mark.parametrize('loginAs', users, ids=labels)
def test_database_credential_detail_self(flask_app_client, db, loginAs, regularUserDatabaseCredential):
    changeOwner(db, loginAs, regularUserDatabaseCredential)
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get(f'/profile/database_credentials')
        assert200(response)
        assertRenderedTemplate(templates, 'database_credentials.html')

def test_non_existant_database_credential_detail(flask_app_client, regular_user):
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.get(f'/database_credentials/1')
        assert404(response, templates)