# pylint: disable=missing-docstring
import json

def test_delete_admin_user_by_admin_user(flask_app_client, admin_user, admin_user2):

    userToDelete = admin_user2
    with flask_app_client.login(admin_user):
        response = flask_app_client.delete(f'/api/v1/users/{userToDelete.id}')

    assert response.status_code == 204
    assert response.content_type == 'text/html; charset=utf-8'
    assert response.content_length is None

    from app.modules.users.models import User

    initalUser = User.query.get(userToDelete.id)
    assert initalUser is None

def test_delete_admin_user_by_deactivated_admin_user(flask_app_client, admin_user, deactivated_admin_user2):
    userToDelete = admin_user
    with flask_app_client.login(deactivated_admin_user2):
        response = flask_app_client.delete(f'/api/v1/users/{userToDelete.id}')

    assert response.status_code == 401
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}
    assert response.json['message'] == "The server could not verify that you are authorized to access the URL requested. You either supplied the wrong credentials (e.g. a bad password), or your browser doesn't understand how to supply the credentials required."

    from app.modules.users.models import User

    initalUser = User.query.get(userToDelete.id)
    assert initalUser is not None

def test_delete_admin_user_by_deactivated_regular_user(flask_app_client, admin_user, deactivated_regular_user):
    userToDelete = admin_user
    with flask_app_client.login(deactivated_regular_user):
        response = flask_app_client.delete(f'/api/v1/users/{userToDelete.id}')

    assert response.status_code == 401
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}
    assert response.json['message'] == "The server could not verify that you are authorized to access the URL requested. You either supplied the wrong credentials (e.g. a bad password), or your browser doesn't understand how to supply the credentials required."

    from app.modules.users.models import User

    initalUser = User.query.get(userToDelete.id)
    assert initalUser is not None

def test_delete_admin_user_by_internal_user(flask_app_client, admin_user, internal_user):

    userToDelete = admin_user
    with flask_app_client.login(internal_user):
        response = flask_app_client.delete(f'/api/v1/users/{userToDelete.id}')

    assert response.status_code == 204
    assert response.content_type == 'text/html; charset=utf-8'
    assert response.content_length is None

    from app.modules.users.models import User

    initalUser = User.query.get(userToDelete.id)
    assert initalUser is None

def test_delete_admin_user_by_regular_user(flask_app_client, admin_user, regular_user):

    userToDelete = admin_user
    with flask_app_client.login(regular_user):
        response = flask_app_client.delete(f'/api/v1/users/{userToDelete.id}')

    assert response.status_code == 403
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}
    assert response.json['message'] == "You don't have the permission to access the requested resource."

    from app.modules.users.models import User

    initalUser = User.query.get(userToDelete.id)
    assert initalUser is not None

def test_delete_admin_user_by_self(flask_app_client, admin_user):

    userToDelete = admin_user
    with flask_app_client.login(admin_user):
        response = flask_app_client.delete(f'/api/v1/users/{userToDelete.id}')

    assert response.status_code == 409
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}
    assert response.json['message'] == "You can't delete yourself."

    from app.modules.users.models import User

    initalUser = User.query.get(userToDelete.id)
    assert initalUser is not None

def test_delete_deactivated_admin_user_by_admin_user(flask_app_client, deactivated_admin_user, admin_user):
    userToDelete = deactivated_admin_user
    with flask_app_client.login(admin_user):
        response = flask_app_client.delete(f'/api/v1/users/{userToDelete.id}')

    assert response.status_code == 204
    assert response.content_type == 'text/html; charset=utf-8'
    assert response.content_length is None

    from app.modules.users.models import User

    initalUser = User.query.get(userToDelete.id)
    assert initalUser is None

def test_delete_deactivated_admin_user_by_deactivated_admin_user(flask_app_client, deactivated_admin_user, deactivated_admin_user2):
    userToDelete = deactivated_admin_user
    with flask_app_client.login(deactivated_admin_user2):
        response = flask_app_client.delete(f'/api/v1/users/{userToDelete.id}')

    assert response.status_code == 401
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}
    assert response.json['message'] == "The server could not verify that you are authorized to access the URL requested. You either supplied the wrong credentials (e.g. a bad password), or your browser doesn't understand how to supply the credentials required."

    from app.modules.users.models import User

    initalUser = User.query.get(userToDelete.id)
    assert initalUser is not None

