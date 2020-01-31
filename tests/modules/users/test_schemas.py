# encoding: utf-8
# pylint: disable=invalid-name,missing-docstring

from app.modules.users import schemas


def test_BaseUserSchema_dump_empty_input():
    dumped_result = schemas.BaseUserSchema().dump({})
    assert dumped_result.errors == {}
    assert dumped_result.data == {}

def test_BaseUserSchema_dump_user_instance(user_instance):
    user_instance.password = "password"
    dumped_result = schemas.BaseUserSchema().dump(user_instance)
    assert dumped_result.errors == {}
    assert 'password' not in dumped_result.data
    assert set(dumped_result.data.keys()) == {
        'id',
        'username'
    }

def test_DetailedUserSchema_dump_user_instance(user_instance):
    user_instance.password = "password"
    dumped_result = schemas.DetailedUserSchema().dump(user_instance)
    assert dumped_result.errors == {}
    assert 'password' not in dumped_result.data
    assert set(dumped_result.data.keys()) == {
        'id',
        'username',
        'default_redirect_uri',
        'created',
        'updated',
        'is_active',
        'is_regular_user',
        'is_admin',
    }