from flask_restful import Resource
from flask_login import login_required
from ..decorators import *
from .. import db, log, appApi, userSerializer, botSerializer, redditAppSerializer, refreshTokenSerializer, sentrySerializer, databaseSerializer, apiTokenSerializer
from ..models import User, Bot, RedditApp, RefreshToken, Sentry, Database, ApiToken

itemTypes = {'users': User, 'bots': Bot, 'reddit_apps': RedditApp, 'refresh_tokens': RefreshToken, 'sentry_tokens': Sentry, 'database_credentials': Database, 'api_tokens': ApiToken, }
names = {'users': 'username', 'bots': 'bot_name', 'reddit_apps': 'app_name', 'refresh_tokens': 'app_name', 'sentry_tokens': 'app_name', 'database_credentials': 'app_name', 'api_tokens': 'app_name', }
# serializers = {'users': userSerializer, 'bots': botSerializer, 'reddit_apps': redditAppSerializer, 'refresh_tokens': refreshTokenSerializer, 'sentry_tokens': sentrySerializer, 'database_credentials': databaseSerializer, 'api_tokens': apiTokenSerializer, }

@login_required
@requiresAdmin
@appApi.resource('/toggle')
class toggle(Resource):

    def post(self):
        '''Toggles an app

        .. :quickref: Toggle; Enable/Disable an app

        **Example request**:

        .. sourcecode:: http

            POST /api/toggle HTTP/1.1
            Host: credmgr.jesassn.org
            Content-Type: application/x-www-form-urlencoded

            item_type=users&id=1&enabled=true

        **Example response**:

        .. sourcecode:: http

           HTTP/1.1 202 Accepted
           Content-Type: application/json

            {
                "success": true,
                "error": null,
                "name": 'root',
                "enabled": true
            }

        :formparam item_type: item type
            One of:
                - ``users``
                - ``bots``
                - ``reddit_apps``
                - ``sentry_tokens``
                - ``database_credentials``
                - ``api_tokens``
        :formparam id: item id
        :formparam enabled: enables/disables the app

        :resheader Content-Type: application/json

        :status 202: The item was toggled successfully
        :status 400: Bad Request
        :status 404: App not found
            '''
        success = None
        error = None
        code = None
        item_type = request.form.get('item_type')
        if item_type:
            item_type = item_type.lower()
        id = request.form.get('id')
        if id.isdigit():
            id = int(id)
        else:
            return abort(400, 'id must be an integer')
        enabled = True if request.form.get('enabled') else False
        item = itemTypes.get(item_type, None)
        if not item:
            return 404
        if item_type and id:
            try:
                item = item.query.filter_by(id=id).first()
                if item:
                    item.enabled = enabled
                    db.session.commit()
                    success = True
                    code = 202
            except Exception as e:
                log.exception(error)
                error = e
                code = 400
        else:
            code = 400
            error = 'Item type or id not specified!'
        return {'success': success, 'error': str(error), 'name': getattr(item, names[item_type]), 'enabled': item.enabled}

@login_required
@requiresAdmin
@appApi.resource('/users/delete')
class delete(Resource):

    def post(self, user):
        '''Delete item

        .. :quickref: Delete item; Delete item

        **Example request**:

        .. sourcecode:: http

            POST /api/delete HTTP/1.1
            Host: credmgr.jesassn.org
            Content-Type: application/x-www-form-urlencoded

            item_type=bots=spaz&item_id=1&cascade=true

        **Example response**:

        .. sourcecode:: http

           HTTP/1.1 202 Accepted
           Content-Type: application/json

            {
                "success": "Deleted user: 'root' successfully!",
                "error": null,
                "name": 'root'
            }

        :formparam username: username, case-insensitive
        :formparam password: password
        :formparam admin: enables/disables the user's ability to create users and see other users' apps

        :resheader Content-Type: application/json

        :status 202: The item was updated successfully
        :status 400: The posted transaction was invalid.
        '''
        notification = {'success': None, 'error': None}
        code = None
        item_type = request.form.get('item_type')
        if item_type:
            item_type = item_type.lower()
        item = itemTypes.get(item_type, None)
        id = request.form.get('id')
        try:
            item = item.query.filter_by(id=id).first()
            if item:
                if getattr(item, 'username', None) in ('root', 'spaz'):
                    notification['error'] = 'You can\'t delete that item'
                else:
                    db.session.delete(item)
                    db.session.commit()
                    notification['success'] = True
            else:
                notification['error'] = "That item doesn't exist"
        except Exception as error:
            notification['error'] = error
        return {'success': notification['success'], 'error': notification['error'], 'notification': notification, 'name': getattr(item, names[item_type])}, code