def test_delete_deactivated_admin_user_by_deactivated_regular_user(flask_app_client, deactivated_admin_user, deactivated_regular_user):
    userToDelete = deactivated_admin_user
    with flask_app_client.login(deactivated_regular_user):
        response = flask_app_client.delete(f'/api/v1/users/{userToDelete.id}')

    assert response.status_code == 401
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}
    assert response.json['message'] == "The server could not verify that you are authorized to access the URL requested. You either supplied the wrong credentials (e.g. a bad password), or your browser doesn't understand how to supply the credentials required."

    from app.modules.users.models import User

    initalUser = User.query.get(userToDelete.id)
    assert initalUser is not None

def test_delete_deactivated_admin_user_by_internal_user(flask_app_client, deactivated_admin_user, internal_user):
    userToDelete = deactivated_admin_user
    with flask_app_client.login(internal_user):
        response = flask_app_client.delete(f'/api/v1/users/{userToDelete.id}')

    assert response.status_code == 204
    assert response.content_type == 'text/html; charset=utf-8'
    assert response.content_length is None

    from app.modules.users.models import User

    initalUser = User.query.get(userToDelete.id)
    assert initalUser is None

def test_delete_deactivated_admin_user_by_regular_user(flask_app_client, deactivated_admin_user, regular_user):
    userToDelete = deactivated_admin_user
    with flask_app_client.login(regular_user):
        response = flask_app_client.delete(f'/api/v1/users/{userToDelete.id}')

    assert response.status_code == 403
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}
    assert response.json['message'] == "You don't have the permission to access the requested resource."

    from app.modules.users.models import User

    initalUser = User.query.get(userToDelete.id)
    assert initalUser is not None

def test_delete_deactivated_admin_user_by_self(flask_app_client, deactivated_admin_user):
    userToDelete = deactivated_admin_user
    with flask_app_client.login(deactivated_admin_user):
        response = flask_app_client.delete(f'/api/v1/users/{userToDelete.id}')

    assert response.status_code == 401
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}
    assert response.json['message'] == "The server could not verify that you are authorized to access the URL requested. You either supplied the wrong credentials (e.g. a bad password), or your browser doesn't understand how to supply the credentials required."

    from app.modules.users.models import User

    initalUser = User.query.get(userToDelete.id)
    assert initalUser is not None

def test_delete_deactivated_regular_user_by_admin_user(flask_app_client, deactivated_regular_user, admin_user):
    userToDelete = deactivated_regular_user
    with flask_app_client.login(admin_user):
        response = flask_app_client.delete(f'/api/v1/users/{userToDelete.id}')

    assert response.status_code == 204
    assert response.content_type == 'text/html; charset=utf-8'
    assert response.content_length is None

    from app.modules.users.models import User

    initalUser = User.query.get(userToDelete.id)
    assert initalUser is None

def test_delete_deactivated_regular_user_by_deactivated_admin_user(flask_app_client, deactivated_regular_user, deactivated_admin_user):
    userToDelete = deactivated_regular_user
    with flask_app_client.login(deactivated_admin_user):
        response = flask_app_client.delete(f'/api/v1/users/{userToDelete.id}')

    assert response.status_code == 401
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}
    assert response.json['message'] == "The server could not verify that you are authorized to access the URL requested. You either supplied the wrong credentials (e.g. a bad password), or your browser doesn't understand how to supply the credentials required."

    from app.modules.users.models import User

    initalUser = User.query.get(userToDelete.id)
    assert initalUser is not None

def test_delete_deactivated_regular_user_by_deactivated_regular_user(flask_app_client, deactivated_regular_user, deactivated_regular_user2):
    userToDelete = deactivated_regular_user
    with flask_app_client.login(deactivated_regular_user2):
        response = flask_app_client.delete(f'/api/v1/users/{userToDelete.id}')

    assert response.status_code == 401
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}
    assert response.json['message'] == "The server could not verify that you are authorized to access the URL requested. You either supplied the wrong credentials (e.g. a bad password), or your browser doesn't understand how to supply the credentials required."

    from app.modules.users.models import User

    initalUser = User.query.get(userToDelete.id)
    assert initalUser is not None

