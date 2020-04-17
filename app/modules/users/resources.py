import logging

from flask_login import current_user
from flask_restplus._http import HTTPStatus

from app.extensions.api import Namespace, http_exceptions
from flask_restplus_patched import Resource
from . import parameters, permissions, schemas
from .models import User, db


log = logging.getLogger(__name__)
api = Namespace('users', description='User Management')

@api.route('/')
@api.login_required()
class Users(Resource):
    '''
    Manipulations with users.
    '''

    @api.permission_required(permissions.AdminRolePermission())
    @api.response(schemas.BaseUserSchema(many=True))
    @api.response(code=HTTPStatus.FORBIDDEN)
    @api.paginate()
    def get(self, args):
        '''
        List of users.

        Returns a list of users starting from ``offset`` limited by ``limit``
        parameter.
        '''
        query = User.query
        return query.offset(args['offset']).limit(args['limit'])

    @api.permission_required(permissions.AdminRolePermission())
    @api.parameters(parameters.CreateUserParameters())
    @api.response(schemas.DetailedUserSchema())
    @api.response(code=HTTPStatus.FORBIDDEN)
    @api.response(code=HTTPStatus.CONFLICT)
    def post(self, args):
        '''
        Create a new user.
        '''
        args.created_by = current_user.id
        args.updated_by = current_user.id
        fields = [
            'username',
            'password',
            'default_settings',
            'reddit_username'
        ]
        perms = [
            'is_admin',
            'is_active',
            'is_regular_user',
            'is_internal',
        ]
        user = User(**{k: v for k, v in args.items() if k in fields})
        for perm in perms:
            if perm in args:
                setattr(user, perm, args[perm])
        with api.commit_or_abort(db.session, default_error_message='Failed to create a new user.'):
            db.session.add(user)
        return user

@api.route('/<int:user_id>')
@api.login_required()
@api.response(code=HTTPStatus.NOT_FOUND, description='User not found.')
@api.resolveObjectToModel(User, 'user')
class UserByID(Resource):
    '''
    Manipulations with a specific user.
    '''

    @api.permission_required(permissions.OwnerRolePermission, kwargs_on_request=lambda kwargs: {'obj': kwargs['user']})
    @api.response(schemas.DetailedUserSchema())
    def get(self, user):
        '''
        Get user details by ID.
        '''
        return user # pragma: no cover

    @api.permission_required(permissions.OwnerRolePermission, kwargs_on_request=lambda kwargs: {'obj': kwargs['user']})
    @api.permission_required(permissions.WriteAccessPermission())
    @api.parameters(parameters.PatchUserDetailsParameters())
    @api.response(schemas.DetailedUserSchema())
    @api.response(code=HTTPStatus.CONFLICT)
    def patch(self, args, user):
        '''
        Patch user details by ID.
        '''

        with api.commit_or_abort(db.session, default_error_message='Failed to update user details.'):
            parameters.PatchUserDetailsParameters.perform_patch(args, user)
            user.updated_by = current_user.id
            db.session.merge(user)
        return user

    @api.permission_required(permissions.AdminRolePermission, kwargs_on_request=lambda kwargs: {'obj': kwargs['user']})
    @api.permission_required(permissions.WriteAccessPermission())
    @api.response(code=HTTPStatus.CONFLICT)
    @api.response(code=HTTPStatus.NO_CONTENT)
    def delete(self, user):
        '''
        Delete a user by ID.
        '''
        with api.commit_or_abort(db.session, default_error_message='Failed to delete user.'):
            if user == current_user:
                http_exceptions.abort(code=HTTPStatus.CONFLICT, message="You can't delete yourself.")
            db.session.delete(user)
        return None

@api.route('/<int:user_id>/apps')
@api.login_required()
@api.response(code=HTTPStatus.NOT_FOUND, description='User not found.')
@api.resolveObjectToModel(User, 'user')
class AppsByUserID(Resource):
    '''
    Returns all apps owned by a specific user.
    '''

    @api.permission_required(permissions.OwnerRolePermission, kwargs_on_request=lambda kwargs: {'obj': kwargs['user']})
    @api.response(schemas.UserItemsSchema())
    def get(self, user):
        '''
        Get items that is owned by user.
        '''
        return user

@api.route('/me')
@api.login_required()
class UserMe(Resource):
    '''
    Useful reference to the authenticated user itself.
    '''

    @api.response(schemas.DetailedUserSchema())
    def get(self):
        '''
        Get current user details.
        '''
        return User.query.get_or_404(current_user.id)

@api.route('/by_name')
@api.login_required()
@api.response(code=HTTPStatus.NOT_FOUND, description='User not found.')
class GetUserByName(Resource):
    '''
    Get User by name
    '''

    @api.permission_required(permissions.AdminRolePermission())
    @api.parameters(parameters.GetUserByName())
    @api.response(schemas.DetailedUserSchema())
    def post(self, args):
        '''
        Get User by username.
        '''
        user = User.query.filter_by(username=args['username']).first_or_404(f'User {args["username"]!r} does not exist.')
        if user.is_internal:
            permissions.InternalRolePermission().__enter__()
        return user