import logging


from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import current_user, login_required

from .forms import ApiTokenForm
from .models import ApiToken
from .tables import TokenTable
from ...extensions import db

log = logging.getLogger(__name__)

apiTokensBlueprint = Blueprint('api_tokens', __name__, template_folder='./templates', static_folder='./static', static_url_path='/api_tokens/static/')


@login_required
@apiTokensBlueprint.route('/api_tokens', methods=['GET', 'POST'])
def api_tokens():

    form = ApiTokenForm()
    if request.method == 'POST' and form.validate_on_submit():
        data = form.data
        length = int(data['length'])
        del data['csrf_token']
        del data['length']
        apiToken = ApiToken(**data)
        apiToken.generate_token(length)
        db.session.add(apiToken)

    if current_user.is_admin or current_user.is_internal:
        api_tokens = ApiToken.query.all()
    else:
        api_tokens = current_user.api_tokens.all()
    table = TokenTable(api_tokens, current_user=current_user)
    return render_template('api_tokens.html', table=table, form=form)
