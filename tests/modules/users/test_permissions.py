from mock import Mock
import pytest

from werkzeug.exceptions import HTTPException

from app.modules.users import permissions


def test_DenyAbortMixin():
    with pytest.raises(HTTPException):
        permissions.rules.DenyAbortMixin().deny()

def test_WriteAccessRule_authenticated_user(authenticated_user_instance):
    authenticated_user_instance.is_regular_user = True
    assert permissions.rules.WriteAccessRule().check() is True
    authenticated_user_instance.is_regular_user = False
    assert permissions.rules.WriteAccessRule().check() is False

def test_ActiveUserRoleRule_anonymous(anonymous_user_instance):
  
    assert permissions.rules.ActiveUserRoleRule().check() is False

def test_ActiveUserRoleRule_authenticated_user(authenticated_user_instance):
    authenticated_user_instance.is_active = True
    assert permissions.rules.ActiveUserRoleRule().check() is True
    authenticated_user_instance.is_active = False
    assert permissions.rules.ActiveUserRoleRule().check() is False

def test_PasswordRequiredRule(authenticated_user_instance):
    authenticated_user_instance.password = "correct_password"
    assert permissions.rules.PasswordRequiredRule(password="correct_password").check() is True
    assert permissions.rules.PasswordRequiredRule(password="wrong_password").check() is False

def test_AdminRoleRule_authenticated_user(authenticated_user_instance):
    authenticated_user_instance.is_admin = True
    assert permissions.rules.AdminRoleRule().check() is True
    authenticated_user_instance.is_admin = False
    assert permissions.rules.AdminRoleRule().check() is False

def test_OwnerRoleRule_authenticated_user(authenticated_user_instance):
    obj = Mock()
    del obj.check_owner
    obj.owner.is_internal = False
    assert permissions.rules.OwnerRoleRule(obj).check() is False
    obj.check_owner = lambda user: user == authenticated_user_instance
    assert permissions.rules.OwnerRoleRule(obj).check() is True
    obj.owner.is_internal = True
    assert permissions.rules.OwnerRoleRule(obj).check() is False
    obj.check_owner = lambda user: False
    assert permissions.rules.OwnerRoleRule(obj).check() is False

def test_PartialPermissionDeniedRule():
    with pytest.raises(RuntimeError):
        permissions.rules.PartialPermissionDeniedRule().check()

def test_PasswordRequiredPermissionMixin():
    mixin = permissions.PasswordRequiredPermissionMixin(password_required=False)
    with pytest.raises(AttributeError):
        mixin.rule()

def test_WriteAccessPermission_authenticated_user(authenticated_user_instance):
    authenticated_user_instance.is_regular_user = True
    with permissions.WriteAccessPermission():
        pass
    authenticated_user_instance.is_regular_user = False
    with pytest.raises(HTTPException):
        with permissions.WriteAccessPermission():
            pass

def test_RolePermission():
    with permissions.RolePermission():
        pass
    with pytest.raises(RuntimeError):
        with permissions.RolePermission(partial=True):
            pass

def test_ActiveUserRolePermission_anonymous_user(anonymous_user_instance):
  
    with pytest.raises(HTTPException):
        with permissions.ActiveUserRolePermission():
            pass

def test_ActiveUserRolePermission_authenticated_user(authenticated_user_instance):
    authenticated_user_instance.is_active = True
    with permissions.ActiveUserRolePermission():
        pass
    authenticated_user_instance.is_active = False
    with pytest.raises(HTTPException):
        with permissions.ActiveUserRolePermission():
            pass

def test_AdminRolePermission_anonymous_user(anonymous_user_instance):
  
    with pytest.raises(HTTPException):
        with permissions.AdminRolePermission():
            pass

def test_AdminRolePermission_authenticated_user(authenticated_user_instance):
    authenticated_user_instance.is_admin = True
    with permissions.AdminRolePermission():
        pass
    authenticated_user_instance.is_admin = False
    with pytest.raises(HTTPException):
        with permissions.AdminRolePermission():
            pass

def test_AdminRolePermission_anonymous_user_with_password(anonymous_user_instance):
  
    with pytest.raises(HTTPException):
        with permissions.AdminRolePermission(password_required=True, password="any_password"):
            pass

def test_AdminRolePermission_authenticated_user_with_password_is_admin(authenticated_user_instance):
    authenticated_user_instance.password = "correct_password"
    authenticated_user_instance.is_admin = True
    with permissions.AdminRolePermission(password_required=True, password="correct_password"):
        pass
    with pytest.raises(HTTPException):
        with permissions.AdminRolePermission(password_required=True, password="wrong_password"):
            pass

def test_AdminRolePermission_authenticated_user_with_password_not_admin(authenticated_user_instance):
    authenticated_user_instance.password = "correct_password"
    authenticated_user_instance.is_admin = False
    with pytest.raises(HTTPException):
        with permissions.AdminRolePermission(password_required=True, password="correct_password"):
            pass
    with pytest.raises(HTTPException):
        with permissions.AdminRolePermission(password_required=True, password="wrong_password"):
            pass

def test_OwnerRolePermission_anonymous_user(anonymous_user_instance):
  
    with pytest.raises(HTTPException):
        with permissions.OwnerRolePermission():
            pass

def test_OwnerRolePermission_authenticated_user(authenticated_user_instance):
    obj = Mock()
    obj.owner.is_internal = False
    obj.check_owner = lambda user: user == authenticated_user_instance
    with permissions.OwnerRolePermission(obj=obj):
        pass
    del obj.check_owner
    with pytest.raises(HTTPException):
        with permissions.OwnerRolePermission():
            pass

def test_OwnerRolePermission_anonymous_user_with_password(anonymous_user_instance):
  
    obj = Mock()
    obj.owner.is_internal = False
    obj.check_owner = lambda user: False
    with pytest.raises(HTTPException):
        with permissions.OwnerRolePermission(
            obj=obj,
            password_required=True,
            password="any_password"
        ):
            pass

def test_OwnerRolePermission_authenticated_user_with_password_with_check_owner(authenticated_user_instance):
    authenticated_user_instance.password = "correct_password"
    obj = Mock()
    obj.owner.is_internal = False
    obj.check_owner = lambda user: user == authenticated_user_instance
    with permissions.OwnerRolePermission(obj=obj, password_required=True, password="correct_password"):
        pass
    with pytest.raises(HTTPException):
        with permissions.OwnerRolePermission(obj=obj, password_required=True, password="wrong_password"):
            pass

def test_OwnerRolePermission_authenticated_user_with_password_without_check_owner(authenticated_user_instance):
    authenticated_user_instance.password = "correct_password"
    obj = Mock()
    del obj.check_owner
    with pytest.raises(HTTPException):
        with permissions.OwnerRolePermission(obj=obj, password_required=True, password="correct_password"):
            pass
    with pytest.raises(HTTPException):
        with permissions.OwnerRolePermission(obj=obj, password_required=True, password="wrong_password"):
            pass
