# encoding: utf-8
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
from .models import db, ApiToken
from ..users import permissions
from ..users.models import User

log = logging.getLogger(__name__)
api = Namespace('api_tokens', description="API Token Management")


@api.route('/')
@api.login_required()
class ApiTokens(Resource):
    """
    Manipulations with API Tokens.
    """

    # @api.permission_required(permissions.AdminRolePermission())
    @api.response(schemas.BaseApiTokenSchema(many=True))
    @api.parameters(parameters.ListApiTokensParameters(), locations=('query',))
    def get(self, args):
        """
        List of API Tokens.

        Returns a list of API Tokens starting from ``offset`` limited by
        ``limit`` parameter.

        Only Admins can specify ``owner`` to see API Tokens for other users. Regular users will see their own API Tokens.
        """
        apiKeys = ApiToken.query
        if 'owner_id' in args:
            owner_id = args['owner_id']
            if current_user.is_admin:
                apiKeys = apiKeys.filter(ApiToken.owner_id == owner_id)
            else:
                if owner_id == current_user.id:
                    apiKeys = apiKeys.filter(ApiToken.owner == current_user)
                else:
                    http_exceptions.abort(HTTPStatus.FORBIDDEN, "You don't have the permission to access other users' API Tokens.")
        else:
            if not current_user.is_admin:
                apiKeys = apiKeys.filter(ApiToken.owner == current_user)
        return apiKeys.offset(args['offset']).limit(args['limit'])

    @api.parameters(parameters.CreateApiTokenParameters())
    @api.response(schemas.DetailedApiTokenSchema())
    @api.response(code=HTTPStatus.FORBIDDEN)
    @api.response(code=HTTPStatus.CONFLICT)
    def post(self, args):
        """
        Create a new API Token.

        API token can be used instead of username/password. Include the API token in the ``X-API-TOKEN`` header
        """
        if 'owner_id' in args:
            owner_id = args['owner_id']
            if current_user.is_admin:
                owner = User.query.get(owner_id)
            else:
                if owner_id == current_user.id:
                    owner = current_user
                else:
                    http_exceptions.abort(HTTPStatus.FORBIDDEN, "You don't have the permission to create API Tokens for other users.")
        else:
            if not current_user.is_admin:
                owner = current_user
        with api.commit_or_abort(db.session, default_error_message="Failed to create a new API Token."):
            # todo: make token length a changable setting from the web interface
            newApiToken = ApiToken(owner=owner, token=security.gen_salt(32), **args)
            db.session.add(newApiToken)
        return newApiToken

@api.route('/<int:api_token_id>')
@api.login_required()
@api.response(code=HTTPStatus.NOT_FOUND, description="API Token not found.")
@api.resolveObjectToModel(ApiToken, 'api_token')
class ApiTokenByID(Resource):
    """
    Manipulations with a specific API TOken.
    """

    @api.login_required()
    @api.permission_required(permissions.OwnerRolePermission, kwargs_on_request=lambda kwargs: {'obj': kwargs['api_token']})
    @api.response(schemas.DetailedApiTokenSchema())
    def get(self, api_token):
        """
        Get API Token details by ID.
        """
        return api_token

    @api.login_required()
    @api.permission_required(permissions.OwnerRolePermission, kwargs_on_request=lambda kwargs: {'obj': kwargs['api_token']})
    @api.permission_required(permissions.WriteAccessPermission())
    @api.response(code=HTTPStatus.CONFLICT)
    @api.response(code=HTTPStatus.NO_CONTENT)
    def delete(self, api_token):
        """
        Delete a API Token by ID.
        """
        figure out internal server error on delete
        - MOVE TO CREDENTIAL MANAGER REPO
        with api.commit_or_abort(db.session, default_error_message="Failed to delete API Token."):
            db.session.delete(api_token)
        return None

    @api.login_required()
    @api.permission_required(permissions.OwnerRolePermission, kwargs_on_request=lambda kwargs: {'obj': kwargs['api_token']})
    @api.parameters(parameters.PatchApiTokenDetailsParameters())
    @api.response(schemas.DetailedApiTokenSchema())
    @api.response(code=HTTPStatus.CONFLICT)
    def patch(self, args, api_token):
        """
        Patch api_token details by ID.
        """
        with api.commit_or_abort(db.session, default_error_message="Failed to update API Token details."):
            parameters.PatchApiTokenDetailsParameters.perform_patch(args, api_token)
            db.session.merge(api_token)
        return api_token
