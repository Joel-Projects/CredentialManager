
def test_getting_list_of_api_tokens(flask_app_client, regular_user, regularUserApiToken):

    with flask_app_client.login(regular_user):
        response = flask_app_client.get('/api/v1/api_tokens/')

    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert isinstance(response.json, list)
    assert set(response.json[0].keys()) >= {'id', 'name'}
    assert response.json[0]['id'] == regularUserApiToken.id
    assert response.json[0]['name'] == regularUserApiToken.name

def test_getting_list_of_api_tokens_with_admin(flask_app_client, regular_user, admin_user, regularUserApiToken):

    with flask_app_client.login(admin_user):
        response = flask_app_client.get('/api/v1/api_tokens/', query_string={'owner_id': regular_user.id})

    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert isinstance(response.json, list)
    assert set(response.json[0].keys()) >= {'id', 'name'}
    assert response.json[0]['id'] == regularUserApiToken.id
    assert response.json[0]['name'] == regularUserApiToken.name

def test_getting_list_of_api_tokens_with_owner(flask_app_client, regular_user, regularUserApiToken):

    with flask_app_client.login(regular_user):
        response = flask_app_client.get('/api/v1/api_tokens/')

    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert isinstance(response.json, list)
    assert set(response.json[0].keys()) >= {'id', 'name'}
    assert response.json[0]['id'] == regularUserApiToken.id
    assert response.json[0]['name'] == regularUserApiToken.name

def test_getting_list_of_api_tokens_with_owner_with_id(flask_app_client, regular_user, regularUserApiToken):

    with flask_app_client.login(regular_user):
        response = flask_app_client.get('/api/v1/api_tokens/', query_string={'owner_id': regular_user.id})

    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert isinstance(response.json, list)
    assert set(response.json[0].keys()) >= {'id', 'name'}
    assert response.json[0]['id'] == regularUserApiToken.id
    assert response.json[0]['name'] == regularUserApiToken.name

def test_getting_list_of_api_tokens_for_admin_user_with_regular_user(flask_app_client, regular_user, admin_user):

    with flask_app_client.login(regular_user):
        response = flask_app_client.get('/api/v1/api_tokens/', query_string={'owner_id': admin_user.id})

    assert response.status_code == 403
    assert response.content_type == 'application/json'
    assert set(response.json.keys()) >= {'status', 'message'}

def test_getting_list_of_api_tokens_with_bad_owner_id(flask_app_client, regular_user):

    with flask_app_client.login(regular_user):
        response = flask_app_client.get('/api/v1/api_tokens/', query_string={'owner_id': 100500})

    assert response.status_code == 422
    assert response.content_type == 'application/json'
    assert set(response.json.keys()) >= {'status', 'message'}