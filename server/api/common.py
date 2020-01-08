from flask_restful import Resource
from flask_login import login_required
from ..decorators import *
from .. import db, log, appApi, items, csrf

@csrf.exempt
@verifyOwnership
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

            item_type=bot&id=1&enabled=true

        **Example response**:

        .. sourcecode:: http

            HTTP/1.0 202 ACCEPTED
            Content-Type: application/json
            Content-Length: 95
            Server: Werkzeug/0.16.0 Python/3.7.5
            Date: Tue, 07 Jan 2020 23:58:33 GMT

            {
              "status": "success",
              "message": "Enalbled",
              "name": "bot",
              "enabled": true
            }

        :fparam item_type: item type
            One of:
                - ``user``
                - ``bot``
                - ``reddit_app``
                - ``sentry_token``
                - ``database_credential``
                - ``api_token``
        :fparam id: item id
        :fparam enabled: enables/disables the app

        :resheader Content-Type: application/json

        :status 202: The item was toggled successfully
        :status 400: Bad Request
        :status 404: App not found
            '''
        status = None
        message = None
        code = None
        item_type = request.form.get('item_type')
        if item_type:
            item_type = item_type.lower()
        id = request.form.get('id')
        if id.isdigit():
            id = int(id)
        else:
            return abort(400, 'id must be an integer')
        item = items.get(item_type, {}).get('model', None)
        if item:
            if item_type and id:
                try:
                    item = item.query.filter_by(id=id).first()
                    if item:
                        if item.owner == current_user or current_user.admin:
                            enabled = request.form.get('enabled', str(not(item.enabled))) == 'True'
                            item.enabled = enabled
                            db.session.commit()
                            status = 'success'
                            code = 202
                            message = f"{('Disabled', 'Enabled')[item.enabled]} '{getattr(item, items[item_type]['name'])}' successfully"
                        else:
                            code = 403
                            status = 'fail'
                            message = "You don't have the permission to access the requested resource."
                except Exception as e:
                    log.exception(e)
                    code = 400
                    status = 'fail'
                    message = str(e)
            else:
                code = 400
                status = 'fail'
                message = 'Item type or id not specified!'
        return {'status': status, 'message': message, 'name': getattr(item, items[item_type]['name']), 'enabled': item.enabled}, code

@csrf.exempt
@verifyOwnership
@appApi.resource('/delete')
class delete(Resource):

    def post(self):
        '''Delete item

        .. :quickref: Delete item; Delete item

        **Example request**:

        .. sourcecode:: http

            POST /api/delete HTTP/1.1
            Host: credmgr.jesassn.org
            Content-Type: application/x-www-form-urlencoded

            item_type=user&item_id=1&cascade=true

        **Example response**:

        .. sourcecode:: http

           HTTP/1.1 202 Accepted
           Content-Type: application/json

            {
                "status": "Deleted user: 'root' successfully!",
                "message": null,
                "name": 'root'
            }

        :fparam item_type: username, case-insensitive
        :fparam id: password
        :fparam cascade: enables/disables the user's ability to create users and see other users' apps

        :resheader Content-Type: application/json

        :status 202: The item was updated successfully
        :status 400: The posted transaction was invalid.
        '''
        status = None
        message = None
        code = None
        item_type = request.form.get('item_type')
        if item_type:
            item_type = item_type.lower()
        id = request.form.get('id')
        if id.isdigit():
            id = int(id)
        else:
            return abort(400, 'id must be an integer')
        itemModel = items.get(item_type, {}).get('model', None)
        if itemModel:
            if item_type and id:
                try:
                    item = itemModel.query.filter(itemModel.id==id).first()
                    if item:
                        if item.owner == current_user or current_user.admin:
                            itemModel.query.filter(itemModel.id==id).delete()
                            db.session.commit()
                            status = 'success'
                            code = 202
                            message = f"Deleted '{getattr(item, items[item_type]['name'])}' successfully."
                        else:
                            code = 403
                            status = 'fail'
                            message = "You don't have the permission to access the requested resource."
                except Exception as e:
                    log.exception(e)
                    code = 400
                    status = 'fail'
                    message = str(e)
            else:
                code = 400
                status = 'fail'
                message = 'Item type or id not specified.'
        return {'status': status, 'message': message, 'name': getattr(item, items[item_type]['name'])}, code
