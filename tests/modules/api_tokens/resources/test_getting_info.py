import pytest

from app.modules.api_tokens.models import ApiToken
from app.modules.api_tokens.schemas import DetailedApiTokenSchema
from tests.params import labels, users
from tests.utils import assert403, assert_success

path = "/api/v1/api_tokens/"


@pytest.mark.parametrize("login_as", users, ids=labels)
@pytest.mark.parametrize(
    "token_to_get",
    [
        pytest.lazy_fixture("admin_user_api_token"),
        pytest.lazy_fixture("internal_user_api_token"),
        pytest.lazy_fixture("regular_user_api_token"),
    ],
    ids=["get_admin_user_token", "get_internal_user_token", "get_regular_user_token"],
)
def test_getting_api_token_with_id(flask_app_client, login_as, token_to_get):
    response = flask_app_client.get(f"/api/v1/api_tokens/{token_to_get.id}")

    if token_to_get.owner.is_internal:
        if login_as.is_internal:
            assert_success(response, token_to_get.owner, ApiToken, DetailedApiTokenSchema)
        elif login_as.is_admin:
            assert403(response, ApiToken, internal=True)
        else:
            assert403(response, ApiToken, internal=True)
    elif login_as.is_admin or login_as.is_internal:
        assert_success(response, token_to_get.owner, ApiToken, DetailedApiTokenSchema)
    else:
        assert403(response, ApiToken, internal=True)


def test_getting_list_of_api_tokens(flask_app_client, regular_user_instance, regular_user_api_token):
    regular_user_api_token.owner = regular_user_instance
    response = flask_app_client.get(path)

    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert isinstance(response.json, list)
    assert set(response.json[0].keys()) >= {"id", "name"}
    assert response.json[0]["id"] == regular_user_api_token.id
    assert response.json[0]["name"] == regular_user_api_token.name


def test_getting_list_of_api_tokens_owner_id(flask_app_client, regular_user_instance, regular_user_api_token):
    regular_user_api_token.owner = regular_user_instance
    response = flask_app_client.get(path, query_string={"owner_id": regular_user_instance.id})

    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert isinstance(response.json, list)
    assert set(response.json[0].keys()) >= {"id", "name"}
    assert response.json[0]["id"] == regular_user_api_token.id
    assert response.json[0]["name"] == regular_user_api_token.name


def test_getting_list_of_api_tokens_with_admin(
    flask_app_client, regular_user_instance, admin_user_instance, regular_user_api_token
):
    regular_user_api_token.owner = regular_user_instance
    response = flask_app_client.get(path, query_string={"owner_id": regular_user_instance.id})

    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert isinstance(response.json, list)
    assert set(response.json[0].keys()) >= {"id", "name"}
    assert response.json[0]["id"] == regular_user_api_token.id
    assert response.json[0]["name"] == regular_user_api_token.name


def test_getting_list_of_api_tokens_with_owner(flask_app_client, regular_user_instance, regular_user_api_token):
    regular_user_api_token.owner = regular_user_instance
    response = flask_app_client.get(path)

    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert isinstance(response.json, list)
    assert set(response.json[0].keys()) >= {"id", "name"}
    assert response.json[0]["id"] == regular_user_api_token.id
    assert response.json[0]["name"] == regular_user_api_token.name


def test_getting_list_of_api_tokens_for_admin_user_with_regular_user(
    flask_app_client, regular_user_instance, admin_user, admin_user_api_token
):
    admin_user_api_token.owner = admin_user
    response = flask_app_client.get(path, query_string={"owner_id": admin_user.id})

    assert response.status_code == 403
    assert response.content_type == "application/json"
    assert set(response.json.keys()) >= {"status", "message"}


def test_getting_list_of_api_tokens_with_bad_owner_id(flask_app_client, regular_user_instance):
    response = flask_app_client.get(path, query_string={"owner_id": 100500})

    assert response.status_code == 422
    assert response.content_type == "application/json"
    assert set(response.json.keys()) >= {"status", "message"}
