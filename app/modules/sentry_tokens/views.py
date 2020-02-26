import logging, os

import requests
from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from flask_restplus._http import HTTPStatus
from wtforms import BooleanField

from .parameters import PatchSentryTokenDetailsParameters
from ..users.models import User
from ...extensions import db, paginateArgs, verifyEditable

log = logging.getLogger(__name__)
from .models import SentryToken
from .forms import SentryTokenForm
from .tables import SentryTokenTable

sentryTokensBlueprint = Blueprint('sentry_tokens', __name__, template_folder='./templates', static_folder='./static', static_url_path='/sentry_tokens/static/')

@login_required
@sentryTokensBlueprint.route('/sentry_tokens', methods=['GET', 'POST'])
@paginateArgs(SentryToken)
def sentry_tokens(page, perPage):
    form = SentryTokenForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            data = form.data
            # del data['csrf_token']
            sentryToken = SentryToken(**data)
            db.session.add(sentryToken)
        else:
            return jsonify(status='error', errors=form.errors)
    if current_user:
        if current_user.is_admin and not current_user.is_internal:
            paginator = SentryToken.query.filter(*(SentryToken.owner_id!=i.id for i in User.query.filter(User.internal==True).all())).paginate(page, perPage, error_out=False)
        elif current_user.is_internal:
            paginator = SentryToken.query.paginate(page, perPage, error_out=False)
    else:
        paginator = current_user.sentry_tokens.paginate(page, perPage, error_out=False)
    table = SentryTokenTable(paginator.items, current_user=current_user)
    form = SentryTokenForm()
    return render_template('sentry_tokens.html', sentry_tokensTable=table, sentry_tokensForm=form, paginator=paginator, route='sentry_tokens.sentry_tokens', perPage=perPage)

@login_required
@sentryTokensBlueprint.route('/sentry_tokens/<SentryToken:sentry_token>/', methods=['GET', 'POST'])
@verifyEditable('sentry_token')
def editSentryToken(sentry_token):
    form = SentryTokenForm(obj=sentry_token)
    if request.method == 'POST':
        if form.validate_on_submit():
            itemsToUpdate = []
            for item in PatchSentryTokenDetailsParameters.fields:
                if getattr(form, item, None) is not None:
                    if not isinstance(getattr(form, item), BooleanField):
                        if getattr(form, item).data:
                            if getattr(sentry_token, item) != getattr(form, item).data:
                                itemsToUpdate.append({"op": "replace", "path": f'/{item}', "value": getattr(form, item).data})
                    else:
                        if getattr(sentry_token, item) != getattr(form, item).data:
                            itemsToUpdate.append({"op": "replace", "path": f'/{item}', "value": getattr(form, item).data})
            if itemsToUpdate:
                response = requests.patch(f'{request.host_url}api/v1/sentry_tokens/{sentry_token.id}', json=itemsToUpdate, headers={'Cookie': request.headers['Cookie'], 'Content-Type': 'application/json'})
                if response.status_code == 200:
                    flash(f'Sentry Token {sentry_token.app_name!r} saved successfully!', 'success')
                else:
                    flash(f'Failed to update Sentry Token {sentry_token.app_name!r}', 'error')
        else:
            return jsonify(status='error', errors=form.errors)
    return render_template('edit_sentry_token.html', sentry_token=sentry_token, form=form)
