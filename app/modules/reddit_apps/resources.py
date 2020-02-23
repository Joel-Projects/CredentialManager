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
from .models import db, RedditApp
from ..users import permissions
from ..users.models import User

log = logging.getLogger(__name__)
api = Namespace('reddit_apps', description="Reddit App Management")


@api.route('/')
@api.login_required()
class RedditApps(Resource):
    """
    Manipulations with Reddit Apps.
    """

    # @api.permission_required(permissions.AdminRolePermission())
    @api.response(schemas.BaseRedditAppSchema(many=True))
    @api.parameters(parameters.ListRedditAppsParameters(), locations=('query',))
    def get(self, args):
        """
        List of Reddit Apps.

        Returns a list of Reddit Apps starting from ``offset`` limited by
        ``limit`` parameter.

        Only Admins can specify ``owner`` to see Reddit Apps for other users. Regular users will see their own Reddit Apps.
        """
        redditApps = RedditApp.query
        if 'owner_id' in args:
            owner_id = args['owner_id']
            if current_user.is_admin:
                redditApps = redditApps.filter(RedditApp.owner_id == owner_id)
            else:
                if owner_id == current_user.id:
                    redditApps = redditApps.filter(RedditApp.owner == current_user)
                else:
                    http_exceptions.abort(HTTPStatus.FORBIDDEN, "You don't have the permission to access other users' Reddit Apps.")
        else:
            if not current_user.is_admin:
                redditApps = redditApps.filter(RedditApp.owner == current_user)
        return redditApps.offset(args['offset']).limit(args['limit'])

    @api.parameters(parameters.CreateRedditAppParameters())
    @api.response(schemas.DetailedRedditAppSchema())
    @api.response(code=HTTPStatus.FORBIDDEN)
    @api.response(code=HTTPStatus.CONFLICT)
    def post(self, args):
        """
        Create a new Reddit App.

        Reddit Apps are used for interacting with reddit
        """
        if getattr(args, 'owner_id', None):
            owner_id = args.owner_id
            if current_user.is_admin:
                owner = User.query.get(owner_id)
            else:
                if owner_id == current_user.id:
                    owner = current_user
                else:
                    http_exceptions.abort(HTTPStatus.FORBIDDEN, "You don't have the permission to create Reddit Apps for other users.")
        else:
            owner = current_user
        with api.commit_or_abort(db.session, default_error_message="Failed to create a new Reddit App."):
            data = {
                'app_name', args.app_name,
                'short_name', args.short_name,
                'app_description', args.app_description,
                'client_id', args.client_id,
                'client_secret', args.client_secret,
                'user_agent', args.user_agent,
                'app_type', args.app_type,
                'redirect_uri', args.redirect_uri,
                'enabled', args.enabled
            }
            newRedditApp = RedditApp(owner=owner, **data)
            db.session.add(newRedditApp)
        return newRedditApp

@api.route('/<int:reddit_app_id>')
@api.login_required()
@api.response(code=HTTPStatus.NOT_FOUND, description="Reddit App not found.")
@api.resolveObjectToModel(RedditApp, 'reddit_app')
class RedditAppByID(Resource):
    """
    Manipulations with a specific Reddit App.
    """

    @api.login_required()
    @api.permission_required(permissions.OwnerRolePermission, kwargs_on_request=lambda kwargs: {'obj': kwargs['reddit_app']})
    @api.response(schemas.DetailedRedditAppSchema())
    def get(self, reddit_app):
        """
        Get Reddit App details by ID.
        """
        return reddit_app

    @api.login_required()
    @api.permission_required(permissions.OwnerRolePermission, kwargs_on_request=lambda kwargs: {'obj': kwargs['reddit_app']})
    @api.permission_required(permissions.WriteAccessPermission())
    @api.response(code=HTTPStatus.CONFLICT)
    @api.response(code=HTTPStatus.NO_CONTENT)
    def delete(self, reddit_app):
        """
        Delete a Reddit App by ID.
        """
        with api.commit_or_abort(db.session, default_error_message="Failed to delete Reddit App."):
            db.session.delete(reddit_app)
        return None

    @api.login_required()
    @api.permission_required(permissions.OwnerRolePermission, kwargs_on_request=lambda kwargs: {'obj': kwargs['reddit_app']})
    @api.parameters(parameters.PatchRedditAppDetailsParameters())
    @api.response(schemas.DetailedRedditAppSchema())
    @api.response(code=HTTPStatus.CONFLICT)
    def patch(self, args, reddit_app):
        """
        Patch reddit_app details by ID.
        """
        with api.commit_or_abort(db.session, default_error_message="Failed to update Reddit App details."):
            parameters.PatchRedditAppDetailsParameters.perform_patch(args, reddit_app)
            db.session.merge(reddit_app)
        return reddit_app

@api.route('/<int:reddit_app_id>/generate_auth')
@api.login_required()
@api.response(code=HTTPStatus.NOT_FOUND, description="Reddit App not found.")
@api.resolveObjectToModel(RedditApp, 'reddit_app')
class GenerateAuthUrl(Resource):
    """
    Generate a reddit auth url
    """

    @api.permission_required(permissions.OwnerRolePermission, kwargs_on_request=lambda kwargs: {'obj': kwargs['reddit_app']})
    @api.parameters(parameters.GenerateAuthUrlParameters())
    @api.response(schemas.AuthUrlSchema())
    def post(self, args, reddit_app):
        """
        Generate a reddit auth url


        """
        auth_url = reddit_app.genAuthUrl(args['scopes'], args['duration'])
        setattr(reddit_app, 'auth_url', auth_url)
        return reddit_app