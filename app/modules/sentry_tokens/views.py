import logging, os

from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from flask_restplus._http import HTTPStatus

from ...extensions import db, paginateArgs

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
            del data['csrf_token']
            sentryToken = SentryToken(**data)
            db.session.add(sentryToken)
        else:
            return jsonify(status='error', errors=form.errors)
    if current_user.is_admin or current_user.is_internal:
        paginator = SentryToken.query.paginate(page, perPage, error_out=False)
    else:
        paginator = current_user.sentry_tokens.paginate(page, perPage, error_out=False)
    table = SentryTokenTable(paginator.items, current_user=current_user)
    form = SentryTokenForm()
    return render_template('sentry_tokens.html', table=table, form=form, paginator=paginator, route='sentry_tokens.sentry_tokens', perPage=perPage)
