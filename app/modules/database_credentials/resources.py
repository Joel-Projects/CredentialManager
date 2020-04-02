'''
RESTful API Auth resources
--------------------------
'''

import logging

from flask_login import current_user
from flask_restplus._http import HTTPStatus

from app.extensions.api import Namespace, http_exceptions
from flask_restplus_patched import Resource
from . import parameters, schemas
from .models import DatabaseCredential, db
from .. import getViewableItems
from ..users import permissions
from ..users.models import User


log = logging.getLogger(__name__)
api = Namespace('database_credentials', description='Database Credential Management')

@api.route('/')
@api.login_required()
class DatabaseCredentials(Resource):
    '''
    Manipulations with Database Credentials.
    '''

    # @api.permission_required(permissions.AdminRolePermission())
    @api.response(schemas.BaseDatabaseCredentialSchema(many=True))
    @api.parameters(parameters.ListDatabaseCredentialsParameters(), locations=('query',))
    def get(self, args):
        '''
        List of Database Credentials.

        Returns a list of Database Credentials starting from ``offset`` limited by
        ``limit`` parameter.

        Only Admins can specify ``owner`` to see Database Credentials for other users. Regular users will see their own Database Credentials.
        '''
        databaseCredentials = getViewableItems(args, DatabaseCredential)
        return databaseCredentials.offset(args['offset']).limit(args['limit'])

    @api.parameters(parameters.CreateDatabaseCredentialParameters())
    @api.response(schemas.DetailedDatabaseCredentialSchema())
    @api.response(code=HTTPStatus.FORBIDDEN)
    @api.response(code=HTTPStatus.CONFLICT)
    def post(self, args):
        '''
        Create a new Database Credential.

        Database Credentials are used for logging and error reporting in applications
        '''
        args.owner = current_user
        if args.owner_id:
            args.owner = User.query.get(args.owner_id)
        with api.commit_or_abort(db.session, default_error_message='Failed to create a new Database Credential.'):
            db.session.add(args)
        return args

@api.route('/<int:database_credential_id>')
@api.login_required()
@api.response(code=HTTPStatus.NOT_FOUND, description='Database Credential not found.')
@api.resolveObjectToModel(DatabaseCredential, 'database_credential')
class DatabaseCredentialByID(Resource):
    '''
    Manipulations with a specific Database Credential.
    '''

    @api.login_required()
    @api.permission_required(permissions.OwnerRolePermission, kwargs_on_request=lambda kwargs: {'obj': kwargs['database_credential']})
    @api.response(schemas.DetailedDatabaseCredentialSchema())
    def get(self, database_credential):
        '''
        Get Database Credential details by ID.
        '''
        return database_credential

    @api.login_required()
    @api.permission_required(permissions.OwnerRolePermission, kwargs_on_request=lambda kwargs: {'obj': kwargs['database_credential']})
    @api.response(code=HTTPStatus.CONFLICT)
    @api.response(code=HTTPStatus.NO_CONTENT)
    def delete(self, database_credential):
        '''
        Delete a Database Credential by ID.
        '''
        with api.commit_or_abort(db.session, default_error_message='Failed to delete Database Credential.'):
            db.session.delete(database_credential)
        return None

    @api.login_required()
    @api.permission_required(permissions.OwnerRolePermission, kwargs_on_request=lambda kwargs: {'obj': kwargs['database_credential']})
    @api.parameters(parameters.PatchDatabaseCredentialDetailsParameters())
    @api.response(schemas.DetailedDatabaseCredentialSchema())
    @api.response(code=HTTPStatus.CONFLICT)
    def patch(self, args, database_credential):
        '''
        Patch database_credential details by ID.
        '''
        with api.commit_or_abort(db.session, default_error_message='Failed to update Database Credential details.'):
            parameters.PatchDatabaseCredentialDetailsParameters.perform_patch(args, database_credential)
            db.session.merge(database_credential)
        return database_credential