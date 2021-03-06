import logging

from flask_login import current_user
from flask_restplus._http import HTTPStatus

from app.extensions.api import Namespace
from flask_restplus_patched import Resource

from .. import get_viewable_items
from ..users import permissions
from ..users.models import User
from . import parameters, schemas
from .models import SentryToken, db
from .sentry_requestor import SentryRequestor

log = logging.getLogger(__name__)
api = Namespace("sentry_tokens", description="Sentry Token Management")


@api.route("/")
@api.login_required()
class SentryTokens(Resource):
    """
    Manipulations with Sentry Tokens.
    """

    # @api.permission_required(permissions.AdminRolePermission())
    @api.response(schemas.BaseSentryTokenSchema(many=True))
    @api.parameters(parameters.ListSentryTokensParameters(), locations=("query",))
    def get(self, args):
        """
        List of Sentry Tokens.

        Returns a list of Sentry Tokens starting from ``offset`` limited by
        ``limit`` parameter.

        Only Admins can specify ``owner`` to see Sentry Tokens for other users. Regular users will see their own Sentry Tokens.
        """
        sentry_tokens = get_viewable_items(args, SentryToken)
        return sentry_tokens.offset(args["offset"]).limit(args["limit"])

    @api.parameters(parameters.CreateSentryTokenParameters())
    @api.response(schemas.DetailedSentryTokenSchema())
    @api.response(code=HTTPStatus.FORBIDDEN)
    @api.response(code=HTTPStatus.CONFLICT)
    def post(self, args):
        """
        Create a new Sentry Token.

        Sentry Tokens are used for logging and error reporting in applications
        """
        args.owner = current_user
        if args.owner_id:
            args.owner = User.query.get(args.owner_id)
        with api.commit_or_abort(db.session, default_error_message="Failed to create a new Sentry Token."):
            db.session.add(args)
        return args


@api.route("/<int:sentry_token_id>")
@api.login_required()
@api.response(code=HTTPStatus.NOT_FOUND, description="Sentry Token not found.")
@api.resolve_object_to_model(SentryToken, "sentry_token")
class SentryTokenByID(Resource):
    """
    Manipulations with a specific Sentry Token.
    """

    @api.login_required()
    @api.permission_required(
        permissions.OwnerRolePermission,
        kwargs_on_request=lambda kwargs: {"obj": kwargs["sentry_token"]},
    )
    @api.restrict_enabled(lambda kwargs: kwargs["sentry_token"])
    @api.response(schemas.DetailedSentryTokenSchema())
    def get(self, sentry_token):
        """
        Get Sentry Token details by ID.
        """
        return sentry_token

    @api.login_required()
    @api.permission_required(
        permissions.OwnerRolePermission,
        kwargs_on_request=lambda kwargs: {"obj": kwargs["sentry_token"]},
    )
    @api.permission_required(permissions.WriteAccessPermission())
    @api.response(code=HTTPStatus.CONFLICT)
    @api.response(code=HTTPStatus.NO_CONTENT)
    def delete(self, sentry_token):
        """
        Delete a Sentry Token by ID.
        """
        with api.commit_or_abort(db.session, default_error_message="Failed to delete Sentry Token."):
            db.session.delete(sentry_token)
        return None

    @api.login_required()
    @api.permission_required(
        permissions.OwnerRolePermission,
        kwargs_on_request=lambda kwargs: {"obj": kwargs["sentry_token"]},
    )
    @api.parameters(parameters.PatchSentryTokenDetailsParameters())
    @api.response(schemas.DetailedSentryTokenSchema())
    @api.response(code=HTTPStatus.CONFLICT)
    def patch(self, args, sentry_token):
        """
        Patch sentry_token details by ID.
        """
        with api.commit_or_abort(db.session, default_error_message="Failed to update Sentry Token details."):
            parameters.PatchSentryTokenDetailsParameters.perform_patch(args, sentry_token)
            db.session.merge(sentry_token)
        return sentry_token


@api.route("/sentry_organizations")
class SentryOrganizations(Resource):
    """
    Get organizations from Sentry
    """

    @api.login_required()
    def get(self):  # pragma: no cover
        """
        Get Sentry organizations
        """
        response = []
        if current_user.sentry_auth_token:
            requestor = SentryRequestor(current_user.sentry_auth_token)
            response = [
                (i.slug, i.name)
                for i in requestor.get("/api/0/organizations/", "organization", params={"member": True})
            ]
        return response


@api.route("/sentry_organizations/<org_slug>/teams")
class SentryOrganization(Resource):
    """
    Get organizations from Sentry
    """

    @api.login_required()
    def get(self, org_slug):  # pragma: no cover
        """
        Get Sentry organizations
        """
        response = []
        if current_user.sentry_auth_token:
            requestor = SentryRequestor(current_user.sentry_auth_token)
            response = [(i.slug, i.name) for i in requestor.get(f"/api/0/organizations/{org_slug}/teams/", "team")]
        return response