def test_delete_deactivated_regular_user_by_internal_user(flask_app_client, deactivated_regular_user, internal_user):
    userToDelete = deactivated_regular_user
    with flask_app_client.login(internal_user):
        response = flask_app_client.delete(f'/api/v1/users/{userToDelete.id}')

    assert response.status_code == 204
    assert response.content_type == 'text/html; charset=utf-8'
    assert response.content_length is None

    from app.modules.users.models import User

    initalUser = User.query.get(userToDelete.id)
    assert initalUser is None

def test_delete_deactivated_regular_user_by_regular_user(flask_app_client, deactivated_regular_user, regular_user):
    userToDelete = deactivated_regular_user
    with flask_app_client.login(regular_user):
        response = flask_app_client.delete(f'/api/v1/users/{userToDelete.id}')

    assert response.status_code == 403
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}
    assert response.json['message'] == "You don't have the permission to access the requested resource."

    from app.modules.users.models import User

    initalUser = User.query.get(userToDelete.id)
    assert initalUser is not None

def test_delete_deactivated_regular_user_by_self(flask_app_client, deactivated_regular_user):
    userToDelete = deactivated_regular_user
    with flask_app_client.login(deactivated_regular_user):
        response = flask_app_client.delete(f'/api/v1/users/{userToDelete.id}')

    assert response.status_code == 401
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}
    assert response.json['message'] == "The server could not verify that you are authorized to access the URL requested. You either supplied the wrong credentials (e.g. a bad password), or your browser doesn't understand how to supply the credentials required."

    from app.modules.users.models import User

    initalUser = User.query.get(userToDelete.id)
    assert initalUser is not None

def test_delete_internal_user_by_admin_user(flask_app_client, admin_user, internal_user):

    userToDelete = internal_user
    with flask_app_client.login(admin_user):
        response = flask_app_client.delete(f'/api/v1/users/{userToDelete.id}')

    assert response.status_code == 403
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}
    assert response.json['message'] == "You don't have the permission to access the requested resource."

    from app.modules.users.models import User

    initalUser = User.query.get(userToDelete.id)
    assert initalUser is not None

def test_delete_internal_user_by_deactivated_admin_user(flask_app_client, internal_user, deactivated_admin_user):
    userToDelete = internal_user
    with flask_app_client.login(deactivated_admin_user):
        response = flask_app_client.delete(f'/api/v1/users/{userToDelete.id}')

    assert response.status_code == 401
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}
    assert response.json['message'] == "The server could not verify that you are authorized to access the URL requested. You either supplied the wrong credentials (e.g. a bad password), or your browser doesn't understand how to supply the credentials required."

    from app.modules.users.models import User

    initalUser = User.query.get(userToDelete.id)
    assert initalUser is not None

def test_delete_internal_user_by_deactivated_regular_user(flask_app_client, internal_user, deactivated_regular_user):
    userToDelete = internal_user
    with flask_app_client.login(deactivated_regular_user):
        response = flask_app_client.delete(f'/api/v1/users/{userToDelete.id}')

    assert response.status_code == 401
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}
    assert response.json['message'] == "The server could not verify that you are authorized to access the URL requested. You either supplied the wrong credentials (e.g. a bad password), or your browser doesn't understand how to supply the credentials required."

    from app.modules.users.models import User

    initalUser = User.query.get(userToDelete.id)
    assert initalUser is not None

def test_delete_internal_user_by_internal_user(flask_app_client, internal_user, internal_user2):

    userToDelete = internal_user
    with flask_app_client.login(internal_user2):
        response = flask_app_client.delete(f'/api/v1/users/{userToDelete.id}')

    assert response.status_code == 204
    assert response.content_type == 'text/html; charset=utf-8'
    assert response.content_length is None

    from app.modules.users.models import User

    initalUser = User.query.get(userToDelete.id)
    assert initalUser is None

