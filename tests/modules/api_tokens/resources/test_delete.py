import pytest

from app.modules.api_tokens.models import ApiToken
from tests.params import labels, users
from tests.utils import assert403, assertSuccess

path = "/api/v1/api_tokens"


@pytest.mark.parametrize("loginAs", users, ids=labels)
def test_deleting_api_token(flask_app_client, loginAs, regularUserApiToken):
    response = flask_app_client.delete(f"{path}/{regularUserApiToken.id}")

    if loginAs.is_admin or loginAs.is_internal:
        assertSuccess(
            response, None, ApiToken, None, deleteItemId=regularUserApiToken.id
        )
    else:
        assert403(
            response,
            ApiToken,
            oldItem=regularUserApiToken,
            internal=True,
            action="deleted",
        )


def test_deleting_self(flask_app_client, db, regularUserInstance, regularUserApiToken):
    regularUserApiToken.owner = regularUserInstance
    db.session.merge(regularUserApiToken)
    response = flask_app_client.delete(f"{path}/{regularUserApiToken.id}")
    assertSuccess(response, None, ApiToken, None, deleteItemId=regularUserApiToken.id)
