from flask_restful import Resource, request
# from flask_restplus import Namespace, Resource, fields
from flask_login import login_required, current_user
from flask import jsonify
from ..decorators import *
from .. import db, log, appApi, userSerializer, User

@login_required
@requiresAdmin
@appApi.resource('/user')
class create(Resource):

    def post(self):
        '''Create user

        .. :quickref: Create User; Create user

        **Example request**:

        .. sourcecode:: http

            POST /api/users/create HTTP/1.1
            Host: credmgr.jesassn.org
            Content-Type: application/x-www-form-urlencoded

            username=spaz&password=password&admin=true

        **Example response**:

        .. sourcecode:: http

           HTTP/1.1 202 Accepted
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

        :status 202: The user was created successfully
        :status 409: The user already exists
        :status 400: Username or password not specified or bad request
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

@login_required
@requiresAdmin
@appApi.resource('/users/update')
class update(Resource):

    def post(self, user):
        '''Update user

        .. :quickref: Update User; Update user

        **Example request**:

        .. sourcecode:: http

            POST /api/users/update HTTP/1.1
            Host: credmgr.jesassn.org
            Content-Type: application/x-www-form-urlencoded

            user=username=spaz&password=password&admin=true

        **Example response**:

        .. sourcecode:: http

           HTTP/1.1 202 Accepted
           Content-Type: application/json

            {
                "success": "Updated user: 'spaz' successfully!",
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

        :status 202: The user was updated successfully
        :status 400: The posted transaction was invalid.
        '''
        username = user
        password = request.form.get('password', None)
        admin = request.form.get('admin') == 'true'
        updated_by = current_user.username
        user = User.query.filter_by(username=username).first()
        success = None
        error = None
        code = None
        userExists = False
        try:
            if user:
                user.username = username
                if password:
                    user.passowrd = password
                if user.username in ('admin', 'spaz'):
                    admin = True
                if current_user.admin:
                    user.admin = admin
                else:
                    user.admin = user.admin
                user.updated_by = updated_by
                db.session.commit()
                success = f'Updated {user.username} successfully!'
                code = 202
            else:
                error = "That user doesn't exist!"
                code = 404
        except Exception as e:
            log.exception(e)
            error = str(e)
            code = 400
        return {'success': success, 'error': error, 'userExists': userExists, 'user': userSerializer.dump(user)}, code