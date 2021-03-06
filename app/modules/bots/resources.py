import logging

from flask_login import current_user
from flask_restplus._http import HTTPStatus

from app.extensions.api import Namespace, http_exceptions
from flask_restplus_patched import Resource

from .. import get_viewable_items
from ..users import permissions
from ..users.models import User
from . import parameters, schemas
from .models import Bot, db

log = logging.getLogger(__name__)
api = Namespace("bots", description="Bot Management")


def verify_enabled_apps(bot):
    query = Bot.query
    if not (current_user.is_admin or current_user.is_internal):
        query = Bot.query.filter(Bot.owner == current_user)
    elif current_user.is_admin and not current_user.is_internal:
        query = Bot.query.filter(Bot.owner.has(internal=False))
    bot = query.filter_by(id=bot.id).first_or_404()
    for app in ["reddit_app", "sentry_token", "database_credential"]:
        if getattr(bot, app) and not getattr(bot, app).enabled:
            http_exceptions.abort(
                code=HTTPStatus.FAILED_DEPENDENCY,
                message="Requested object has a sub-object that is disabled",
            )
    return bot


@api.route("/")
@api.login_required()
class Bots(Resource):
    """
    Manipulations with Bots.
    """

    @api.response(schemas.BaseBotSchema(many=True))
    @api.parameters(parameters.ListBotsParameters(), locations=("query",))
    def get(self, args):
        """
        List of Bots.

        Returns a list of Bots starting from ``offset`` limited by
        ``limit`` parameter.

        Only Admins can specify ``owner`` to see Bots for other users. Regular users will see their own Bots.
        """
        bots = get_viewable_items(args, Bot)
        return bots.offset(args["offset"]).limit(args["limit"])

    @api.parameters(parameters.CreateBotParameters())
    @api.response(schemas.DetailedBotSchema())
    @api.response(code=HTTPStatus.FORBIDDEN)
    @api.response(code=HTTPStatus.CONFLICT)
    def post(self, args):
        """
        Create a new Bot.

        Bots are used for grouping apps into a single request
        """
        args.owner = current_user
        if args.owner_id:
            args.owner = User.query.get(args.owner_id)
        with api.commit_or_abort(db.session, default_error_message="Failed to create a new Bot."):
            db.session.add(args)
        return args


@api.route("/<int:bot_id>")
@api.login_required()
@api.response(code=HTTPStatus.NOT_FOUND, description="Bot not found.")
@api.resolve_object_to_model(Bot, "bot")
class BotByID(Resource):
    """
    Manipulations with a specific Bot.
    """

    @api.login_required()
    @api.permission_required(
        permissions.OwnerRolePermission,
        kwargs_on_request=lambda kwargs: {"obj": kwargs["bot"]},
    )
    @api.restrict_enabled(lambda kwargs: kwargs["bot"])
    @api.response(schemas.DetailedBotSchema())
    def get(self, bot):
        """
        Get Bot details by ID.
        """
        log.info("bot fetch begin")
        return verify_enabled_apps(bot)

    @api.login_required()
    @api.permission_required(
        permissions.OwnerRolePermission,
        kwargs_on_request=lambda kwargs: {"obj": kwargs["bot"]},
    )
    @api.response(code=HTTPStatus.CONFLICT)
    @api.response(code=HTTPStatus.NO_CONTENT)
    def delete(self, bot):
        """
        Delete a Bot by ID.
        """
        with api.commit_or_abort(db.session, default_error_message="Failed to delete Bot."):
            db.session.delete(bot)
        return None

    @api.login_required()
    @api.permission_required(
        permissions.OwnerRolePermission,
        kwargs_on_request=lambda kwargs: {"obj": kwargs["bot"]},
    )
    @api.parameters(parameters.PatchBotDetailsParameters())
    @api.response(schemas.DetailedBotSchema())
    @api.response(code=HTTPStatus.CONFLICT)
    def patch(self, args, bot):
        """
        Patch bot details by ID.
        """
        with api.commit_or_abort(db.session, default_error_message="Failed to update Bot details."):
            parameters.PatchBotDetailsParameters.perform_patch(args, bot)
            db.session.merge(bot)
        return bot


@api.route("/by_name")
@api.login_required()
@api.response(code=HTTPStatus.NOT_FOUND, description="Bot not found.")
class GetBotByName(Resource):
    """
    Get Bot by name
    """

    @api.parameters(parameters.GetBotByName())
    @api.response(schemas.DetailedBotSchema())
    @api.resolve_object_to_model(Bot, "bot", "app_name")
    @api.restrict_enabled(lambda kwargs: kwargs["bot"])
    def post(self, bot):
        """
        Get Bot by name.
        """
        return verify_enabled_apps(bot)
