import logging

from flask_login import current_user
from flask_restplus._http import HTTPStatus

from app.extensions.api import Namespace, abort
from flask_restplus_patched import Resource

from .. import get_viewable_items
from ..refresh_tokens.schemas import DetailedRefreshTokenSchema
from ..user_verifications.models import UserVerification
from ..users import permissions
from ..users.models import User
from . import parameters, schemas
from .models import RedditApp, db

log = logging.getLogger(__name__)
api = Namespace("reddit_apps", description="Reddit App Management")


@api.route("/")
@api.login_required()
class RedditApps(Resource):
    """
    Manipulations with Reddit Apps.
    """

    # @api.permission_required(permissions.AdminRolePermission())
    @api.response(schemas.BaseRedditAppSchema(many=True))
    @api.parameters(parameters.ListRedditAppsParameters(), locations=("query",))
    def get(self, args):
        """
        List of Reddit Apps.

        Returns a list of Reddit Apps starting from ``offset`` limited by
        ``limit`` parameter.

        Only Admins can specify ``owner`` to see Reddit Apps for other users. Regular users will see their own Reddit Apps.
        """
        reddit_apps = get_viewable_items(args, RedditApp)
        return reddit_apps.offset(args["offset"]).limit(args["limit"])

    @api.parameters(parameters.CreateRedditAppParameters())
    @api.response(schemas.DetailedRedditAppSchema())
    @api.response(code=HTTPStatus.FORBIDDEN)
    @api.response(code=HTTPStatus.CONFLICT)
    def post(self, args):
        """
        Create a new Reddit App.

        Reddit Apps are used for interacting with reddit
        """
        args.owner = current_user
        if args.owner_id:
            args.owner = User.query.get(args.owner_id)
        with api.commit_or_abort(db.session, default_error_message="Failed to create a new Reddit App."):
            db.session.add(args)
        return args


@api.route("/<int:reddit_app_id>")
@api.response(code=HTTPStatus.NOT_FOUND, description="Reddit App not found.")
@api.login_required()
@api.resolve_object_to_model(RedditApp, "reddit_app")
class RedditAppByID(Resource):
    """
    Manipulations with a specific Reddit App.
    """

    @api.login_required()
    @api.permission_required(
        permissions.OwnerRolePermission,
        kwargs_on_request=lambda kwargs: {"obj": kwargs["reddit_app"]},
    )
    @api.restrict_enabled(lambda kwargs: kwargs["reddit_app"])
    @api.response(schemas.DetailedRedditAppSchema())
    @api.response(code=HTTPStatus.NOT_FOUND, description="Reddit App not found.")
    def get(self, reddit_app):
        """
        Get Reddit App details by ID.
        """
        return reddit_app

    @api.login_required()
    @api.permission_required(
        permissions.OwnerRolePermission,
        kwargs_on_request=lambda kwargs: {"obj": kwargs["reddit_app"]},
    )
    @api.restrict_enabled(lambda kwargs: kwargs["reddit_app"])
    @api.parameters(parameters.GetRefreshTokenByRedditor())
    @api.response(DetailedRefreshTokenSchema())
    @api.response(
        code=HTTPStatus.FORBIDDEN,
        description="You don't have the permission to access other users' Refresh Tokens.",
    )
    @api.response(code=HTTPStatus.NOT_FOUND, description="Reddit App or Redditor not found.")
    def post(self, args, reddit_app: RedditApp):
        """
        Get Refresh Token by reddit app and redditor.

        Only Admins can see Refresh Tokens for other users' Reddit Apps. Regular users will see their own Reddit Apps' Refresh Tokens.
        """
        refresh_token = reddit_app.get_refresh_token(args["redditor"])
        if refresh_token:
            return refresh_token
        else:
            abort(404)

    @api.login_required()
    @api.permission_required(
        permissions.OwnerRolePermission,
        kwargs_on_request=lambda kwargs: {"obj": kwargs["reddit_app"]},
    )
    @api.permission_required(permissions.WriteAccessPermission())
    @api.response(code=HTTPStatus.CONFLICT)
    @api.response(code=HTTPStatus.NO_CONTENT)
    @api.response(code=HTTPStatus.NOT_FOUND, description="Reddit App not found.")
    def delete(self, reddit_app):
        """
        Delete a Reddit App by ID.
        """
        try:
            with api.commit_or_abort(db.session, default_error_message="Failed to delete Reddit App."):
                db.session.delete(reddit_app)
        except Exception as error:  # pragma: no cover
            log.exception(error)
        return None

    @api.login_required()
    @api.permission_required(
        permissions.OwnerRolePermission,
        kwargs_on_request=lambda kwargs: {"obj": kwargs["reddit_app"]},
    )
    @api.parameters(parameters.PatchRedditAppDetailsParameters())
    @api.response(schemas.DetailedRedditAppSchema())
    @api.response(code=HTTPStatus.CONFLICT)
    @api.response(code=HTTPStatus.NOT_FOUND, description="Reddit App not found.")
    def patch(self, args, reddit_app):
        """
        Patch reddit_app details by ID.
        """
        with api.commit_or_abort(db.session, default_error_message="Failed to update Reddit App details."):
            parameters.PatchRedditAppDetailsParameters.perform_patch(args, reddit_app)
            db.session.merge(reddit_app)
        return reddit_app


@api.route("/<int:reddit_app_id>/generate_auth")
@api.login_required()
@api.response(code=HTTPStatus.NOT_FOUND, description="Reddit App not found.")
@api.resolve_object_to_model(RedditApp, "reddit_app")
class GenerateAuthUrl(Resource):
    """
    Generate a reddit auth url
    """

    @api.permission_required(
        permissions.OwnerRolePermission,
        kwargs_on_request=lambda kwargs: {"obj": kwargs["reddit_app"]},
    )
    @api.parameters(parameters.GenerateAuthUrlParameters())
    @api.response(schemas.AuthUrlSchema())
    def post(self, args, reddit_app):
        """
        Generate a reddit auth url
        """
        user_verification = None
        user_verification_id = args.pop("user_verification_id", None)
        user_verification_user_id = args.pop("user_verification_user_id", None)
        if user_verification_id:
            user_verification = UserVerification.query.get_or_404(user_verification_id)
        if not user_verification and user_verification_user_id:
            user_verification = UserVerification.query.filter_by(user_id=user_verification_user_id).first_or_404()
        auth_url = reddit_app.gen_auth_url(args["scopes"], args["duration"], user_verification)
        setattr(reddit_app, "auth_url", auth_url)
        return reddit_app
