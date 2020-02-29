import logging

import requests
from flask import Blueprint, request, render_template, jsonify, flash
from flask_login import current_user, login_required
from wtforms import BooleanField

from .forms import ApiTokenForm, EditApiTokenForm
from .models import ApiToken
from .parameters import PatchApiTokenDetailsParameters
from .tables import ApiTokenTable
from ..users.models import User
from ...extensions import db, paginateArgs, verifyEditable

log = logging.getLogger(__name__)

apiTokensBlueprint = Blueprint('api_tokens', __name__, template_folder='./templates', static_folder='./static', static_url_path='/api_tokens/static/')


@apiTokensBlueprint.route('/api_tokens', methods=['GET', 'POST'])
@login_required
@paginateArgs(ApiToken)
def api_tokens(page=1, perPage=10):
    form = ApiTokenForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            data = form.data
            length = int(data['length'])
            # del data['csrf_token']
            del data['length']
            apiToken = ApiToken(**data)
            apiToken.generate_token(length)
            db.session.add(apiToken)
        else:
            return jsonify(status='error', errors=form.errors)
    if current_user.is_admin and not current_user.is_internal:
        paginator = ApiToken.query.filter(*(ApiToken.owner_id!=i.id for i in User.query.filter(User.internal==True).all())).paginate(page, perPage, error_out=False)
    elif current_user.is_internal:
        paginator = ApiToken.query.paginate(page, perPage, error_out=False)
    else:
        paginator = current_user.api_tokens.paginate(page, perPage, error_out=False)
    table = ApiTokenTable(paginator.items, current_user=current_user)
    return render_template('api_tokens.html', api_tokensTable=table, api_tokensForm=form, paginator=paginator, route='api_tokens.api_tokens', perPage=perPage)

@apiTokensBlueprint.route('/api_tokens/<ApiToken:api_token>/', methods=['GET', 'POST'])
@login_required
@verifyEditable('api_token')
def editApiToken(api_token):
    form = EditApiTokenForm(obj=api_token)
    if request.method == 'POST':
        if form.validate_on_submit():
            itemsToUpdate = []
            for item in PatchApiTokenDetailsParameters.fields:
                if getattr(form, item, None) is not None:
                    if not isinstance(getattr(form, item), BooleanField):
                        if getattr(form, item).data:
                            if getattr(api_token, item) != getattr(form, item).data:
                                itemsToUpdate.append({"op": "replace", "path": f'/{item}', "value": getattr(form, item).data})
                    else:
                        if getattr(api_token, item) != getattr(form, item).data:
                            itemsToUpdate.append({"op": "replace", "path": f'/{item}', "value": getattr(form, item).data})
            if itemsToUpdate:
                response = requests.patch(f'{request.host_url}api/v1/api_tokens/{api_token.id}', json=itemsToUpdate, headers={'Cookie': request.headers['Cookie'], 'Content-Type': 'application/json'})
                if response.status_code == 200:
                    flash(f'API Token {api_token.name!r} saved successfully!', 'success')
                else:
                    flash(f'Failed to update API Token {api_token.name!r}', 'error')
        # else:
            # return jsonify(status='error', errors=form.errors)
    return render_template('edit_api_token.html', api_token=api_token, form=form)