def test_delete_internal_user_by_regular_user(flask_app_client, regular_user, internal_user):

    userToDelete = internal_user
    with flask_app_client.login(regular_user):
        response = flask_app_client.delete(f'/api/v1/users/{userToDelete.id}')

    assert response.status_code == 403
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}
    assert response.json['message'] == "You don't have the permission to access the requested resource."

    from app.modules.users.models import User

    initalUser = User.query.get(userToDelete.id)
    assert initalUser is not None

def test_delete_internal_user_by_self(flask_app_client, internal_user):

    userToDelete = internal_user
    with flask_app_client.login(internal_user):
        response = flask_app_client.delete(f'/api/v1/users/{userToDelete.id}')

    assert response.status_code == 409
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}
    assert response.json['message'] == "You can't delete yourself."

    from app.modules.users.models import User

    initalUser = User.query.get(userToDelete.id)
    assert initalUser is not None

def test_delete_regular_user_by_admin_user(flask_app_client, admin_user, regular_user):

    userToDelete = regular_user
    with flask_app_client.login(admin_user):
        response = flask_app_client.delete(f'/api/v1/users/{userToDelete.id}')

    assert response.status_code == 204
    assert response.content_type == 'text/html; charset=utf-8'
    assert response.content_length is None

    from app.modules.users.models import User

    initalUser = User.query.get(userToDelete.id)
    assert initalUser is None

def test_delete_regular_user_by_deactivated_admin_user(flask_app_client, regular_user, deactivated_admin_user):
    userToDelete = regular_user
    with flask_app_client.login(deactivated_admin_user):
        response = flask_app_client.delete(f'/api/v1/users/{userToDelete.id}')

    assert response.status_code == 401
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}
    assert response.json['message'] == "The server could not verify that you are authorized to access the URL requested. You either supplied the wrong credentials (e.g. a bad password), or your browser doesn't understand how to supply the credentials required."

    from app.modules.users.models import User

    initalUser = User.query.get(userToDelete.id)
    assert initalUser is not None

def test_delete_regular_user_by_deactivated_regular_user(flask_app_client, regular_user, deactivated_regular_user):
    userToDelete = regular_user
    with flask_app_client.login(deactivated_regular_user):
        response = flask_app_client.delete(f'/api/v1/users/{userToDelete.id}')

    assert response.status_code == 401
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}
    assert response.json['message'] == "The server could not verify that you are authorized to access the URL requested. You either supplied the wrong credentials (e.g. a bad password), or your browser doesn't understand how to supply the credentials required."

    from app.modules.users.models import User

    initalUser = User.query.get(userToDelete.id)
    assert initalUser is not None

def test_delete_regular_user_by_internal_user(flask_app_client, internal_user, regular_user):

    userToDelete = regular_user
    with flask_app_client.login(internal_user):
        response = flask_app_client.delete(f'/api/v1/users/{userToDelete.id}')

    assert response.status_code == 204
    assert response.content_type == 'text/html; charset=utf-8'
    assert response.content_length is None

    from app.modules.users.models import User

    initalUser = User.query.get(userToDelete.id)
    assert initalUser is None

def test_delete_regular_user_by_regular_user(flask_app_client, regular_user, regular_user2):

    userToDelete = regular_user2
    with flask_app_client.login(regular_user):
        response = flask_app_client.delete(f'/api/v1/users/{userToDelete.id}')

    assert response.status_code == 403
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}
    assert response.json['message'] == "You don't have the permission to access the requested resource."

    from app.modules.users.models import User

    initalUser = User.query.get(userToDelete.id)
    assert initalUser is not None

def test_delete_regular_user_by_self(flask_app_client, regular_user):

    userToDelete = regular_user
    with flask_app_client.login(regular_user):
        response = flask_app_client.delete(f'/api/v1/users/{userToDelete.id}')

    assert response.status_code == 403
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= {'status', 'message'}
    assert response.json['message'] == "You don't have the permission to access the requested resource."

    from app.modules.users.models import User

    initalUser = User.query.get(userToDelete.id)
    assert initalUser is not None