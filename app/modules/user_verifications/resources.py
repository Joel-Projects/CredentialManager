# pylint: disable=too-few-public-methods,invalid-name,bad-continuation
"""
RESTful API Auth resources
--------------------------
"""

import logging

from flask_login import current_user
from flask_restplus_patched import Resource
from flask_restplus._http import HTTPStatus
from werkzeug import security

from app.extensions.api import Namespace, http_exceptions

from . import schemas, parameters
from .models import db, UserVerification
from ..users import permissions
from ..users.models import User

log = logging.getLogger(__name__)
api = Namespace('user_verifications', description="User Verification Management")


@api.route('/')
@api.login_required()
class UserVerifications(Resource):
    """
    Manipulations with User Verifications.
    """

    # @api.permission_required(permissions.AdminRolePermission())
    @api.response(schemas.BaseUserVerificationSchema(many=True))
    @api.parameters(parameters.ListUserVerificationsParameters(), locations=('query',))
    def get(self, args):
        """
        List of User Verifications.

        Returns a list of User Verifications starting from ``offset`` limited by
        ``limit`` parameter.

        Only Admins can specify ``owner`` to see User Verifications for other users. Regular users will see their own User Verifications.
        """
        userVerifications = UserVerification.query
        if 'owner_id' in args:
            owner_id = args['owner_id']
            if current_user.is_admin or current_user.is_internal:
                userVerifications = userVerifications.filter(UserVerification.owner_id == owner_id)
            else:
                if owner_id == current_user.id:
                    userVerifications = userVerifications.filter(UserVerification.owner == current_user)
                else:
                    http_exceptions.abort(HTTPStatus.FORBIDDEN, "You don't have the permission to access other users' User Verifications.")
        else:
            if not current_user.is_admin:
                userVerifications = userVerifications.filter(UserVerification.owner == current_user)
        return userVerifications.offset(args['offset']).limit(args['limit'])

    @api.parameters(parameters.CreateUserVerificationParameters())
    @api.response(schemas.DetailedUserVerificationSchema())
    @api.response(code=HTTPStatus.FORBIDDEN)
    @api.response(code=HTTPStatus.CONFLICT)
    def post(self, args):
        """
        Create a new User Verification.

        User Verifications for verifying a redditor with a Discord member ID
        """
        if getattr(args, 'owner_id', None):
            owner_id = args.owner_id
            if current_user.is_admin or current_user.is_internal:
                owner = User.query.get(owner_id)
            else:
                if owner_id == current_user.id:
                    owner = current_user
                else:
                    http_exceptions.abort(HTTPStatus.FORBIDDEN, "You don't have the permission to create User Verifications for other users.")
        else:
            owner = current_user
        with api.commit_or_abort(db.session, default_error_message="Failed to create a new User Verification."):
            newUserVerification = UserVerification(owner=owner, dsn=args.dsn, name=args.name)
            db.session.add(newUserVerification)
        return newUserVerification

@api.route('/<int:user_verification_id>')
@api.login_required()
@api.response(code=HTTPStatus.NOT_FOUND, description="User Verification not found.")
@api.resolveObjectToModel(UserVerification, 'user_verification')
class UserVerificationByID(Resource):
    """
    Manipulations with a specific User Verification.
    """

    @api.login_required()
    @api.permission_required(permissions.OwnerRolePermission, kwargs_on_request=lambda kwargs: {'obj': kwargs['user_verification']})
    @api.response(schemas.DetailedUserVerificationSchema())
    def get(self, user_verification):
        """
        Get User Verification details by ID.
        """
        return user_verification

    @api.login_required()
    @api.permission_required(permissions.OwnerRolePermission, kwargs_on_request=lambda kwargs: {'obj': kwargs['user_verification']})
    @api.permission_required(permissions.WriteAccessPermission())
    @api.response(code=HTTPStatus.CONFLICT)
    @api.response(code=HTTPStatus.NO_CONTENT)
    def delete(self, user_verification):
        """
        Delete a User Verification by ID.
        """
        with api.commit_or_abort(db.session, default_error_message="Failed to delete User Verification."):
            db.session.delete(user_verification)
        return None

    @api.login_required()
    @api.permission_required(permissions.OwnerRolePermission, kwargs_on_request=lambda kwargs: {'obj': kwargs['user_verification']})
    @api.parameters(parameters.PatchUserVerificationDetailsParameters())
    @api.response(schemas.DetailedUserVerificationSchema())
    @api.response(code=HTTPStatus.CONFLICT)
    def patch(self, args, user_verification):
        """
        Patch user_verification details by ID.
        """
        with api.commit_or_abort(db.session, default_error_message="Failed to update User Verification details."):
            parameters.PatchUserVerificationDetailsParameters.perform_patch(args, user_verification)
            db.session.merge(user_verification)
        return user_verification