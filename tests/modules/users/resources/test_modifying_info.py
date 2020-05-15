import json

from app.modules.users.models import User


data = [
    {
        'op': 'replace',
        'path': '/default_settings',
        'value': {'database_flavor': 'postgres', 'database_host': 'localhost'},
    },
    {
        'op': 'replace',
        'path': '/is_active',
        'value': False,
    },
    {
        'op': 'replace',
        'path': '/is_admin',
        'value': True,
    },
]

def assertCorrectStructure(response):
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}

def assertSuccess(db, regularUserInstance, response, saved_default_settings):
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'id', 'username'}
    assert response.json['id'] == regularUserInstance.id
    assert 'password' not in response.json.keys()
    user1_instance = User.query.get(response.json['id'])
    assert user1_instance.username == regularUserInstance.username
    assert user1_instance.defaultSettings == {'database_flavor': 'postgres', 'database_host': 'localhost'}
    user1_instance.default_settings = saved_default_settings
    user1_instance.is_active = True
    user1_instance.is_regular_user = True
    user1_instance.is_admin = False
    with db.session.begin():
        db.session.merge(user1_instance)

def test_modifying_user_info_by_owner(flask_app_client, regularUserInstance, db):
    saved_default_settings = regularUserInstance.default_settings
    response = flask_app_client.patch(f'/api/v1/users/{regularUserInstance.id}', content_type='application/json', data=json.dumps([{'op': 'replace', 'path': '/default_settings', 'value': {'database_flavor': 'postgres', 'database_host': 'localhost'}, }]))

    assertSuccess(db, regularUserInstance, response, saved_default_settings)

def test_modifying_user_info_by_admin(flask_app_client, adminUserInstance, regular_user, db):
    saved_default_settings = regular_user.default_settings
    response = flask_app_client.patch(f'/api/v1/users/{regular_user.id}', content_type='application/json', data=json.dumps(data))

    assertSuccess(db, regular_user, response, saved_default_settings)

def test_modifying_user_info_admin_fields_by_not_admin(flask_app_client, regularUserInstance, db):
    data = [{'op': 'replace', 'path': '/is_regular_user', 'value': False, }]
    response = flask_app_client.patch(f'/api/v1/users/{regularUserInstance.id}', content_type='application/json', data=json.dumps(data))

    assert response.status_code == 403
    assertCorrectStructure(response)

def test_modifying_user_info_admin_fields_by_not_admin(flask_app_client, regularUserInstance, db):
    response = flask_app_client.patch(f'/api/v1/users/{regularUserInstance.id}', content_type='application/json', data=json.dumps(data))

    assert response.status_code == 406
    assertCorrectStructure(response)

def test_modifying_user_info_with_invalid_format_must_fail(flask_app_client, regularUserInstance):
    response = flask_app_client.patch(f'/api/v1/users/{regularUserInstance.id}', content_type='application/json', data=json.dumps([{'op': 'test', 'path': '/username', 'value': '', }, {'op': 'replace', 'path': '/default_settings', }, ]))

    assert response.status_code == 422
    assertCorrectStructure(response)

def test_modifying_user_info_with_conflict_data_must_fail(flask_app_client, admin_user, regularUserInstance):
    response = flask_app_client.patch(f'/api/v1/users/{regularUserInstance.id}', content_type='application/json', data=json.dumps([{'op': 'replace', 'path': '/username', 'value': admin_user.username}]))

    assert response.status_code == 409
    assertCorrectStructure(response)