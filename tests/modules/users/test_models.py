import pytest

from app.modules.users import models


def test_User_repr(userInstance):
    assert len(str(userInstance)) > 0


def test_User_auth(userInstance):
    assert userInstance.is_authenticated
    assert not userInstance.is_anonymous


@pytest.mark.parametrize(
    "init_static_roles,is_internal,is_admin,is_regular_user,is_active",
    [
        (_init_static_roles, _is_internal, _is_admin, _is_regular_user, _is_active)
        for _init_static_roles in (
            0,
            (
                models.User.StaticRoles.INTERNAL.mask
                | models.User.StaticRoles.ADMIN.mask
                | models.User.StaticRoles.REGULAR_USER.mask
                | models.User.StaticRoles.ACTIVE.mask
            ),
        )
        for _is_internal in (False, True)
        for _is_admin in (False, True)
        for _is_regular_user in (False, True)
        for _is_active in (False, True)
    ],
)
def test_User_static_roles_setting(
    init_static_roles, is_internal, is_admin, is_regular_user, is_active, userInstance
):
    """
    Static User Roles are saved as bit flags into one ``static_roles``
    integer field. Ideally, it would be better implemented as a custom field,
    and the plugin would be tested separately, but for now this implementation
    is fine, so we test it as it is.
    """
    userInstance.static_roles = init_static_roles

    if is_internal:
        userInstance.setStaticRole(userInstance.StaticRoles.INTERNAL)
    else:
        userInstance.unsetStaticRole(userInstance.StaticRoles.INTERNAL)

    if is_admin:
        userInstance.setStaticRole(userInstance.StaticRoles.ADMIN)
    else:
        userInstance.unsetStaticRole(userInstance.StaticRoles.ADMIN)

    if is_regular_user:
        userInstance.setStaticRole(userInstance.StaticRoles.REGULAR_USER)
    else:
        userInstance.unsetStaticRole(userInstance.StaticRoles.REGULAR_USER)

    if is_active:
        userInstance.setStaticRole(userInstance.StaticRoles.ACTIVE)
    else:
        userInstance.unsetStaticRole(userInstance.StaticRoles.ACTIVE)

    assert userInstance.hasStaticRole(userInstance.StaticRoles.INTERNAL) is is_internal
    assert userInstance.hasStaticRole(userInstance.StaticRoles.ADMIN) is is_admin
    assert (
        userInstance.hasStaticRole(userInstance.StaticRoles.REGULAR_USER)
        is is_regular_user
    )
    assert userInstance.hasStaticRole(userInstance.StaticRoles.ACTIVE) is is_active
    assert userInstance.is_internal is is_internal
    assert userInstance.is_admin is is_admin
    assert userInstance.is_regular_user is is_regular_user
    assert userInstance.is_active is is_active

    if not is_active and not is_regular_user and not is_admin and not is_internal:
        assert userInstance.static_roles == 0


def test_User_check_owner(userInstance):
    assert userInstance.check_owner(userInstance)
    assert not userInstance.check_owner(models.User())
    assert isinstance(userInstance.__repr__(), str)


def test_User_findWithPassword(patch_user_password_scheme, db):
    def create_user(username, password):
        user = models.User(username=username, password=password)
        return user

    user1 = create_user("user1", "user1password")
    user2 = create_user("user2", "user2password")
    with db.session.begin():
        db.session.add(user1)
        db.session.add(user2)

    assert models.User.findWithPassword("user1", "user1password") == user1
    assert models.User.findWithPassword("user1", "wrong-user1password") is None
    assert models.User.findWithPassword("user2", "user1password") is None
    assert models.User.findWithPassword("user2", "user2password") == user2
    assert models.User.findWithPassword("nouser", "userpassword") is None

    with db.session.begin():
        db.session.delete(user1)
        db.session.delete(user2)
