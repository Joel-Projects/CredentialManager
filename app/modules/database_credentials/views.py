import logging

import requests
from flask import Blueprint, request, render_template, flash, jsonify
from flask_login import current_user, login_required
from wtforms import BooleanField

from .parameters import PatchDatabaseCredentialDetailsParameters
from ..users.models import User
from ...extensions import db, paginateArgs, verifyEditable

log = logging.getLogger(__name__)
from .models import DatabaseCredential
from .forms import DatabaseCredentialForm
from .tables import DatabaseCredentialTable

DatabaseCredentialsBlueprint = Blueprint('database_credentials', __name__, template_folder='./templates', static_folder='./static', static_url_path='/database_credentials/static/')

@DatabaseCredentialsBlueprint.route('/database_credentials', methods=['GET', 'POST'])
@login_required
@paginateArgs(DatabaseCredential)
def database_credentials(page, perPage):
    form = DatabaseCredentialForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            data = form.data
            databaseCredential = DatabaseCredential(**data)
            db.session.add(databaseCredential)
        else:
            return jsonify(status='error', errors=form.errors)
    if current_user:
        if current_user.is_admin and not current_user.is_internal:
            paginator = DatabaseCredential.query.filter(*(DatabaseCredential.owner_id!=i.id for i in User.query.filter(User.internal==True).all())).paginate(page, perPage, error_out=False)
        elif current_user.is_internal:
            paginator = DatabaseCredential.query.paginate(page, perPage, error_out=False)
        else:
            paginator = current_user.database_credentials.paginate(page, perPage, error_out=False)
    else:
        paginator = current_user.database_credentials.paginate(page, perPage, error_out=False)
    table = DatabaseCredentialTable(paginator.items, current_user=current_user)
    form = DatabaseCredentialForm()
    return render_template('database_credentials.html', database_credentialsTable=table, database_credentialsForm=form, paginator=paginator, perPage=perPage)

@DatabaseCredentialsBlueprint.route('/database_credentials/<DatabaseCredential:database_credential>/', methods=['GET', 'POST'])
@login_required
@verifyEditable('database_credential')
def editDatabaseCredential(database_credential):
    form = DatabaseCredentialForm(obj=database_credential)
    if request.method == 'POST':
        if form.validate_on_submit():
            itemsToUpdate = []
            for item in PatchDatabaseCredentialDetailsParameters.fields:
                if getattr(form, item, None) is not None:
                    if not isinstance(getattr(form, item), BooleanField):
                        if getattr(form, item).data:
                            if getattr(database_credential, item) != getattr(form, item).data:
                                itemsToUpdate.append({"op": "replace", "path": f'/{item}', "value": getattr(form, item).data})
                    else:
                        if getattr(database_credential, item) != getattr(form, item).data:
                            itemsToUpdate.append({"op": "replace", "path": f'/{item}', "value": getattr(form, item).data})
            if itemsToUpdate:
                response = requests.patch(f'{request.host_url}api/v1/database_credentials/{database_credential.id}', json=itemsToUpdate, headers={'Cookie': request.headers['Cookie'], 'Content-Type': 'application/json'})
                if response.status_code == 200:
                    flash(f'Database Credential {database_credential.app_name!r} saved successfully!', 'success')
                else:
                    flash(f'Failed to update Database Credential {database_credential.app_name!r}', 'error')
        # else:
        #     return jsonify(status='error', errors=form.errors)
    return render_template('edit_database_credential.html', database_credential=database_credential, form=form)
