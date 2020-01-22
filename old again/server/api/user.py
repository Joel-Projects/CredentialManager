import json
from flask_restful import Resource, request
# from flask_restplus import Namespace, Resource, fields
from flask_login import login_required, current_user
from flask import jsonify
from ..decorators import *
from .. import db, log, appApi, userSerializer, User, csrf

@login_required
@requiresAdmin
@csrf.exempt
@appApi.resource('/user')
class create(Resource):


    def get(self):
        '''Create user

        .. :quickref: Create User; Create user

        **Example request**:

        .. sourcecode:: http

            GET /api/user HTTP/1.1
            Host: credmgr.jesassn.org
            Content-Type: application/x-www-form-urlencoded

            id=1

        **Example response**:

        .. sourcecode:: http

           HTTP/1.1 200 Accepted
           Content-Type: application/json

            {
                "success": true,
                "error": null,
                "user": {
                    "id": 1,
                    "username": "spaz",
                    "admin": true,
                    "created": 01/06/2020 02:28:45 PM CST,
                    "created_by": "root",
                    "updated": 01/06/2020 02:28:45 PM CST,
                    "updated_by": "root"
                }
            }

        :formparam username: username, case-insensitive
        :formparam password: password
        :formparam admin: enables/disables the user's ability to create users and see other users' apps

        :resheader Content-Type: application/json

        :status 200: User returned.
        :status 403: Unauthorized.
        :status 404: Username or password not specified or bad request
        '''

    def post(self):
        '''Create user

        .. :quickref: Create User; Create user

        **Example request**:

        .. sourcecode:: http

            POST /api/user HTTP/1.1
            Host: credmgr.jesassn.org
            Content-Type: application/x-www-form-urlencoded

            username=spaz&password=password&admin=true

        **Example response**:

        .. sourcecode:: http

           HTTP/1.1 202 Created
           Content-Type: application/json

            {
                "success": "Created user: 'spaz' successfully!",
                "error": null,
                "userExists": false,
                "user": {
                    "id": 1,
                    "username": "spaz",
                    "admin": true,
                    "created": 01/06/2020 02:28:45 PM CST,
                    "created_by": "root",
                    "updated": 01/06/2020 02:28:45 PM CST,
                    "updated_by": "root"
                }
            }

        :formparam username: username, case-insensitive
        :formparam password: password
        :formparam admin: enables/disables the user's ability to create users and see other users' apps

        :resheader Content-Type: application/json

        :status 201: The user was created successfully.
        :status 400: Username or password not specified or bad request
        :status 403: Unauthorized.
        :status 409: The user already exists.
        '''
        userExists = False
        user = None
        code = None
        username = request.form.get('username')
        password = request.form.get('password')
        admin = request.form.get('admin') == 'True'
        if username and password:
            if current_user.admin:
                try:
                    user = User.query.filter_by(username=username).first()
                    if user:
                        userExists = True
                        message = 'A user with that username already exists!'
                        status = 'fail'
                    else:
                        user = User(username=username, admin=admin, password=password, updated_by=getattr(current_user, 'username', None), created_by=getattr(current_user, 'username', None))
                        db.session.add(user)
                        db.session.commit()
                        status = 'success'
                        message = f"Created user: '{user.username}' successfully!"
                        code = 201
                except Exception as e:
                    log.exception(e)
                    message = str(e)
                    status = 'fail'
                    code = 400
            else:
                code = 403
                message = 'You\'re not allowed to do that!'
                status = 'fail'
        else:
            code = 400
            message = 'Username or password not specified!'
            status = 'fail'
        if user:
            user = userSerializer.dump(user)
        return {'status': status, 'message': message, 'userExists': userExists, 'user': user}, code

    def patch(self):
        '''Update user

        .. :quickref: Update User; Update user

        **Example request**:

        .. sourcecode:: http

            PATCH /api/user HTTP/1.1
            Host: credmgr.jesassn.org
            Content-Type: application/x-www-form-urlencoded

            id=1&username=spaz&password=password&admin=true

        **Example response**:

        .. sourcecode:: http

           HTTP/1.1 202 Accepted
           Content-Type: application/json

            {
                "success": "Updated user: 'spaz' successfully!",
                "error": null,
                "user": {
                    "id": 1,
                    "username": "spaz",
                    "admin": true,
                    "created": 01/06/2020 02:28:45 PM CST,
                    "created_by": "root",
                    "updated": 01/06/2020 02:28:45 PM CST,
                    "updated_by": "root"
                }
            }

        :formparam id: user ID
        :formparam username: updates username
        :formparam password: updates password
        :formparam admin: enables/disables the user's ability to create users and see other users' apps

        :resheader Content-Type: application/json

        :status 201: The user was updated successfully.
        :status 400: The posted transaction was invalid.
        :status 403: Unauthorized.
        :status 404: The user does not exist.
        '''
        user = None
        id = request.form.get('id', None)
        attrs = request.form.get('attrs', {})
        if isinstance(attrs, str):
            attrs = json.loads(request.form.get('attrs', '{}'))
        if current_user.admin:
            if attrs:
                try:
                    user = User.query.filter_by(id=id).first()
                    if user:
                        admin = attrs.get('admin', None) == 'True'
                        if admin:
                            del(attrs['admin'])
                            user.admin = admin
                        for key, value in attrs.items():
                            setattr(user, key, value)
                        db.session.commit()
                        status = 'success'
                        message = f"Update user: '{user.username}' successfully!"
                        code = 200
                    else:
                        message = "That user doesn't exist!"
                        status = 'fail'
                        code = 404
                except Exception as e:
                    log.exception(e)
                    message = str(e)
                    status = 'fail'
                    code = 400
            else:
                message = 'You must specify an attribute to update!'
                status = 'fail'
                code = 400
        else:
            code = 403
            message = 'You\'re not allowed to do that!'
            status = 'fail'
        if user:
            user = userSerializer.dump(user)
        return {'status': status, 'message': message, 'user': user}, code
    
    def delete(self):
        '''Delete user

        .. :quickref: Delete User; Delete user

        **Example request**:

        .. sourcecode:: http

            DELETE /api/user HTTP/1.1
            Host: credmgr.jesassn.org
            Content-Type: application/x-www-form-urlencoded

            id=1

        **Example response**:

        .. sourcecode:: http

           HTTP/1.1 202 Accepted
           Content-Type: application/json

            {
                "success": "Deleted user: 'spaz' successfully!",
                "error": null
            }

        :formparam id: user ID

        :resheader Content-Type: application/json

        :status 202: The user was deleted successfully.
        :status 400: The posted transaction was invalid.
        :status 403: Unauthorized.
        :status 404: The specified user was not found.
        '''
        userExists = False
        user = None
        code = None
        userid = request.form.get('id')
        if userid:
            if current_user.admin:
                try:
                    user = User.query.filter_by(id=userid).first()
                    if user:
                        db.session.delete(user)
                        db.session.commit()
                        status = 'success'
                        message = f"Deleted user: '{user.username}' successfully!"
                        code = 200
                    else:
                        message = "That user doesn't exist!"
                        status = 'fail'
                        code = 404
                except Exception as e:
                    log.exception(e)
                    message = str(e)
                    status = 'fail'
                    code = 400
            else:
                code = 403
                message = "You're not allowed to do that!"
                status = 'fail'
        else:
            code = 400
            message = 'Username or password not specified!'
            status = 'fail'
        return {'status': status, 'message': message}, code