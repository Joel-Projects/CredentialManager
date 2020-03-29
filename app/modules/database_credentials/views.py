import logging

from flask import Blueprint, flash, jsonify, render_template, request
from flask_login import current_user, login_required

from .parameters import PatchDatabaseCredentialDetailsParameters
from .resources import api
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
    code = 200
    if request.method == 'POST':
        if form.validate_on_submit():
            if not current_user.is_admin and not current_user.is_internal:
                if current_user != form.data['owner']:
                    code = 403
                    return jsonify(status='error', message="You can't create Database Credentials for other users"), code
            code = 201
            data = form.data
            databaseCredential = DatabaseCredential(**data)
            db.session.add(databaseCredential)
        else:
            return jsonify(status='error', errors=form.errors), code
    if current_user:
        if current_user.is_admin and not current_user.is_internal:
            paginator = DatabaseCredential.query.filter(*(DatabaseCredential.owner_id != i.id for i in User.query.filter(User.internal == True).all())).paginate(page, perPage, error_out=False)
        elif current_user.is_internal:
            paginator = DatabaseCredential.query.paginate(page, perPage, error_out=False)
        else:
            paginator = current_user.database_credentials.paginate(page, perPage, error_out=False)
    else:  # pragma: no cover
        paginator = current_user.database_credentials.paginate(page, perPage, error_out=False)
    table = DatabaseCredentialTable(paginator.items, current_user=current_user)
    form = DatabaseCredentialForm()
    return render_template('database_credentials.html', database_credentialsTable=table, database_credentialsForm=form, paginator=paginator, perPage=perPage), code

@DatabaseCredentialsBlueprint.route('/database_credentials/<DatabaseCredential:database_credential>/', methods=['GET', 'POST'])
@login_required
@verifyEditable('database_credential')
def editDatabaseCredential(database_credential):
    code = 200
    form = DatabaseCredentialForm(obj=database_credential)
    if request.method == 'POST':
        if form.validate_on_submit():
            itemsToUpdate = []
            for item in PatchDatabaseCredentialDetailsParameters.fields:
                if getattr(form, item, None) is not None and getattr(database_credential, item) != getattr(form, item).data:
                    itemsToUpdate.append({'op': 'replace', 'path': f'/{item}', 'value': getattr(form, item).data})
            if itemsToUpdate:
                for item in itemsToUpdate:
                    PatchDatabaseCredentialDetailsParameters().validate_patch_structure(item)
                try:
                    with api.commit_or_abort(db.session, default_error_message='Failed to update Database Credentials details.'):
                        PatchDatabaseCredentialDetailsParameters.perform_patch(itemsToUpdate, database_credential)
                        db.session.merge(database_credential)
                        code = 202
                        flash(f'Database Credentials {database_credential.app_name!r} saved successfully!', 'success')
                except Exception as error: # pragma: no cover
                    log.exception(error)
                    code = 400
                    flash(f'Failed to update Database Credentials {database_credential.app_name!r}', 'error')
        else:
            code = 422
    return render_template('edit_database_credential.html', database_credential=database_credential, form=form), code