# pylint: disable=too-few-public-methods
"""
RESTful API User resources
--------------------------
"""

import logging

from flask_login import current_user
from flask_restplus_patched import Resource
from flask_restplus._http import HTTPStatus

from app.extensions.api import Namespace, http_exceptions

from . import permissions, schemas, parameters
from .models import db, User


log = logging.getLogger(__name__)
api = Namespace('users', description="User Management")


@api.route('/')
class Users(Resource):
    """
    Manipulations with users.
    """

    @api.permission_required(permissions.AdminRolePermission())
    @api.response(schemas.BaseUserSchema(many=True))
    @api.response(code=HTTPStatus.FORBIDDEN)
    @api.paginate()
    def get(self, args):
        """
        List of users.

        Returns a list of users starting from ``offset`` limited by ``limit``
        parameter.
        """
        query = User.query
        return query.offset(args['offset']).limit(args['limit'])

    @api.permission_required(permissions.AdminRolePermission())
    @api.parameters(parameters.CreateUserParameters())
    @api.response(schemas.DetailedUserSchema())
    @api.response(code=HTTPStatus.FORBIDDEN)
    @api.response(code=HTTPStatus.CONFLICT)
    @api.doc(id='create_user')
    def post(self, data):
        """
        Create a new user.
        """
        with api.commit_or_abort(db.session, default_error_message="Failed to create a new user."):
            new_user = User(created_by=current_user.id, updated_by=current_user.id, **data)
            db.session.add(new_user)
        return new_user


@api.route('/<int:user_id>')
@api.login_required()
@api.response(code=HTTPStatus.NOT_FOUND, description="User not found.")
@api.resolveObjectToModel(User, 'user')
class UserByID(Resource):
    """
    Manipulations with a specific user.
    """

    # @api.login_required()
    # def options(self, *args, **kwargs):
    #     return super(UserByID, self).options(*args, **kwargs)

    @api.permission_required(permissions.OwnerRolePermission, kwargs_on_request=lambda kwargs: {'obj': kwargs['user']})
    @api.response(schemas.DetailedUserSchema())
    def get(self, user):
        """
        Get user details by ID.
        """
        return user

    @api.permission_required(permissions.OwnerRolePermission, kwargs_on_request=lambda kwargs: {'obj': kwargs['user']})
    @api.permission_required(permissions.WriteAccessPermission())
    @api.parameters(parameters.PatchUserDetailsParameters())
    @api.response(schemas.DetailedUserSchema())
    @api.response(code=HTTPStatus.CONFLICT)
    def patch(self, args, user):
        """
        Patch user details by ID.
        """

        with api.commit_or_abort(db.session, default_error_message="Failed to update user details."):
            parameters.PatchUserDetailsParameters.perform_patch(args, user)
            user.updated_by = current_user.id
            db.session.merge(user)
        return user

    @api.permission_required(permissions.AdminRolePermission, kwargs_on_request=lambda kwargs: {'obj': kwargs['user']})
    @api.permission_required(permissions.WriteAccessPermission())
    @api.response(code=HTTPStatus.CONFLICT)
    @api.response(code=HTTPStatus.NO_CONTENT)
    def delete(self, user):
        """
        Delete a user by ID.
        """
        with api.commit_or_abort(db.session, default_error_message="Failed to delete user."):
            if user == current_user:
                http_exceptions.abort(code=HTTPStatus.CONFLICT, message="You can't delete yourself.")
            db.session.delete(user)
        return None

@api.route('/<int:user_id>/apps')
@api.login_required()
@api.response(code=HTTPStatus.NOT_FOUND, description="User not found.")
@api.resolveObjectToModel(User, 'user')
class AppsByUserID(Resource):
    """
    Returns all apps owned by a specific user.
    """

    @api.permission_required(permissions.OwnerRolePermission, kwargs_on_request=lambda kwargs: {'obj': kwargs['user']})
    @api.response(schemas.UserItemsSchema())
    def get(self, user):
        """
        Get items that is owned by user.
        """
        print()
        return user

@api.route('/me')
@api.login_required()
class UserMe(Resource):
    """
    Useful reference to the authenticated user itself.
    """

    @api.response(schemas.DetailedUserSchema())
    def get(self):
        """
        Get current user details.
        """
        return User.query.get_or_404(current_user.id)
