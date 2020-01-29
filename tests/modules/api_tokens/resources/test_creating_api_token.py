
def test_creating_api_token_for_admin_user_by_admin_user(flask_app_client, admin_user, admin_user2):
    tokenOwner = admin_user
    with flask_app_client.login(admin_user2):
        response = flask_app_client.post('/api/v1/api_tokens/',data={'name': 'testToken', 'owner_id': tokenOwner.id})

    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= { 'id', 'name', 'token', 'owner_id'}
    assert isinstance(response.json['id'], int)
    assert isinstance(response.json['name'], str)
    assert isinstance(response.json['token'], str)
    assert isinstance(response.json['owner_id'], int)

    from app.modules.api_tokens.models import ApiToken

    createdApiToken = ApiToken.query.filter_by(id=response.json['id']).first()
    assert createdApiToken is not None

    assert response.json['id'] == createdApiToken.id
    assert response.json['name'] == createdApiToken.name
    assert response.json['token'] == createdApiToken.token
    assert response.json['owner_id'] == createdApiToken.owner_id
    assert response.json['owner_id'] == tokenOwner.id

def test_creating_api_token_for_admin_user_by_deactivated_admin_user(flask_app_client, admin_user, deactivated_admin_user):
    tokenOwner = admin_user
    with flask_app_client.login(deactivated_admin_user):
        response = flask_app_client.post('/api/v1/api_tokens/',data={'name': 'testToken', 'owner_id': tokenOwner.id})

    assert response.status_code == 401
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}
    assert response.json['message'] == "The server could not verify that you are authorized to access the URL requested. You either supplied the wrong credentials (e.g. a bad password), or your browser doesn't understand how to supply the credentials required."

    from app.modules.api_tokens.models import ApiToken

    dbApiToken = ApiToken.query.first()
    assert dbApiToken is None

def test_creating_api_token_for_admin_user_by_internal_user(flask_app_client, admin_user, internal_user):
    tokenOwner = admin_user
    with flask_app_client.login(internal_user):
        response = flask_app_client.post('/api/v1/api_tokens/',data={'name': 'testToken', 'owner_id': tokenOwner.id})

    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= { 'id', 'name', 'token', 'owner_id'}
    assert isinstance(response.json['id'], int)
    assert isinstance(response.json['name'], str)
    assert isinstance(response.json['token'], str)
    assert isinstance(response.json['owner_id'], int)

    from app.modules.api_tokens.models import ApiToken

    createdApiToken = ApiToken.query.filter_by(id=response.json['id']).first()
    assert createdApiToken is not None

    assert response.json['id'] == createdApiToken.id
    assert response.json['name'] == createdApiToken.name
    assert response.json['token'] == createdApiToken.token
    assert response.json['owner_id'] == createdApiToken.owner_id
    assert response.json['owner_id'] == tokenOwner.id

def test_creating_api_token_for_admin_user_by_regular_user(flask_app_client, admin_user, regular_user):
    tokenOwner = admin_user
    with flask_app_client.login(regular_user):
        response = flask_app_client.post('/api/v1/api_tokens/',data={'name': 'testToken', 'owner_id': tokenOwner.id})

    assert response.status_code == 403
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}
    assert response.json['message'] == "You don't have the permission to create API Tokens for other users."

def test_creating_api_token_for_admin_user_by_self(flask_app_client, admin_user):
    tokenOwner = admin_user
    with flask_app_client.login(admin_user):
        response = flask_app_client.post('/api/v1/api_tokens/',data={'name': 'testToken', 'owner_id': tokenOwner.id})

    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= { 'id', 'name', 'token', 'owner_id'}
    assert isinstance(response.json['id'], int)
    assert isinstance(response.json['name'], str)
    assert isinstance(response.json['token'], str)
    assert isinstance(response.json['owner_id'], int)

    from app.modules.api_tokens.models import ApiToken

    createdApiToken = ApiToken.query.filter_by(id=response.json['id']).first()
    assert createdApiToken is not None

    assert response.json['id'] == createdApiToken.id
    assert response.json['name'] == createdApiToken.name
    assert response.json['token'] == createdApiToken.token
    assert response.json['owner_id'] == createdApiToken.owner_id
    assert response.json['owner_id'] == tokenOwner.id


def test_creating_api_token_for_internal_user_by_admin_user(flask_app_client, internal_user, admin_user):
    tokenOwner = internal_user
    with flask_app_client.login(admin_user):
        response = flask_app_client.post('/api/v1/api_tokens/',data={'name': 'testToken', 'owner_id': tokenOwner.id})

    assert response.status_code == 403
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}
    assert response.json['message'] == "You don't have the permission to create API Tokens for internal users."

