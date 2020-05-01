import json
import logging

from flask import Blueprint, flash, jsonify, redirect, render_template, request
from flask_login import current_user, login_required
from sqlalchemy import or_
from unflatten import unflatten
from wtforms import BooleanField

from .forms import EditUserForm, UserForm
from .models import User
from .parameters import PatchUserDetailsParameters
from .resources import api
from .tables import UserTable
from ..api_tokens.forms import ApiTokenForm
from ..api_tokens.models import ApiToken
from ..api_tokens.views import ApiTokenTable
from ..bots.forms import BotForm
from ..bots.models import Bot
from ..bots.tables import BotTable
from ..database_credentials.forms import DatabaseCredentialForm
from ..database_credentials.models import DatabaseCredential
from ..database_credentials.tables import DatabaseCredentialTable
from ..reddit_apps.forms import RedditAppForm
from ..reddit_apps.models import RedditApp
from ..reddit_apps.tables import RedditAppTable
from ..refresh_tokens.forms import GenerateRefreshTokenForm
from ..refresh_tokens.models import RefreshToken
from ..refresh_tokens.views import RefreshTokenTable
from ..sentry_tokens.forms import SentryTokenForm
from ..sentry_tokens.models import SentryToken
from ..sentry_tokens.tables import SentryTokenTable
from ..user_verifications.forms import UserVerificationForm
from ..user_verifications.models import UserVerification
from ..user_verifications.views import UserVerificationTable
from ...extensions import ModelForm, db, paginateArgs, requiresAdmin, verifyEditable
from ...extensions.api import abort


log = logging.getLogger(__name__)

usersBlueprint = Blueprint('users', __name__, template_folder='./templates', static_folder='./static', static_url_path='/users/static/')

@usersBlueprint.route('/users', methods=['GET', 'POST'])
@login_required
@requiresAdmin
@paginateArgs(User)
def users(page, perPage):
    query = User.query
    form = UserForm()
    code = 200
    if request.method == 'POST':
        if form.validate_on_submit():
            data = {key: value for key, value in form.data.items() if value is not None}
            if 'default_settings' in request.form:
                data['default_settings'] = {item['key']: item['value'] for item in json.loads(request.form['default_settings'])}
            user = User(**data)
            user.created_by = current_user.id
            user.updated_by = current_user.id
            db.session.add(user)
            code = 201
        else:
            # code = 422
            return jsonify(status='error', errors=form.errors), code
    if current_user.is_internal:
        paginator = query.paginate(page, perPage, error_out=False)
    elif current_user.is_admin:
        paginator = query.filter_by(internal=False).paginate(page, perPage, error_out=False)
    table = UserTable(paginator.items, current_user, endpointAttr='username')
    return render_template('users.html', usersTable=table, usersForm=form, paginator=paginator, route='users.users', perPage=perPage), code

