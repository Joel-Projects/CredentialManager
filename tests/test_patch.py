import json

from app.modules.users.models import User
from tests.utils import assert422


data = [
    {
        'op': 'test',
        'path': '/is_admin',
        'value': False,
    },
    {
        'op': 'copy',
        'fromPath': '/is_active',
        'path': '/is_admin',
    }
]


def test_patch_operations(flask_app_client, adminUserInstance, regular_user, db):
    flask_app_client.patch(f'/api/v1/users/{regular_user.id:d}', content_type='application/json', data=json.dumps(data))
    assert regular_user.is_active
    assert regular_user.is_admin

def test_bad_patch_bad_path(flask_app_client, adminUserInstance, regular_user, db):
    response = flask_app_client.patch(f'/api/v1/users/{regular_user.id:d}', content_type='application/json', data=json.dumps([{'op': 'test','path': 'is_admin','value': True,}]))
    assert422(response, User, [('0', {'path': ['Not a valid choice.'], '_schema': ['Path is required and must always begin with /']})], oldItem=regular_user, action='patch')

def test_bad_patch_bad_field(flask_app_client, adminUserInstance, regular_user, db):
    response = flask_app_client.patch(f'/api/v1/users/{regular_user.id:d}', content_type='application/json', data=json.dumps([{'op': 'replace','path': '/bad_field','value': True,}]))
    assert422(response, User, [('0', {'path': ['Not a valid choice.'], '_schema': ['Path is required and must always begin with /']})], oldItem=regular_user, action='patch')
