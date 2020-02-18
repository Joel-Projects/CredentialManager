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
from .models import db, Bot
from ..users import permissions
from ..users.models import User

log = logging.getLogger(__name__)
api = Namespace('bots', description="Bot Management")


@api.route('/')
@api.login_required()
class Bots(Resource):
    """
    Manipulations with Bots.
    """

    # @api.permission_required(permissions.AdminRolePermission())
    @api.response(schemas.BaseBotSchema(many=True))
    @api.parameters(parameters.ListBotsParameters(), locations=('query',))
    def get(self, args):
        """
        List of Bots.

        Returns a list of Bots starting from ``offset`` limited by
        ``limit`` parameter.

        Only Admins can specify ``owner`` to see Bots for other users. Regular users will see their own Bots.
        """
        apiKeys = Bot.query
        if 'owner_id' in args:
            owner_id = args['owner_id']
            if current_user.is_admin:
                apiKeys = apiKeys.filter(Bot.owner_id == owner_id)
            else:
                if owner_id == current_user.id:
                    apiKeys = apiKeys.filter(Bot.owner == current_user)
                else:
                    http_exceptions.abort(HTTPStatus.FORBIDDEN, "You don't have the permission to access other users' Bots.")
        else:
            if not current_user.is_admin:
                apiKeys = apiKeys.filter(Bot.owner == current_user)
        return apiKeys.offset(args['offset']).limit(args['limit'])

    @api.parameters(parameters.CreateBotParameters())
    @api.response(schemas.DetailedBotSchema())
    @api.response(code=HTTPStatus.FORBIDDEN)
    @api.response(code=HTTPStatus.CONFLICT)
    def post(self, args):
        """
        Create a new Bot.

        Bots are used for grouping apps into a single request
        """
        if getattr(args, 'owner_id', None):
            owner_id = args.owner_id
            if current_user.is_admin:
                owner = User.query.get(owner_id)
            else:
                if owner_id == current_user.id:
                    owner = current_user
                else:
                    http_exceptions.abort(HTTPStatus.FORBIDDEN, "You don't have the permission to create Bots for other users.")
        else:
            owner = current_user
        with api.commit_or_abort(db.session, default_error_message="Failed to create a new Bot."):
            newBot = Bot(owner=owner, dsn=args.dsn, name=args.name)
            db.session.add(newBot)
        return newBot

@api.route('/<int:bot_id>')
@api.login_required()
@api.response(code=HTTPStatus.NOT_FOUND, description="Bot not found.")
@api.resolveObjectToModel(Bot, 'bot')
class BotByID(Resource):
    """
    Manipulations with a specific Bot.
    """

    @api.login_required()
    @api.permission_required(permissions.OwnerRolePermission, kwargs_on_request=lambda kwargs: {'obj': kwargs['bot']})
    @api.response(schemas.DetailedBotSchema())
    def get(self, bot):
        """
        Get Bot details by ID.
        """
        return bot

    @api.login_required()
    @api.permission_required(permissions.OwnerRolePermission, kwargs_on_request=lambda kwargs: {'obj': kwargs['bot']})
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
    @api.permission_required(permissions.OwnerRolePermission, kwargs_on_request=lambda kwargs: {'obj': kwargs['bot']})
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
