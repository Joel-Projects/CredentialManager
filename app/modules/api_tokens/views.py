import logging

from flask import Blueprint, request, render_template, jsonify
from flask_login import current_user, login_required

from .forms import ApiTokenForm
from .models import ApiToken
from .tables import ApiTokenTable
from ...extensions import db, paginateArgs

log = logging.getLogger(__name__)

apiTokensBlueprint = Blueprint('api_tokens', __name__, template_folder='./templates', static_folder='./static', static_url_path='/api_tokens/static/')


@login_required
@apiTokensBlueprint.route('/api_tokens', methods=['GET', 'POST'])
@paginateArgs(ApiToken)
def api_tokens(page=1, perPage=10):
    form = ApiTokenForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            data = form.data
            length = int(data['length'])
            del data['csrf_token']
            del data['length']
            apiToken = ApiToken(**data)
            apiToken.generate_token(length)
            db.session.add(apiToken)
        else:
            return jsonify(status='error', errors=form.errors)
    if current_user and (current_user.is_admin or current_user.is_internal):
        paginator = ApiToken.query.paginate(page, perPage, error_out=False)
    else:
        paginator = current_user.api_tokens.paginate(page, perPage, error_out=False)
    table = ApiTokenTable(paginator.items, current_user=current_user)
    return render_template('api_tokens.html', table=table, form=form, paginator=paginator, route='api_tokens.api_tokens', perPage=perPage)