@usersBlueprint.route('/u/<User:user>/', methods=['GET', 'POST'])
@usersBlueprint.route('/profile', methods=['GET', 'POST'], defaults={'user': current_user})
@login_required
@verifyEditable('user')
def editUser(user):
    kwargs = {}
    showOld = request.args.get('showOld', 'False') == 'True'

    bots = user.bots.all()
    kwargs['botsTable'] = BotTable(bots, current_user=current_user)
    kwargs['botsForm'] = BotForm()

    reddit_apps = user.reddit_apps.all()
    kwargs['reddit_appsTable'] = RedditAppTable(reddit_apps, current_user=current_user)
    kwargs['reddit_appsForm'] = RedditAppForm()

    sentry_tokens = user.sentry_tokens.all()
    kwargs['sentry_tokensTable'] = SentryTokenTable(sentry_tokens, current_user=current_user)
    kwargs['sentry_tokensForm'] = SentryTokenForm()

    database_credentials = user.database_credentials.all()
    kwargs['database_credentialsTable'] = DatabaseCredentialTable(database_credentials, current_user=current_user)
    kwargs['database_credentialsForm'] = DatabaseCredentialForm()

    api_tokens = user.api_tokens.all()
    kwargs['api_tokensTable'] = ApiTokenTable(api_tokens, current_user=current_user)
    kwargs['api_tokensForm'] = ApiTokenForm()

    refresh_tokens = user.refresh_tokens.filter(or_(RefreshToken.revoked == False, RefreshToken.revoked == showOld)).all()
    kwargs['refresh_tokensTable'] = RefreshTokenTable(refresh_tokens, current_user=current_user)
    kwargs['refresh_tokensForm'] = GenerateRefreshTokenForm()

    user_verifications = user.user_verifications.all()
    kwargs['user_verificationsTable'] = UserVerificationTable(user_verifications, current_user=current_user)
    kwargs['user_verificationsForm'] = UserVerificationForm()

    form = EditUserForm(obj=user)
    newUsername = None
    newDefaultSettings = user.default_settings
    code = 200
    if request.method == 'POST':
        if form.validate_on_submit():
            itemsToUpdate = []
            unflattenedForm = unflatten(dict([(a.replace('[Setting]', '.setting').replace('[Default Value]', '.value'), b) for a, b in dict(request.form).items() if a.startswith('root')]))
            defaultSettings = {}
            if 'root' in unflattenedForm:
                defaultSettings = {item['setting']: item['value'] for item in unflattenedForm['root']}
            if user.default_settings != defaultSettings:
                itemsToUpdate.append({'op': 'replace', 'path': f'/default_settings', 'value': defaultSettings})
                newDefaultSettings = defaultSettings
            else:
                newDefaultSettings = user.default_settings
            for item in PatchUserDetailsParameters.fields:
                if getattr(form, item, None) is not None and getattr(user, item) != getattr(form, item).data:
                    if item == 'username':
                        newUsername = getattr(form, item).data
                    if item == 'password' and not form.updatePassword.data:
                        continue
                    itemsToUpdate.append({'op': 'replace', 'path': f'/{item}', 'value': getattr(form, item).data})
            if itemsToUpdate:
                for item in itemsToUpdate:
                    PatchUserDetailsParameters().validate_patch_structure(item)
                try:
                    with api.commit_or_abort(db.session, default_error_message='Failed to update User details.'):
                        PatchUserDetailsParameters.perform_patch(itemsToUpdate, user)
                        db.session.merge(user)
                        code = 202
                        flash(f'User {user.username!r} saved successfully!', 'success')
                except Exception as error:
                    log.exception(error)
                    code = 400
                    flash(f'Failed to update User {user.username!r}', 'error')
            if newUsername:
                if request.path == '/profile':
                    newPath = '/profile'
                else:
                    newPath = f'{newUsername}'
                return redirect(newPath), 202
        else:
            code = 422
    for key, value in kwargs.items():
        if isinstance(value, ModelForm):
            if 'owner' in value:
                value.owner.data = user or current_user
            for defaultSetting, settingValue in user.default_settings.items():
                if defaultSetting in value.data:
                    getattr(value, defaultSetting).data = settingValue
    return render_template('edit_user.html', user=user, usersForm=form, defaultSettings=json.dumps([{'Setting': key, 'Default Value': value} for key, value in newDefaultSettings.items()]), showOld=showOld, **kwargs), code

# noinspection PyUnresolvedReferences
@usersBlueprint.route('/u/<User:user>/<item>/', methods=['GET', 'POST'])
@usersBlueprint.route('/profile/<item>/', methods=['GET', 'POST'], defaults={'user': current_user})
@login_required
def itemsPerUser(user, item):
    validItems = {
        'bots': [BotTable, BotForm, Bot],
        'reddit_apps': [RedditAppTable, RedditAppForm, RedditApp],
        'sentry_tokens': [SentryTokenTable, SentryTokenForm, SentryToken],
        'database_credentials': [DatabaseCredentialTable, DatabaseCredentialForm, DatabaseCredential],
        'api_tokens': [ApiTokenTable, ApiTokenForm, ApiToken],
        'refresh_tokens': [RefreshTokenTable, GenerateRefreshTokenForm, RefreshToken],
        'user_verifications': [UserVerificationTable, UserVerificationForm, UserVerification]
    }
    item = item.lower()
    if not item in validItems:
        abort(404)
    items = getattr(user, item).all()
    table = validItems[item][0](items, current_user=current_user)
    Model = validItems[item][2]
    form = validItems[item][1]()
    code = 200
    if request.method == 'POST':
        if form.validate_on_submit():
            data = {key: value for key, value in form.data.items() if value is not None}
            if item == 'api_tokens':
                length = int(data['length'])
            model = Model(owner_id=data['owner'].id, **data)
            if item == 'api_tokens':
                model.token = model.generate_token(length)
            db.session.add(model)
            items = getattr(user, item).all()
            table = validItems[item][0](items, current_user=current_user)
            code = 201
        else:
            code = 422
            return jsonify(status='error', errors=form.errors), code
    kwargs = {
        f'{item}Table': table,
        f'{item}Form': form,
    }
    return render_template(f'{item}.html', user=user, **kwargs), code