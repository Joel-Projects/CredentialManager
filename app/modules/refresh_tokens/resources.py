import logging

from flask_login import current_user
from flask_restplus._http import HTTPStatus

from app.extensions.api import Namespace, http_exceptions
from flask_restplus_patched import Resource

from .. import get_viewable_items
from ..reddit_apps.models import RedditApp
from ..users import permissions
from . import parameters, schemas
from .models import RefreshToken, db

log = logging.getLogger(__name__)
api = Namespace("refresh_tokens", description="Refresh Token Management")


@api.route("/")
@api.login_required()
class RefreshTokens(Resource):
    """
    Manipulations with Refresh Tokens.
    """

    @api.response(schemas.BaseRefreshTokenSchema(many=True))
    @api.parameters(parameters.ListRefreshTokensParameters(), locations=("query",))
    def get(self, args):
        """
        List of Refresh Tokens.

        Returns a list of Refresh Tokens starting from ``offset`` limited by
        ``limit`` parameter.

        Only Admins can specify ``owner_id`` to see Refresh Tokens for other users' Reddit Apps. Regular users will see their own Reddit Apps' Refresh Tokens.
        """
        refresh_tokens = get_viewable_items(args, RefreshToken)
        return refresh_tokens.offset(args["offset"]).limit(args["limit"])


@api.route("/<int:refresh_token_id>")
@api.login_required()
@api.response(code=HTTPStatus.NOT_FOUND, description="Refresh Token not found.")
@api.resolve_object_to_model(RefreshToken, "refresh_token")
class RefreshTokenByID(Resource):
    """
    Manipulations with a specific Refresh Token.
    """

    @api.permission_required(
        permissions.OwnerRolePermission,
        kwargs_on_request=lambda kwargs: {"obj": kwargs["refresh_token"]},
    )
    @api.response(schemas.DetailedRefreshTokenSchema())
    def get(self, refresh_token):
        """
        Get Refresh Token details by ID.
        """
        return refresh_token

    @api.permission_required(
        permissions.OwnerRolePermission,
        kwargs_on_request=lambda kwargs: {"obj": kwargs["refresh_token"]},
    )
    @api.permission_required(permissions.WriteAccessPermission())
    @api.response(code=HTTPStatus.CONFLICT)
    @api.response(code=HTTPStatus.NO_CONTENT)
    def delete(self, refresh_token):
        """
        Delete a Refresh Token by ID.
        """
        with api.commit_or_abort(
            db.session, default_error_message="Failed to delete Refresh Token."
        ):
            db.session.delete(refresh_token)
        return None

    @api.permission_required(
        permissions.OwnerRolePermission,
        kwargs_on_request=lambda kwargs: {"obj": kwargs["refresh_token"]},
    )
    @api.parameters(parameters.PatchRefreshTokenDetailsParameters())
    @api.response(schemas.DetailedRefreshTokenSchema())
    @api.response(code=HTTPStatus.CONFLICT)
    def patch(self, args, refresh_token):
        """
        Patch refresh_token details by ID.
        """
        with api.commit_or_abort(
            db.session, default_error_message="Failed to update Refresh Token details."
        ):
            parameters.PatchRefreshTokenDetailsParameters.perform_patch(
                args, refresh_token
            )
            db.session.merge(refresh_token)
        return refresh_token


@api.route("/by_redditor")
@api.login_required()
class GetRefreshTokenByRedditor(Resource):
    """
    Get Refresh Token by Redditor
    """

    @api.parameters(parameters.GetRefreshTokenByRedditor())
    @api.response(schemas.DetailedRefreshTokenSchema())
    def post(self, args):
        """
        Get Refresh Token by reddit app and redditor.

        Only Admins can see Refresh Tokens for other users' Reddit Apps. Regular users will see their own Reddit Apps' Refresh Tokens.
        """
        reddit_app = RedditApp.query.get_or_404(args["reddit_app_id"])
        refresh_tokens = RefreshToken.query
        refresh_token = refresh_tokens.filter_by(
            redditor=args["redditor"], reddit_app_id=reddit_app.id, revoked=False
        )
        return refresh_token.first_or_404(
            f'Redditor {args["redditor"]!r} does not exist.'
        )
