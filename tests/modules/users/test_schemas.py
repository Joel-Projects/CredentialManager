from app.modules.users import schemas


def test_BaseUserSchema_dump_empty_input():
    dumped_result = schemas.BaseUserSchema().dump({})
    assert dumped_result.errors == {}
    assert dumped_result.data == {"resource_type": "User"}


def test_BaseUserSchema_dump_userInstance(userInstance):
    userInstance.password = "password"
    dumped_result = schemas.BaseUserSchema().dump(userInstance)
    assert dumped_result.errors == {}
    assert "password" not in dumped_result.data
    assert set(dumped_result.data.keys()) == {"id", "username", "resource_type"}


def test_DetailedUserSchema_dump_userInstance(userInstance):
    userInstance.password = "password"
    dumped_result = schemas.DetailedUserSchema().dump(userInstance)
    assert dumped_result.errors == {}
    assert "password" not in dumped_result.data
    assert set(dumped_result.data.keys()) == {
        "id",
        "username",
        "default_settings",
        "reddit_username",
        "created",
        "updated",
        "is_active",
        "is_regular_user",
        "is_admin",
        "resource_type",
    }
