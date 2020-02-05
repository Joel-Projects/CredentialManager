import logging

from flask_login import current_user
from flask_restplus_patched import Resource
from flask_restplus._http import HTTPStatus

from app.extensions import db
from app.extensions.api import Namespace, abort
from app.extensions.api.parameters import PaginationParameters
from app.modules.users import permissions

from . import parameters, schemas
from .models import Bot

log = logging.getLogger(__name__)
api = Namespace('bots', description='Bots')

@api.route('/')
@api.login_required()
@api.permission_required(permissions.OwnerRolePermission())
class Bots(Resource):

    @api.parameters(PaginationParameters())
    @api.response(schemas.BaseBotSchema(many=True))
    def get(self, args):
        '''
        List of Bot.

        Returns a list of Bot starting from ``offset`` limited by ``limit``
        parameter.
        '''
        return Bot.query.offset(args['offset']).limit(args['limit'])

    @api.login_required()
    @api.parameters(parameters.CreateBotParameters())
    @api.response(schemas.DetailedBotSchema())
    @api.response(code=HTTPStatus.CONFLICT)
    def post(self, args):
        '''
        Create a new instance of Bot.
        '''
        with api.commit_or_abort(db.session, default_error_message='Failed to create a new Bot'):
            bot = Bot(**args)
            db.session.add(bot)
        return bot


# noinspection PyUnresolvedReferences
@api.route('/<int:bot_id>')
@api.login_required()
@api.permission_required(permissions.OwnerRolePermission())
@api.response(code=HTTPStatus.NOT_FOUND, description='Bot not found.')
@api.resolveObjectToModel(Bot, 'bot')
class BotByID(Resource):
    '''
    Manipulations with a specific Bot.
    '''

    @api.response(schemas.DetailedBotSchema())
    def get(self, bot):
        '''
        Get Bot details by ID.
        '''
        return bot

    @api.login_required()
    @api.parameters(parameters.PatchBotDetailsParameters())
    @api.response(schemas.DetailedBotSchema())
    @api.response(code=HTTPStatus.CONFLICT)
    def patch(self, args, bot):
        '''
        Patch Bot details by ID.
        '''
        with api.commit_or_abort(db.session, default_error_message='Failed to update Bot details.'):
            parameters.PatchBotDetailsParameters.perform_patch(args, obj=bot)
            db.session.merge(bot)
        return bot

    @api.login_required()
    @api.response(code=HTTPStatus.CONFLICT)
    @api.response(code=HTTPStatus.NO_CONTENT)
    def delete(self, bot):
        '''
        Delete a Bot by ID.
        '''
        with api.commit_or_abort(db.session, default_error_message='Failed to delete the Bot.'):
            db.session.delete(bot)
        return None
