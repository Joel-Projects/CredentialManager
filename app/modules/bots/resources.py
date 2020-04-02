import logging

from flask_login import current_user
from flask_restplus._http import HTTPStatus

from app.extensions.api import Namespace, http_exceptions
from flask_restplus_patched import Resource
from . import parameters, schemas
from .models import Bot, db
from .. import getViewableItems
from ..users import permissions
from ..users.models import User


log = logging.getLogger(__name__)
api = Namespace('bots', description='Bot Management')

@api.route('/')
@api.login_required()
class Bots(Resource):
    '''
    Manipulations with Bots.
    '''

    @api.response(schemas.BaseBotSchema(many=True))
    @api.parameters(parameters.ListBotsParameters(), locations=('query',))
    def get(self, args):
        '''
        List of Bots.

        Returns a list of Bots starting from ``offset`` limited by
        ``limit`` parameter.

        Only Admins can specify ``owner`` to see Bots for other users. Regular users will see their own Bots.
        '''
        bots = getViewableItems(args, Bot)
        return bots.offset(args['offset']).limit(args['limit'])

    @api.parameters(parameters.CreateBotParameters())
    @api.response(schemas.DetailedBotSchema())
    @api.response(code=HTTPStatus.FORBIDDEN)
    @api.response(code=HTTPStatus.CONFLICT)
    def post(self, args):
        '''
        Create a new Bot.

        Bots are used for grouping apps into a single request
        '''
        owner = current_user
        if args.owner_id:
            owner = User.query.get(args.owner_id)
        with api.commit_or_abort(db.session, default_error_message='Failed to create a new Bot.'):
            db.session.add(args)
        return args

@api.route('/<int:bot_id>')
@api.login_required()
@api.response(code=HTTPStatus.NOT_FOUND, description='Bot not found.')
@api.resolveObjectToModel(Bot, 'bot')
class BotByID(Resource):
    '''
    Manipulations with a specific Bot.
    '''

    @api.login_required()
    @api.permission_required(permissions.OwnerRolePermission, kwargs_on_request=lambda kwargs: {'obj': kwargs['bot']})
    @api.response(schemas.DetailedBotSchema())
    def get(self, bot):
        '''
        Get Bot details by ID.
        '''
        return bot

    @api.login_required()
    @api.permission_required(permissions.OwnerRolePermission, kwargs_on_request=lambda kwargs: {'obj': kwargs['bot']})
    @api.response(code=HTTPStatus.CONFLICT)
    @api.response(code=HTTPStatus.NO_CONTENT)
    def delete(self, bot):
        '''
        Delete a Bot by ID.
        '''
        with api.commit_or_abort(db.session, default_error_message='Failed to delete Bot.'):
            db.session.delete(bot)
        return None

    @api.login_required()
    @api.permission_required(permissions.OwnerRolePermission, kwargs_on_request=lambda kwargs: {'obj': kwargs['bot']})
    @api.parameters(parameters.PatchBotDetailsParameters())
    @api.response(schemas.DetailedBotSchema())
    @api.response(code=HTTPStatus.CONFLICT)
    def patch(self, args, bot):
        '''
        Patch bot details by ID.
        '''
        with api.commit_or_abort(db.session, default_error_message='Failed to update Bot details.'):
            parameters.PatchBotDetailsParameters.perform_patch(args, bot)
            db.session.merge(bot)
        return bot

@api.route('/by_name')
@api.login_required()
@api.response(code=HTTPStatus.NOT_FOUND, description='Bot not found.')
class GetBotByName(Resource):
    '''
    Get Refresh Token by name
    '''

    @api.parameters(parameters.GetBotByName())
    @api.response(schemas.DetailedBotSchema())
    def post(self, args):
        '''
        Get Refresh Token by reddit app and redditor.

        Only Admins can specify ``owner_id`` to get other users' Bot details.
        If ``owner_id`` is not specified, only your Bots will be queried.
        '''
        app_name = args['app_name']
        bots = getViewableItems(args, Bot).filter(Bot.app_name==app_name)
        return bots.first_or_404(f'Bot {app_name!r} does not exist for the specified user.')