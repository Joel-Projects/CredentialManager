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
from .models import db, RefreshToken
from ..users import permissions
from ..users.models import User

log = logging.getLogger(__name__)
api = Namespace('refresh_tokens', description="Refresh Token Management")


@api.route('/')
@api.login_required()
class RefreshTokens(Resource):
    """
    Manipulations with Refresh Tokens.
    """

    # @api.permission_required(permissions.AdminRolePermission())
    @api.response(schemas.BaseRefreshTokenSchema(many=True))
    @api.parameters(parameters.ListRefreshTokensParameters(), locations=('query',))
    def get(self, args):
        """
        List of Refresh Tokens.

        Returns a list of Refresh Tokens starting from ``offset`` limited by
        ``limit`` parameter.

        Only Admins can specify ``owner`` to see Refresh Tokens for other users. Regular users will see their own Refresh Tokens.
        """
        refreshTokens = RefreshToken.query
        if 'owner_id' in args:
            owner_id = args['owner_id']
            if current_user.is_admin:
                refreshTokens = refreshTokens.filter(RefreshToken.owner_id == owner_id)
            else:
                if owner_id == current_user.id:
                    refreshTokens = refreshTokens.filter(RefreshToken.owner == current_user)
                else:
                    http_exceptions.abort(HTTPStatus.FORBIDDEN, "You don't have the permission to access other users' Refresh Tokens.")
        else:
            if not current_user.is_admin:
                refreshTokens = refreshTokens.filter(RefreshToken.owner == current_user)
        return refreshTokens.offset(args['offset']).limit(args['limit'])

    @api.parameters(parameters.CreateRefreshTokenParameters())
    @api.response(schemas.DetailedRefreshTokenSchema())
    @api.response(code=HTTPStatus.FORBIDDEN)
    @api.response(code=HTTPStatus.CONFLICT)
    def post(self, args):
        """
        Create a new Refresh Token.

        Refresh Tokens authencating as an user with Reddit's API
        """
        if getattr(args, 'owner_id', None):
            owner_id = args.owner_id
            if current_user.is_admin:
                owner = User.query.get(owner_id)
            else:
                if owner_id == current_user.id:
                    owner = current_user
                else:
                    http_exceptions.abort(HTTPStatus.FORBIDDEN, "You don't have the permission to create Refresh Tokens for other users.")
        else:
            owner = current_user
        with api.commit_or_abort(db.session, default_error_message="Failed to create a new Refresh Token."):
            newRefreshToken = RefreshToken(owner=owner, dsn=args.dsn, name=args.name)
            db.session.add(newRefreshToken)
        return newRefreshToken

@api.route('/<int:refresh_token_id>')
@api.login_required()
@api.response(code=HTTPStatus.NOT_FOUND, description="Refresh Token not found.")
@api.resolveObjectToModel(RefreshToken, 'refresh_token')
class RefreshTokenByID(Resource):
    """
    Manipulations with a specific Refresh Token.
    """

    @api.login_required()
    @api.permission_required(permissions.OwnerRolePermission, kwargs_on_request=lambda kwargs: {'obj': kwargs['refresh_token']})
    @api.response(schemas.DetailedRefreshTokenSchema())
    def get(self, refresh_token):
        """
        Get Refresh Token details by ID.
        """
        return refresh_token

    @api.login_required()
    @api.permission_required(permissions.OwnerRolePermission, kwargs_on_request=lambda kwargs: {'obj': kwargs['refresh_token']})
    @api.permission_required(permissions.WriteAccessPermission())
    @api.response(code=HTTPStatus.CONFLICT)
    @api.response(code=HTTPStatus.NO_CONTENT)
    def delete(self, refresh_token):
        """
        Delete a Refresh Token by ID.
        """
        with api.commit_or_abort(db.session, default_error_message="Failed to delete Refresh Token."):
            db.session.delete(refresh_token)
        return None

    @api.login_required()
    @api.permission_required(permissions.OwnerRolePermission, kwargs_on_request=lambda kwargs: {'obj': kwargs['refresh_token']})
    @api.parameters(parameters.PatchRefreshTokenDetailsParameters())
    @api.response(schemas.DetailedRefreshTokenSchema())
    @api.response(code=HTTPStatus.CONFLICT)
    def patch(self, args, refresh_token):
        """
        Patch refresh_token details by ID.
        """
        with api.commit_or_abort(db.session, default_error_message="Failed to update Refresh Token details."):
            parameters.PatchRefreshTokenDetailsParameters.perform_patch(args, refresh_token)
            db.session.merge(refresh_token)
        return refresh_token