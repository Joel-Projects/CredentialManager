import pytest
from mock import Mock
from werkzeug.exceptions import HTTPException

from app.modules.users import permissions


def test_deny_abort_mixin():
    with pytest.raises(HTTPException):
        permissions.rules.DenyAbortMixin().deny()


def test_write_access_rule_authenticated_user(regular_user_instance):
    regular_user_instance.is_regular_user = True
    assert permissions.rules.WriteAccessRule().check() is True
    regular_user_instance.is_regular_user = False
    assert permissions.rules.WriteAccessRule().check() is False


def test_active_user_role_rule_anonymous(anonymous_user_instance):
    assert permissions.rules.ActiveUserRoleRule().check() is False


def test_active_user_role_rule_authenticated_user(regular_user_instance):
    regular_user_instance.is_active = True
    assert permissions.rules.ActiveUserRoleRule().check() is True
    regular_user_instance.is_active = False
    assert permissions.rules.ActiveUserRoleRule().check() is False


def test_password_required_rule(regular_user_instance):
    regular_user_instance.password = "correct_password"
    assert (
        permissions.rules.PasswordRequiredRule(password="correct_password").check()
        is True
    )
    assert (
        permissions.rules.PasswordRequiredRule(password="wrong_password").check()
        is False
    )


def test_admin_role_rule_authenticated_user(regular_user_instance):
    regular_user_instance.is_admin = True
    assert permissions.rules.AdminRoleRule().check() is True
    regular_user_instance.is_admin = False
    assert permissions.rules.AdminRoleRule().check() is False


def test_owner_role_rule_authenticated_user(regular_user_instance):
    obj = Mock()
    del obj.check_owner
    obj.owner.is_internal = False
    assert permissions.rules.OwnerRoleRule(obj).check() is False
    obj.check_owner = lambda user: user == regular_user_instance
    assert permissions.rules.OwnerRoleRule(obj).check() is True
    obj.owner.is_internal = True
    assert permissions.rules.OwnerRoleRule(obj).check() is False
    obj.check_owner = lambda user: False
    assert permissions.rules.OwnerRoleRule(obj).check() is False


def test_partial_permission_denied_rule():
    with pytest.raises(RuntimeError):
        permissions.rules.PartialPermissionDeniedRule().check()


def test_password_required_permission_mixin():
    mixin = permissions.PasswordRequiredPermissionMixin(password_required=False)
    with pytest.raises(AttributeError):
        mixin.rule()


def test_write_access_permission_authenticated_user(regular_user_instance):
    regular_user_instance.is_regular_user = True
    permissions.WriteAccessPermission().__enter__()
    regular_user_instance.is_regular_user = False
    with pytest.raises(HTTPException):
        permissions.WriteAccessPermission().__enter__()


def test_role_permission():
    permissions.RolePermission().__enter__()
    with pytest.raises(RuntimeError):
        permissions.RolePermission(partial=True).__enter__()


def test_active_user_role_permission_anonymous_user(anonymous_user_instance):
    with pytest.raises(HTTPException):
        permissions.ActiveUserRolePermission().__enter__()


def test_active_user_role_permission_authenticated_user(regular_user_instance):
    regular_user_instance.is_active = True
    permissions.ActiveUserRolePermission().__enter__()
    regular_user_instance.is_active = False
    with pytest.raises(HTTPException):
        permissions.ActiveUserRolePermission().__enter__()


def test_admin_role_permission_anonymous_user(anonymous_user_instance):
    with pytest.raises(HTTPException):
        permissions.AdminRolePermission().__enter__()


def test_admin_role_permission_authenticated_user(regular_user_instance):
    regular_user_instance.is_admin = True
    permissions.AdminRolePermission().__enter__()
    regular_user_instance.is_admin = False
    with pytest.raises(HTTPException):
        permissions.AdminRolePermission().__enter__()


def test_admin_role_permission_anonymous_user_with_password(anonymous_user_instance):
    with pytest.raises(HTTPException):
        permissions.AdminRolePermission(
            password_required=True, password="any_password"
        ).__enter__()


def test_admin_role_permission_authenticated_user_with_password_is_admin(
    regular_user_instance,
):
    regular_user_instance.password = "correct_password"
    regular_user_instance.is_admin = True
    permissions.AdminRolePermission(
        password_required=True, password="correct_password"
    ).__enter__()
    with pytest.raises(HTTPException):
        permissions.AdminRolePermission(
            password_required=True, password="wrong_password"
        ).__enter__()


def test_admin_role_permission_authenticated_user_with_password_not_admin(
    regular_user_instance,
):
    regular_user_instance.password = "correct_password"
    regular_user_instance.is_admin = False
    with pytest.raises(HTTPException):
        permissions.AdminRolePermission(
            password_required=True, password="correct_password"
        ).__enter__()
    with pytest.raises(HTTPException):
        permissions.AdminRolePermission(
            password_required=True, password="wrong_password"
        ).__enter__()


def test_owner_role_permission_anonymous_user(anonymous_user_instance):
    with pytest.raises(HTTPException):
        permissions.OwnerRolePermission().__enter__()


def test_owner_role_permission_authenticated_user(regular_user_instance):
    obj = Mock()
    obj.owner.is_internal = False
    obj.check_owner = lambda user: user == regular_user_instance
    permissions.OwnerRolePermission(obj=obj).__enter__()
    del obj.check_owner
    with pytest.raises(HTTPException):
        permissions.OwnerRolePermission().__enter__()


def test_owner_role_permission_anonymous_user_with_password(anonymous_user_instance):
    obj = Mock()
    obj.owner.is_internal = False
    obj.check_owner = lambda user: False
    with pytest.raises(HTTPException):
        permissions.OwnerRolePermission(
            obj=obj, password_required=True, password="any_password"
        ).__enter__()


def test_owner_role_permission_authenticated_user_with_password_with_check_owner(
    regular_user_instance,
):
    regular_user_instance.password = "correct_password"
    obj = Mock()
    obj.owner.is_internal = False
    obj.check_owner = lambda user: user == regular_user_instance
    permissions.OwnerRolePermission(
        obj=obj, password_required=True, password="correct_password"
    ).__enter__()
    with pytest.raises(HTTPException):
        permissions.OwnerRolePermission(
            obj=obj, password_required=True, password="wrong_password"
        ).__enter__()


def test_owner_role_permission_authenticated_user_with_password_without_check_owner(
    regular_user_instance,
):
    regular_user_instance.password = "correct_password"
    obj = Mock()
    del obj.check_owner
    with pytest.raises(HTTPException):
        permissions.OwnerRolePermission(
            obj=obj, password_required=True, password="correct_password"
        ).__enter__()
    with pytest.raises(HTTPException):
        permissions.OwnerRolePermission(
            obj=obj, password_required=True, password="wrong_password"
        ).__enter__()  # pragma: no cover