def test_creating_api_token_for_internal_user_by_deactivated_admin_user(flask_app_client, internal_user, deactivated_admin_user):
    tokenOwner = internal_user
    with flask_app_client.login(deactivated_admin_user):
        response = flask_app_client.post('/api/v1/api_tokens/',data={'name': 'testToken', 'owner_id': tokenOwner.id})

    assert response.status_code == 401
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}
    assert response.json['message'] == "The server could not verify that you are authorized to access the URL requested. You either supplied the wrong credentials (e.g. a bad password), or your browser doesn't understand how to supply the credentials required."

    from app.modules.api_tokens.models import ApiToken

    dbApiToken = ApiToken.query.first()
    assert dbApiToken is None

def test_creating_api_token_for_internal_user_by_internal_user(flask_app_client, internal_user, internal_user2):
    tokenOwner = internal_user
    with flask_app_client.login(internal_user2):
        response = flask_app_client.post('/api/v1/api_tokens/',data={'name': 'testToken', 'owner_id': tokenOwner.id})

    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= { 'id', 'name', 'token', 'owner_id'}
    assert isinstance(response.json['id'], int)
    assert isinstance(response.json['name'], str)
    assert isinstance(response.json['token'], str)
    assert isinstance(response.json['owner_id'], int)

    from app.modules.api_tokens.models import ApiToken

    createdApiToken = ApiToken.query.filter_by(id=response.json['id']).first()
    assert createdApiToken is not None

    assert response.json['id'] == createdApiToken.id
    assert response.json['name'] == createdApiToken.name
    assert response.json['token'] == createdApiToken.token
    assert response.json['owner_id'] == createdApiToken.owner_id
    assert response.json['owner_id'] == tokenOwner.id

def test_creating_api_token_for_internal_user_by_regular_user(flask_app_client, internal_user, regular_user):
    tokenOwner = internal_user
    with flask_app_client.login(regular_user):
        response = flask_app_client.post('/api/v1/api_tokens/',data={'name': 'testToken', 'owner_id': tokenOwner.id})

    assert response.status_code == 403
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}
    assert response.json['message'] == "You don't have the permission to create API Tokens for other users."

def test_creating_api_token_for_internal_user_by_self(flask_app_client, internal_user):
    tokenOwner = internal_user
    with flask_app_client.login(internal_user):
        response = flask_app_client.post('/api/v1/api_tokens/',data={'name': 'testToken', 'owner_id': tokenOwner.id})

    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= { 'id', 'name', 'token', 'owner_id'}
    assert isinstance(response.json['id'], int)
    assert isinstance(response.json['name'], str)
    assert isinstance(response.json['token'], str)
    assert isinstance(response.json['owner_id'], int)

    from app.modules.api_tokens.models import ApiToken

    createdApiToken = ApiToken.query.filter_by(id=response.json['id']).first()
    assert createdApiToken is not None

    assert response.json['id'] == createdApiToken.id
    assert response.json['name'] == createdApiToken.name
    assert response.json['token'] == createdApiToken.token
    assert response.json['owner_id'] == createdApiToken.owner_id
    assert response.json['owner_id'] == tokenOwner.id

def test_creating_api_token_for_regular_user_by_admin_user(flask_app_client, regular_user, admin_user):
    tokenOwner = regular_user
    with flask_app_client.login(admin_user):
        response = flask_app_client.post('/api/v1/api_tokens/',data={'name': 'testToken', 'owner_id': tokenOwner.id})

    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= { 'id', 'name', 'token', 'owner_id'}
    assert isinstance(response.json['id'], int)
    assert isinstance(response.json['name'], str)
    assert isinstance(response.json['token'], str)
    assert isinstance(response.json['owner_id'], int)

    from app.modules.api_tokens.models import ApiToken

    createdApiToken = ApiToken.query.filter_by(id=response.json['id']).first()
    assert createdApiToken is not None

    assert response.json['id'] == createdApiToken.id
    assert response.json['name'] == createdApiToken.name
    assert response.json['token'] == createdApiToken.token
    assert response.json['owner_id'] == createdApiToken.owner_id
    assert response.json['owner_id'] == tokenOwner.id

def test_creating_api_token_for_regular_user_by_regular_user(flask_app_client, regular_user, regular_user2):
    with flask_app_client.login(regular_user):
        response = flask_app_client.post('/api/v1/api_tokens/', data={'name': 'testToken', 'owner_id': regular_user2.id})

    assert response.status_code == 403
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}
    assert response.json['message'] == "You don't have the permission to create API Tokens for other users."
    
def test_creating_api_token_for_non_existent_user_by_admin_user(flask_app_client, admin_user):
    with flask_app_client.login(admin_user):
        response = flask_app_client.post('/api/v1/api_tokens/', data={'name': 'testToken', 'owner_id': 4})

    assert response.status_code == 403
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}
    assert response.json['message'] == "You don't have the permission to create API Tokens for other users."

def test_creating_api_token_for_non_existent_user_by_internal_user(flask_app_client, internal_user):
    with flask_app_client.login(internal_user):
        response = flask_app_client.post('/api/v1/api_tokens/', data={'name': 'testToken', 'owner_id': 4})

    assert response.status_code == 403
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}
    assert response.json['message'] == "You don't have the permission to create API Tokens for other users."