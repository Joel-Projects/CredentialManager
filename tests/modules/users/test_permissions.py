from mock import Mock
import pytest

from werkzeug.exceptions import HTTPException

from app.modules.users import permissions


def test_DenyAbortMixin():
    with pytest.raises(HTTPException):
        permissions.rules.DenyAbortMixin().deny()

def test_WriteAccessRule_authenticated_user(regularUserInstance):
    regularUserInstance.is_regular_user = True
    assert permissions.rules.WriteAccessRule().check() is True
    regularUserInstance.is_regular_user = False
    assert permissions.rules.WriteAccessRule().check() is False

def test_ActiveUserRoleRule_anonymous(anonymousUserInstance):
    assert permissions.rules.ActiveUserRoleRule().check() is False

def test_ActiveUserRoleRule_authenticated_user(regularUserInstance):
    regularUserInstance.is_active = True
    assert permissions.rules.ActiveUserRoleRule().check() is True
    regularUserInstance.is_active = False
    assert permissions.rules.ActiveUserRoleRule().check() is False

def test_PasswordRequiredRule(regularUserInstance):
    regularUserInstance.password = 'correct_password'
    assert permissions.rules.PasswordRequiredRule(password='correct_password').check() is True
    assert permissions.rules.PasswordRequiredRule(password='wrong_password').check() is False

def test_AdminRoleRule_authenticated_user(regularUserInstance):
    regularUserInstance.is_admin = True
    assert permissions.rules.AdminRoleRule().check() is True
    regularUserInstance.is_admin = False
    assert permissions.rules.AdminRoleRule().check() is False

def test_OwnerRoleRule_authenticated_user(regularUserInstance):
    obj = Mock()
    del obj.check_owner
    obj.owner.is_internal = False
    assert permissions.rules.OwnerRoleRule(obj).check() is False
    obj.check_owner = lambda user: user == regularUserInstance
    assert permissions.rules.OwnerRoleRule(obj).check() is True
    obj.owner.is_internal = True
    assert permissions.rules.OwnerRoleRule(obj).check() is False
    obj.check_owner = lambda user: False # pragma: no branch
    assert permissions.rules.OwnerRoleRule(obj).check() is False

def test_PartialPermissionDeniedRule():
    with pytest.raises(RuntimeError):
        permissions.rules.PartialPermissionDeniedRule().check()

def test_PasswordRequiredPermissionMixin():
    mixin = permissions.PasswordRequiredPermissionMixin(password_required=False)
    with pytest.raises(AttributeError):
        mixin.rule()

def test_WriteAccessPermission_authenticated_user(regularUserInstance):
    regularUserInstance.is_regular_user = True
    permissions.WriteAccessPermission().__enter__()
    regularUserInstance.is_regular_user = False
    with pytest.raises(HTTPException):
        permissions.WriteAccessPermission().__enter__()

def test_RolePermission():
    permissions.RolePermission().__enter__()
    with pytest.raises(RuntimeError):
        permissions.RolePermission(partial=True).__enter__()

def test_ActiveUserRolePermission_anonymous_user(anonymousUserInstance):
    with pytest.raises(HTTPException):
        permissions.ActiveUserRolePermission().__enter__()

def test_ActiveUserRolePermission_authenticated_user(regularUserInstance):
    regularUserInstance.is_active = True
    permissions.ActiveUserRolePermission().__enter__()
    regularUserInstance.is_active = False
    with pytest.raises(HTTPException):
        permissions.ActiveUserRolePermission().__enter__()

def test_AdminRolePermission_anonymous_user(anonymousUserInstance):
    with pytest.raises(HTTPException):
        permissions.AdminRolePermission().__enter__()

def test_AdminRolePermission_authenticated_user(regularUserInstance):
    regularUserInstance.is_admin = True
    permissions.AdminRolePermission().__enter__()
    regularUserInstance.is_admin = False
    with pytest.raises(HTTPException):
        permissions.AdminRolePermission().__enter__()

def test_AdminRolePermission_anonymous_user_with_password(anonymousUserInstance):
    with pytest.raises(HTTPException):
        permissions.AdminRolePermission(password_required=True, password='any_password').__enter__()

def test_AdminRolePermission_authenticated_user_with_password_is_admin(regularUserInstance):
    regularUserInstance.password = 'correct_password'
    regularUserInstance.is_admin = True
    permissions.AdminRolePermission(password_required=True, password='correct_password').__enter__()
    with pytest.raises(HTTPException):
        permissions.AdminRolePermission(password_required=True, password='wrong_password').__enter__()

def test_AdminRolePermission_authenticated_user_with_password_not_admin(regularUserInstance):
    regularUserInstance.password = 'correct_password'
    regularUserInstance.is_admin = False
    with pytest.raises(HTTPException):
        permissions.AdminRolePermission(password_required=True, password='correct_password').__enter__()
    with pytest.raises(HTTPException):
        permissions.AdminRolePermission(password_required=True, password='wrong_password').__enter__()

def test_OwnerRolePermission_anonymous_user(anonymousUserInstance):
    with pytest.raises(HTTPException):
        permissions.OwnerRolePermission().__enter__()

def test_OwnerRolePermission_authenticated_user(regularUserInstance):
    obj = Mock()
    obj.owner.is_internal = False
    obj.check_owner = lambda user: user == regularUserInstance
    permissions.OwnerRolePermission(obj=obj).__enter__()
    del obj.check_owner
    with pytest.raises(HTTPException):
        permissions.OwnerRolePermission().__enter__()

def test_OwnerRolePermission_anonymous_user_with_password(anonymousUserInstance):
    obj = Mock()
    obj.owner.is_internal = False
    obj.check_owner = lambda user: False # pragma: no branch
    with pytest.raises(HTTPException):
        permissions.OwnerRolePermission(obj=obj, password_required=True, password='any_password').__enter__()

def test_OwnerRolePermission_authenticated_user_with_password_with_check_owner(regularUserInstance):
    regularUserInstance.password = 'correct_password'
    obj = Mock()
    obj.owner.is_internal = False
    obj.check_owner = lambda user: user == regularUserInstance
    permissions.OwnerRolePermission(obj=obj, password_required=True, password='correct_password').__enter__()
    with pytest.raises(HTTPException):
        permissions.OwnerRolePermission(obj=obj, password_required=True, password='wrong_password').__enter__()

def test_OwnerRolePermission_authenticated_user_with_password_without_check_owner(regularUserInstance):
    regularUserInstance.password = 'correct_password'
    obj = Mock()
    del obj.check_owner
    with pytest.raises(HTTPException):
        permissions.OwnerRolePermission(obj=obj, password_required=True, password='correct_password').__enter__()
    with pytest.raises(HTTPException):
        permissions.OwnerRolePermission(obj=obj, password_required=True, password='wrong_password').__enter__() # pragma: no cover