import logging

from flask import Blueprint, request, render_template, flash, jsonify
from flask_login import current_user, login_required
from wtforms import BooleanField

from .parameters import PatchSentryTokenDetailsParameters
from .resources import api
from ..users.models import User
from ...extensions import db, paginateArgs, verifyEditable

log = logging.getLogger(__name__)
from .models import SentryToken
from .forms import SentryTokenForm
from .tables import SentryTokenTable

sentryTokensBlueprint = Blueprint('sentry_tokens', __name__, template_folder='./templates', static_folder='./static', static_url_path='/sentry_tokens/static/')

@sentryTokensBlueprint.route('/sentry_tokens', methods=['GET', 'POST'])
@login_required
@paginateArgs(SentryToken)
def sentry_tokens(page, perPage):
    form = SentryTokenForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            data = form.data
            sentryToken = SentryToken(**data)
            db.session.add(sentryToken)
        else:
            return jsonify(status='error', errors=form.errors)
    paginator = current_user.sentry_tokens.paginate(page, perPage, error_out=False)
    if current_user:
        if current_user.is_admin and not current_user.is_internal:
            paginator = SentryToken.query.filter(*(SentryToken.owner_id!=i.id for i in User.query.filter(User.internal==True).all())).paginate(page, perPage, error_out=False)
        elif current_user.is_internal:
            paginator = SentryToken.query.paginate(page, perPage, error_out=False)
    table = SentryTokenTable(paginator.items, current_user=current_user)
    form = SentryTokenForm()
    return render_template('sentry_tokens.html', sentry_tokensTable=table, sentry_tokensForm=form, paginator=paginator, route='sentry_tokens.sentry_tokens', perPage=perPage)

@sentryTokensBlueprint.route('/sentry_tokens/<SentryToken:sentry_token>/', methods=['GET', 'POST'])
@login_required
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
                for item in itemsToUpdate:
                    PatchSentryTokenDetailsParameters().validate_patch_structure(item)
                try:
                    with api.commit_or_abort(db.session, default_error_message="Failed to update Sentry Token details."):
                        PatchSentryTokenDetailsParameters.perform_patch(itemsToUpdate, sentry_token)
                        db.session.merge(sentry_token)
                        flash(f'Sentry Token {sentry_token.app_name!r} saved successfully!', 'success')
                except Exception as error:
                    log.exception(error)
                    flash(f'Failed to update Sentry Token {sentry_token.app_name!r}', 'error')
    return render_template('edit_sentry_token.html', sentry_token=sentry_token, form=form)