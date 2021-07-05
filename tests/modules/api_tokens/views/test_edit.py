import pytest

from app.modules.api_tokens.models import ApiToken
from tests.params import labels, users
from tests.responseStatuses import assert202, assert403
from tests.utils import (
    assertMessageFlashed,
    assertRenderedTemplate,
    captured_templates,
    changeOwner,
)

apiTokens = [
    pytest.lazy_fixture("adminUserApiToken"),
    pytest.lazy_fixture("internalUserApiToken"),
    pytest.lazy_fixture("regularUserApiToken"),
]
apiTokenLabels = [
    "admin_user_api_token",
    "internal_user_api_token",
    "regular_user_api_token",
]


@pytest.mark.parametrize("loginAs", users, ids=labels)
@pytest.mark.parametrize("apiToken", apiTokens, ids=apiTokenLabels)
def test_api_token_detail_edit_for_other_user(flask_app_client, loginAs, apiToken):
    data = {
        "itemType": "api_tokens",
        "itemId": f"{apiToken.id}",
        "name": "newName",
        "token": apiToken.token,
        "enabled": "y",
    }
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            f"/api_tokens/{apiToken.id}",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        if apiToken.owner.is_internal and not loginAs.is_internal:
            assert403(response, templates)
            modifiedApiToken = ApiToken.query.filter_by(id=apiToken.id).first()
            assert modifiedApiToken == apiToken
        elif loginAs.is_admin or loginAs.is_internal:
            assert202(response)
            assertRenderedTemplate(templates, "edit_api_token.html")
            assertMessageFlashed(
                templates, "API Token 'newName' saved successfully!", "success"
            )
            modifiedApiToken = ApiToken.query.filter_by(id=apiToken.id).first()
            assert modifiedApiToken.name == "newName"
            assert modifiedApiToken.token == apiToken.token
        else:
            assert403(response, templates)
            assert apiToken == ApiToken.query.filter_by(id=apiToken.id).first()


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_api_token_detail_edit(flask_app_client, loginAs, regularUserApiToken):
    data = {
        "itemType": "api_tokens",
        "itemId": f"{regularUserApiToken.id}",
        "name": "newName",
        "token": regularUserApiToken.token,
        "enabled": "",
    }
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            f"/api_tokens/{regularUserApiToken.id}",
            content_type="application/x-www-form-urlencoded",
            data=data,
        )
        if loginAs.is_admin or loginAs.is_internal:
            assert202(response)
            assertRenderedTemplate(templates, "edit_api_token.html")
            assertMessageFlashed(
                templates, "API Token 'newName' saved successfully!", "success"
            )
            modifiedApiToken = ApiToken.query.filter_by(
                id=regularUserApiToken.id
            ).first()
            assert modifiedApiToken.name == "newName"
        else:
            assert403(response, templates)
            assert (
                regularUserApiToken
                == ApiToken.query.filter_by(id=regularUserApiToken.id).first()
            )


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_api_token_detail_edit_self(flask_app_client, db, loginAs, regularUserApiToken):
    data = {
        "itemType": "api_tokens",
        "itemId": f"{regularUserApiToken.id}",
        "name": "newName",
        "token": regularUserApiToken.token,
        "enabled": "",
    }
    regularUserApiToken = changeOwner(db, loginAs, regularUserApiToken)
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(
            f"/api_tokens/{regularUserApiToken.id}", data=data
        )
        assert202(response)
        assertRenderedTemplate(templates, "edit_api_token.html")
        assertMessageFlashed(
            templates, "API Token 'newName' saved successfully!", "success"
        )
        modifiedApiToken = ApiToken.query.filter_by(id=regularUserApiToken.id).first()
        assert not modifiedApiToken.enabled
        assert modifiedApiToken.name == "newName"


def test_api_token_detail_conflicting_name(
    flask_app_client, db, regularUserInstance, regularUserApiToken, adminUserApiToken
):
    original = changeOwner(db, regularUserInstance, adminUserApiToken)
    original.name = "original"
    toBeModified = changeOwner(db, regularUserInstance, regularUserApiToken)
    db.session.merge(original)
    data = {
        "itemType": "api_tokens",
        "itemId": toBeModified.id,
        "name": "original",
        "token": toBeModified.token,
        "enabled": "",
    }
    with captured_templates(flask_app_client.application) as templates:
        response = flask_app_client.post(f"/api_tokens/{toBeModified.id}", json=data)
        assert response.status_code == 422
        assert response.mimetype == "text/html"
        assertRenderedTemplate(templates, "edit_api_token.html")
        assert (
            templates["templates"][0][1]["form"].errors["name"][0] == "Already exists."
        )
        assert (
            regularUserApiToken
            == ApiToken.query.filter_by(id=regularUserApiToken.id).first()
        )
