# pylint: disable=missing-docstring
import json


def test_modifying_user_info_by_owner(flask_app_client, regular_user, db):

    saved_default_settings = regular_user.default_settings
    with flask_app_client.login(regular_user):
        response = flask_app_client.patch(f'/api/v1/users/{regular_user.id:d}',
            content_type='application/json',
            data=json.dumps([
                {
                    'op': 'test',
                    'path': '/current_password',
                    'value': regular_user.password_secret,
                },
                {
                    'op': 'replace',
                    'path': '/default_settings',
                    'value': {'database_flavor': 'postgres', 'database_host': 'localhost'},
                },
            ])
        )

    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'id', 'username'}
    assert response.json['id'] == regular_user.id
    assert 'password' not in response.json.keys()

    # Restore original state
    from app.modules.users.models import User

    user1_instance = User.query.get(response.json['id'])
    assert user1_instance.username == regular_user.username
    assert user1_instance.default_settings == {'database_flavor': 'postgres', 'database_host': 'localhost'}

    user1_instance.default_settings = saved_default_settings
    with db.session.begin():
        db.session.merge(user1_instance)

def test_modifying_user_info_by_admin(flask_app_client, admin_user, regular_user, db):

    saved_default_settings = regular_user.default_settings
    with flask_app_client.login(admin_user):
        response = flask_app_client.patch(f'/api/v1/users/{regular_user.id}',
            content_type='application/json',
            data=json.dumps([
                {
                    'op': 'test',
                    'path': '/current_password',
                    'value': admin_user.password_secret,
                },
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
                    'path': '/is_regular_user',
                    'value': False,
                },
                {
                    'op': 'replace',
                    'path': '/is_admin',
                    'value': True,
                },
            ])
        )

    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'id', 'username'}
    assert response.json['id'] == regular_user.id
    assert 'password' not in response.json.keys()

    # Restore original state
    from app.modules.users.models import User

    user1_instance = User.query.get(response.json['id'])
    assert user1_instance.username == regular_user.username
    assert user1_instance.default_settings == {'database_flavor': 'postgres', 'database_host': 'localhost'}
    assert not user1_instance.is_active
    assert not user1_instance.is_regular_user
    assert user1_instance.is_admin

    user1_instance.default_settings = saved_default_settings
    user1_instance.is_active = True
    user1_instance.is_regular_user = True
    user1_instance.is_admin = False
    with db.session.begin():
        db.session.merge(user1_instance)

def test_modifying_user_info_admin_fields_by_not_admin(flask_app_client, regular_user, db):

    with flask_app_client.login(regular_user):
        response = flask_app_client.patch(f'/api/v1/users/{regular_user.id}',
            content_type='application/json',
            data=json.dumps([
                {
                    'op': 'test',
                    'path': '/current_password',
                    'value': regular_user.password_secret,
                },
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
                    'path': '/is_regular_user',
                    'value': False,
                },
                {
                    'op': 'replace',
                    'path': '/is_admin',
                    'value': True,
                },
            ])
        )

    assert response.status_code == 403
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}


def test_modifying_user_info_with_invalid_format_must_fail(flask_app_client, regular_user):

    with flask_app_client.login(regular_user):
        response = flask_app_client.patch(f'/api/v1/users/{regular_user.id}',
            content_type='application/json',
            data=json.dumps([
                {
                    'op': 'test',
                    'path': '/username',
                    'value': '',
                },
                {
                    'op': 'replace',
                    'path': '/default_settings',
                },
            ])
        )

    assert response.status_code == 422
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}

def test_modifying_user_info_with_invalid_password_must_fail(flask_app_client, regular_user):

    with flask_app_client.login(regular_user):
        response = flask_app_client.patch(f'/api/v1/users/{regular_user.id}',
            content_type='application/json',
            data=json.dumps([
                {
                    'op': 'test',
                    'path': '/current_password',
                    'value': "invalid_password",
                },
                {
                    'op': 'replace',
                    'path': '/default_settings',
                    'value': {'database_flavor': 'postgres', 'database_host': 'localhost'},
                },
            ])
        )

    assert response.status_code == 403
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}

def test_modifying_user_info_with_conflict_data_must_fail(
        flask_app_client,
        admin_user,
        regular_user
):

    with flask_app_client.login(regular_user):
        response = flask_app_client.patch(f'/api/v1/users/{regular_user.id}',
            content_type='application/json',
            data=json.dumps([
                {
                    'op': 'test',
                    'path': '/current_password',
                    'value': regular_user.password_secret,
                },
                {
                    'op': 'replace',
                    'path': '/username',
                    'value': admin_user.username,
                },
            ])
        )

    assert response.status_code == 409
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}
