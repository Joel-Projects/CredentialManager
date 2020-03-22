import logging

from flask_login import current_user
from flask_restplus._http import HTTPStatus

from app.extensions.api import Namespace, http_exceptions
from flask_restplus_patched import Resource
from . import parameters, schemas
from .models import SentryToken, db
from ..users import permissions
from ..users.models import User


log = logging.getLogger(__name__)
api = Namespace('sentry_tokens', description='Sentry Token Management')

@api.route('/')
@api.login_required()
class SentryTokens(Resource):
    '''
    Manipulations with Sentry Tokens.
    '''

    # @api.permission_required(permissions.AdminRolePermission())
    @api.response(schemas.BaseSentryTokenSchema(many=True))
    @api.parameters(parameters.ListSentryTokensParameters(), locations=('query',))
    def get(self, args):
        '''
        List of Sentry Tokens.

        Returns a list of Sentry Tokens starting from ``offset`` limited by
        ``limit`` parameter.

        Only Admins can specify ``owner`` to see Sentry Tokens for other users. Regular users will see their own Sentry Tokens.
        '''
        sentryTokens = SentryToken.query
        if 'owner_id' in args: # pragma: no cover
            owner_id = args['owner_id']
            if current_user.is_admin or current_user.is_internal:
                sentryTokens = sentryTokens.filter(SentryToken.owner_id == owner_id)
            else:
                if owner_id == current_user.id:
                    sentryTokens = sentryTokens.filter(SentryToken.owner == current_user)
                else:
                    http_exceptions.abort(HTTPStatus.FORBIDDEN, "You don't have the permission to access other users' Sentry Tokens.")
        else:
            if not current_user.is_admin:
                sentryTokens = sentryTokens.filter(SentryToken.owner == current_user)
        return sentryTokens.offset(args['offset']).limit(args['limit'])

    @api.parameters(parameters.CreateSentryTokenParameters())
    @api.response(schemas.DetailedSentryTokenSchema())
    @api.response(code=HTTPStatus.FORBIDDEN)
    @api.response(code=HTTPStatus.CONFLICT)
    def post(self, args):
        '''
        Create a new Sentry Token.

        Sentry Tokens are used for logging and error reporting in applications
        '''
        if getattr(args, 'owner_id', None):
            owner_id = args.owner_id
            if current_user.is_admin or current_user.is_internal:
                owner = User.query.get(owner_id)
            else:
                if owner_id == current_user.id:
                    owner = current_user
                else: # pragma: no cover
                    http_exceptions.abort(HTTPStatus.FORBIDDEN, "You don't have the permission to create Sentry Tokens for other users.")
        else:
            owner = current_user
        with api.commit_or_abort(db.session, default_error_message='Failed to create a new Sentry Token.'):
            newSentryToken = SentryToken(owner=owner, dsn=args.dsn, app_name=args.app_name)
            db.session.add(newSentryToken)
        return newSentryToken

@api.route('/<int:sentry_token_id>')
@api.login_required()
@api.response(code=HTTPStatus.NOT_FOUND, description='Sentry Token not found.')
@api.resolveObjectToModel(SentryToken, 'sentry_token')
class SentryTokenByID(Resource):
    '''
    Manipulations with a specific Sentry Token.
    '''

    @api.login_required()
    @api.permission_required(permissions.OwnerRolePermission, kwargs_on_request=lambda kwargs: {'obj': kwargs['sentry_token']})
    @api.response(schemas.DetailedSentryTokenSchema())
    def get(self, sentry_token):
        '''
        Get Sentry Token details by ID.
        '''
        return sentry_token

    @api.login_required()
    @api.permission_required(permissions.OwnerRolePermission, kwargs_on_request=lambda kwargs: {'obj': kwargs['sentry_token']})
    @api.permission_required(permissions.WriteAccessPermission())
    @api.response(code=HTTPStatus.CONFLICT)
    @api.response(code=HTTPStatus.NO_CONTENT)
    def delete(self, sentry_token):
        '''
        Delete a Sentry Token by ID.
        '''
        with api.commit_or_abort(db.session, default_error_message='Failed to delete Sentry Token.'):
            db.session.delete(sentry_token)
        return None

    @api.login_required()
    @api.permission_required(permissions.OwnerRolePermission, kwargs_on_request=lambda kwargs: {'obj': kwargs['sentry_token']})
    @api.parameters(parameters.PatchSentryTokenDetailsParameters())
    @api.response(schemas.DetailedSentryTokenSchema())
    @api.response(code=HTTPStatus.CONFLICT)
    def patch(self, args, sentry_token):
        '''
        Patch sentry_token details by ID.
        '''
        with api.commit_or_abort(db.session, default_error_message='Failed to update Sentry Token details.'):
            parameters.PatchSentryTokenDetailsParameters.perform_patch(args, sentry_token)
            db.session.merge(sentry_token)
        return sentry_token