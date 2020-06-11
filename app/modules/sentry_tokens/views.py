import logging
from datetime import datetime, timezone

import requests
from flask import Blueprint, flash, jsonify, redirect, render_template, request
from flask_login import current_user, login_required

import app
from config import BaseConfig
from .parameters import PatchSentryTokenDetailsParameters
from .resources import api
from .sentryRequestor import SentryRequestor
from ...extensions import db, paginateArgs, verifyEditable


log = logging.getLogger(__name__)
from .models import SentryToken
from .forms import EditSentryTokenForm, CreateSentryTokenForm
from .tables import SentryTokenTable


sentryTokensBlueprint = Blueprint('sentry_tokens', __name__, template_folder='./templates', static_folder='./static', static_url_path='/sentry_tokens/static/',
    url_prefix='/sentry_tokens')

@sentryTokensBlueprint.route('/', methods=['GET', 'POST'])
@login_required
@paginateArgs(SentryToken)
def sentry_tokens(page, perPage):
    code = 200
    form = CreateSentryTokenForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if not current_user.is_admin and not current_user.is_internal:
                if current_user != form.data['owner']:
                    code = 403
                    return jsonify(status='error', message="You can't create Sentry Tokens for other users"), code
            if form.create_sentry_app.data:
                requestor = SentryRequestor('current_user.sentry_auth_token')
                if form.sentry_organization.data and form.sentry_team.data:
                    response = requestor.post(f'/api/0/teams/{form.sentry_organization.data}/{form.sentry_team.data}/projects/', form.app_name.data)
                    if 'error' in response.json():
                        code = 400
                        return jsonify(status='error', message='Failed to create Sentry token'), code

            code = 201
            data = {key: value for key, value in form.data.items() if value is not None}
            sentryToken = SentryToken(**data)
            db.session.add(sentryToken)
        else:
            return jsonify(status='error', errors=form.errors)
    paginator = current_user.sentry_tokens.paginate(page, perPage, error_out=False)
    if current_user:
        if current_user.is_admin and not current_user.is_internal:
            paginator = SentryToken.query.filter(SentryToken.owner.has(internal=False)).paginate(page, perPage, error_out=False)
        elif current_user.is_internal:
            paginator = SentryToken.query.paginate(page, perPage, error_out=False)
    table = SentryTokenTable(paginator.items, current_user=current_user)
    return render_template('sentry_tokens.html', sentry_tokensTable=table, sentry_tokensForm=form, paginator=paginator, route='sentry_tokens.sentry_tokens', perPage=perPage), code

@sentryTokensBlueprint.route('/<SentryToken:sentry_token>/', methods=['GET', 'POST'])
@login_required
@verifyEditable('sentry_token')
def editSentryToken(sentry_token):
    form = EditSentryTokenForm(obj=sentry_token)
    code = 200
    if request.method == 'POST':
        if form.validate_on_submit():
            itemsToUpdate = []
            for item in PatchSentryTokenDetailsParameters.fields:
                if getattr(form, item, None) is not None and getattr(sentry_token, item) != getattr(form, item).data:
                    itemsToUpdate.append({'op': 'replace', 'path': f'/{item}', 'value': getattr(form, item).data})
            if itemsToUpdate:
                for item in itemsToUpdate:
                    PatchSentryTokenDetailsParameters().validate_patch_structure(item)
                try:
                    with api.commit_or_abort(db.session, default_error_message='Failed to update Sentry Token details.'):
                        PatchSentryTokenDetailsParameters.perform_patch(itemsToUpdate, sentry_token)
                        db.session.merge(sentry_token)
                        code = 202
                        flash(f'Sentry Token {sentry_token.app_name!r} saved successfully!', 'success')
                except Exception as error:  # pragma: no cover
                    log.exception(error)
                    code = 400
                    flash(f'Failed to update Sentry Token {sentry_token.app_name!r}', 'error')
        else:
            code = 422
    return render_template('edit_sentry_token.html', sentry_token=sentry_token, form=form), code
#
# @sentryTokensBlueprint.route('/setup')
# def sentry_callback():
#     code = request.args.get('code')
#     installationId = request.args.get('installationId')
#
#     url = f'https://sentry.jesassn.org/api/0/sentry-app-installations/{installationId}/authorizations/'
#
#     payload = {
#         'grant_type': 'authorization_code',
#         'code': code,
#         'client_id': BaseConfig.SENTRY_INTEGRATION_CLIENT_ID,
#         'client_secret': BaseConfig.SENTRY_INTEGRATION_CLIENT_SECRET
#     }
#     response = requests.post(url, json=payload)
#     data = response.json()
#
#     token = data['token']
#     refresh_token = data['refreshToken']
#     data.pop('scopes')
#     data['expiresAt'] = datetime.fromisoformat(data['expiresAt'].strip('Z')).replace(tzinfo=timezone.utc).astimezone()
#     data['dateCreated'] = datetime.fromisoformat(data['dateCreated'].strip('Z')).replace(tzinfo=timezone.utc).astimezone()
#     data['installationId'] = installationId
#     requestor = SentryRequestor(token)
#     organizations = requestor.get('/api/0/organizations/')
#     with api.commit_or_abort(db.session, default_error_message='Failed to update Sentry Token details.'):
#         sentryInstanceToken = SentryRefreshToken(**data)
#         db.session.merge(sentryInstanceToken)
#     sentryInstanceToken._refresh('https://sentry.jesassn.org')
#     return redirect('https://sentry.jesassn.org/settings/')
#
# @sentryTokensBlueprint.route('/webhook', methods=['POST'])
# def sentry_webhook():
#     code = request.args.get('code')
#     install_id = request.args.get('installationId')
#
#     url = f'https://sentry.jesassn.org/api/0/sentry-app-installations/{install_id}/authorizations/'
#
#     payload = {
#         'grant_type': 'authorization_code',
#         'code': code,
#         'client_id': '507804f7282640068261600cc37e76b7a6b8ed5d64a3442fba06c859656f26e0',
#         'client_secret': 'a86a514e90b3432b88a2a19321cf38a6bd944ec7c318475498706e981bb092cb',
#     }
#
#     response = requests.post(url, json=payload)
#     data = response.json()
#
#     token = data['token']
#     refresh_token = data['refreshToken']
#     with api.commit_or_abort(db.session, default_error_message='Failed to update Sentry Token details.'):
#         sentryInstanceToken = SentryRefreshToken(**data)
#         db.session.merge(sentryInstanceToken)
#
#     return redirect('https://sentry.jesassn.org/settings/')