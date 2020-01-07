from flask_restful import Resource, request
from flask_login import login_required
from flask import jsonify
from ..decorators import *
from . import User
from .. import db, log, appApi, userSerializer

@login_required
@requiresAdmin
@appApi.resource('/users/create')
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
        success = None
        error = None
        userExists = False
        user = None
        code = None
        username = request.form.get('username')
        password = request.form.get('password')
        admin = True if request.form.get('admin') else False
        if username and password:
            try:
                user = User.query.filter_by(username=username).first()
                if user:
                    userExists = True
                else:
                    user = User(username=username, admin=admin, password=password, updated_by=current_user.username, created_by=current_user.username)
                    db.session.add(user)
                    db.session.commit()
                    success = f"Created user: '{user.username}' successfully!"
                    code = 202
            except Exception as error:
                log.exception(error)
                error = error
                code = 400
        else:
            code = 400
            error = 'Username or password not specified!'
        if user:
            user = userSerializer.dump(user)
        return {'success': success, 'error': error, 'userExists': userExists, 'user': user}, code

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
            error = e
            code = 400
        return {'success': success, 'error': error, 'userExists': userExists, 'user': userSerializer.dump(user)}, code