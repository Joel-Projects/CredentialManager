import logging

from flask_login import current_user
from flask_restplus._http import HTTPStatus

from app.extensions.api import Namespace, http_exceptions
from flask_restplus_patched import Resource
from . import parameters, schemas
from .models import UserVerification, db
from ..reddit_apps.models import RedditApp
from .. import getViewableItems
from ..users import permissions
from ..users.models import User


log = logging.getLogger(__name__)
api = Namespace('user_verifications', description='User Verification Management')

@api.route('/')
@api.login_required()
class UserVerifications(Resource):
    '''
    Manipulations with User Verifications.
    '''

    # @api.permission_required(permissions.AdminRolePermission())
    @api.response(schemas.BaseUserVerificationSchema(many=True))
    @api.parameters(parameters.ListUserVerificationsParameters(), locations=('query',))
    def get(self, args):
        '''
        List of User Verifications.

        Returns a list of User Verifications starting from ``offset`` limited by
        ``limit`` parameter.

        Only Admins can specify ``owner`` to see User Verifications for other users. Regular users will see their own User Verifications.
        '''
        userVerifications = getViewableItems(args, UserVerification)
        return userVerifications.offset(args['offset']).limit(args['limit'])

    @api.parameters(parameters.CreateUserVerificationParameters())
    @api.response(schemas.DetailedUserVerificationSchema())
    @api.response(code=HTTPStatus.FORBIDDEN)
    @api.response(code=HTTPStatus.CONFLICT)
    def post(self, args):
        '''
        Create a new User Verification.

        User Verifications for verifying a redditor with a User ID
        '''
        args.owner = current_user
        if args.owner_id:
            args.owner = User.query.get(args.owner_id)
        with api.commit_or_abort(db.session, default_error_message="Failed to create a new User Verification."):
            db.session.add(args)
        return args

@api.route('/<int:user_verification_id>')
@api.login_required()
@api.response(code=HTTPStatus.NOT_FOUND, description='User Verification not found.')
@api.resolveObjectToModel(UserVerification, 'user_verification')
class UserVerificationByID(Resource):
    '''
    Manipulations with a specific User Verification.
    '''

    @api.login_required()
    @api.permission_required(permissions.OwnerRolePermission, kwargs_on_request=lambda kwargs: {'obj': kwargs['user_verification']})
    @api.response(schemas.DetailedUserVerificationSchema())
    def get(self, user_verification):
        '''
        Get User Verification details by ID.
        '''
        return user_verification

    @api.login_required()
    @api.permission_required(permissions.OwnerRolePermission, kwargs_on_request=lambda kwargs: {'obj': kwargs['user_verification']})
    @api.permission_required(permissions.WriteAccessPermission())
    @api.response(code=HTTPStatus.CONFLICT)
    @api.response(code=HTTPStatus.NO_CONTENT)
    def delete(self, user_verification):
        '''
        Delete a User Verification by ID.
        '''
        with api.commit_or_abort(db.session, default_error_message='Failed to delete User Verification.'):
            db.session.delete(user_verification)
        return None

    @api.login_required()
    @api.permission_required(permissions.OwnerRolePermission, kwargs_on_request=lambda kwargs: {'obj': kwargs['user_verification']})
    @api.parameters(parameters.PatchUserVerificationDetailsParameters())
    @api.response(schemas.DetailedUserVerificationSchema())
    @api.response(code=HTTPStatus.CONFLICT)
    def patch(self, args, user_verification):
        '''
        Patch user_verification details by ID.
        '''
        with api.commit_or_abort(db.session, default_error_message='Failed to update User Verification details.'):
            parameters.PatchUserVerificationDetailsParameters.perform_patch(args, user_verification)
            db.session.merge(user_verification)
        return user_verification

@api.route('/get_redditor')
@api.login_required()
@api.response(code=HTTPStatus.NOT_FOUND, description='Member not found.')
class GetUserVerificationByUserID(Resource):
    '''
    Get redditor from UserVerification
    '''

    @api.parameters(parameters.GetUserVerificationByUserId())
    @api.response(schemas.DetailedUserVerificationSchema())
    def post(self, args):
        '''
        Get  by User ID.
        Optionally filter by Reddit App ID

        Only Admins can see Refresh Tokens for other users' Reddit Apps. Regular users will see their own Reddit Apps' Refresh Tokens.
        '''
        if 'reddit_app_id' in args:
            redditApp = RedditApp.query.get_or_404(args['reddit_app_id'], 'Reddit App not found')
            return UserVerification.query.filter(UserVerification.user_id == args['user_id'], UserVerification.reddit_app == redditApp).first_or_404()
        else:
            return UserVerification.query.filter(UserVerification.user_id == args['user_id']).first_or_404()