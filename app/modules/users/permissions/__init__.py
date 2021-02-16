import logging

from flask_sqlalchemy import BaseQuery
from permission import Permission

from . import rules


log = logging.getLogger(__name__)


class PasswordRequiredPermissionMixin(object):
    """
    Helper rule mixin that ensure that user password is correct if
    `password_required` is set to True.
    """

    def __init__(self, password_required=False, password=None, **kwargs):
        # NOTE: kwargs is required since it is a mixin
        """
        Args:
            password_required (bool) - in some cases you may need to ask
                users for a password to allow certain actions, enforce this
                requirement by setting this :bool:`True`.
            password (str) - pass a user-specified password here.
        """
        self._password_required = password_required
        self._password = password
        super(PasswordRequiredPermissionMixin, self).__init__(**kwargs)

    def rule(self):
        _rule = super(PasswordRequiredPermissionMixin, self).rule()
        if self._password_required:
            _rule &= rules.PasswordRequiredRule(self._password)
        return _rule


class WriteAccessPermission(Permission):
    """
    Require a regular user role to perform an action.
    """

    def rule(self):
        return (
            rules.InternalRoleRule() | rules.AdminRoleRule() | rules.WriteAccessRule()
        )


class RolePermission(Permission):
    """
    This class aims to help distinguish all role-type permissions.
    """

    def __init__(self, partial=False, **kwargs):
        """
        Args:
            partial (bool) - True values is mostly useful for Swagger
                documentation purposes.
        """
        self._partial = partial
        super(RolePermission, self).__init__(**kwargs)

    def rule(self):
        if self._partial:
            return rules.PartialPermissionDeniedRule()
        return rules.AllowAllRule()


class ActiveUserRolePermission(RolePermission):
    """
    At least Active user is required.
    """

    def rule(self):
        return rules.ActiveUserRoleRule()


class AdminRolePermission(PasswordRequiredPermissionMixin, RolePermission):
    """
    Admin role is required.
    """

    def __init__(self, obj=None, **kwargs):
        """
        Args:
            obj (object) - any object can be passed here, which will be asked
                via ``check_owner(current_user)`` method whether a current user
                has enough permissions to perform an action on the given
                object.
        """
        self._obj = obj
        super(AdminRolePermission, self).__init__(**kwargs)

    def rule(self):
        return rules.InternalRoleRule() | (
            rules.AdminRoleRule(obj=self._obj) & super(AdminRolePermission, self).rule()
        )


class InternalRolePermission(RolePermission):
    """
    Internal role is required.
    """

    def rule(self):
        return rules.InternalRoleRule()


class OwnerRolePermission(PasswordRequiredPermissionMixin, RolePermission):
    """
    Owner/Admin may execute this action.
    """

    def __init__(self, obj=None, **kwargs):
        """
        Args:
            obj (object) - any object can be passed here, which will be asked
                via ``check_owner(current_user)`` method whether a current user
                has enough permissions to perform an action on the given
                object.
        """
        self._obj = obj
        super(OwnerRolePermission, self).__init__(**kwargs)

    def rule(self):
        return rules.InternalRoleRule() | (
            (rules.AdminRoleRule(obj=self._obj) | rules.OwnerRoleRule(obj=self._obj))
            & super(OwnerRolePermission, self).rule()
        )
