import logging, os

from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user, login_required
from flask_restplus._http import HTTPStatus

log = logging.getLogger(__name__)
from .models import SentryToken
from .forms import SentryTokenForm
from .tables import SentryTokenTable

sentryTokensBlueprint = Blueprint('sentry_tokens', __name__, template_folder='./templates', static_folder='./static', static_url_path='/sentry_tokens/static/')

@login_required
@sentryTokensBlueprint.route('/sentry_tokens')
def sentry_tokens():
    if current_user.is_admin or current_user.is_internal:
        sentry_tokens = SentryToken.query.all()
    else:
        sentry_tokens = current_user.sentry_tokens.all()
    table = SentryTokenTable(sentry_tokens, current_user=current_user)
    form = SentryTokenForm()
    return render_template('sentry_tokens.html', table=table, form=form)
