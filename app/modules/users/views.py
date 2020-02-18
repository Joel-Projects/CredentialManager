import logging, requests, json
from functools import wraps

from flask import Blueprint, render_template, request, flash, current_app, redirect, jsonify
from flask_login import current_user, login_required
from unflatten import unflatten
from wtforms import BooleanField

from .forms import UserForm, EditUserForm
from .parameters import PatchUserDetailsParameters
from .tables import UserTable
from .models import User
# from ..api_tokens.parameters import PatchApiTokenDetailsParameters
# from ..sentry_tokens.parameters import PatchSentryTokenDetailsParameters
from ...extensions import db, paginateArgs, requiresAdmin, verifyEditable, ModelForm
from ...extensions.api import abort

from ..reddit_apps.tables import RedditAppTable
from ..reddit_apps.forms import RedditAppForm
from ..reddit_apps.models import RedditApp
from ..sentry_tokens.tables import SentryTokenTable
from ..sentry_tokens.forms import SentryTokenForm
from ..sentry_tokens.models import SentryToken
from ..database_credentials.tables import DatabaseCredentialTable
from ..database_credentials.forms import DatabaseCredentialForm
from ..database_credentials.models import DatabaseCredential
from ..bots.tables import BotTable
from ..bots.forms import BotForm
from ..bots.models import Bot
from ..api_tokens.views import ApiTokenTable
from ..api_tokens.forms import ApiTokenForm
from ..api_tokens.models import ApiToken


log = logging.getLogger(__name__)

usersBlueprint = Blueprint('users', __name__, template_folder='./templates', static_folder='./static', static_url_path='/users/static/')

@requiresAdmin
@login_required
@usersBlueprint.route('/users', methods=['GET', 'POST'])
@paginateArgs(User)
def users(page, perPage):
    query = User.query
    form = UserForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            data = form.data
            if 'default_settings' in request.form:
                data['default_settings'] = {item['Setting']: item['Default Value'] for item in json.loads(request.form['default_settings'])}
            # default_settings
            # del data['csrf_token']
            user = User(**data)
            user.created_by = current_user.id
            user.updated_by = current_user.id
            db.session.add(user)
        else:
            return jsonify(status='error', errors=form.errors)
    if current_user:
        if current_user.is_internal:
            paginator = query.paginate(page, perPage, error_out=False)
        elif current_user.is_admin:
            paginator = query.filter_by(internal=False).paginate(page, perPage, error_out=False)
    table = UserTable(paginator.items, current_user, 'username')
    return render_template('users.html', usersTable=table, usersForm=form, paginator=paginator, route='users.users', perPage=perPage)

@usersBlueprint.route('/u/<User:user>/', methods=['GET', 'POST'])
@login_required
@verifyEditable('user')
def editUser(user):
    kwargs = {}

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

    form = EditUserForm(obj=user)
    usernameChanged = False
    newDefaultSettings = user.default_settings
    if request.method == 'POST':
        if form.validate_on_submit():
            itemsToUpdate = []
            defaultSettings = {item['setting']: item['value'] for item in unflatten(dict([(a.replace('[Setting]', '.setting').replace('[Default Value]', '.value'), b) for a, b in dict(request.form).items() if a.startswith('root')]))['root']}
            if user.default_settings != defaultSettings:
                itemsToUpdate.append({"op": "replace", "path": f'/default_settings', "value": defaultSettings})
                newDefaultSettings = defaultSettings
            else:
                newDefaultSettings = user.default_settings
            for item in PatchUserDetailsParameters.getPatchFields():
                if getattr(form, item, None) is not None:
                    if not isinstance(getattr(form, item), BooleanField):
                        if getattr(form, item).data:
                            if getattr(user, item) != getattr(form, item).data:
                                if item == 'username':
                                    usernameChanged = True
                                    newUsername = getattr(form, item).data
                                if item == 'password':
                                    if not form.updatePassword.data:
                                        continue
                                itemsToUpdate.append({"op": "replace", "path": f'/{item}', "value": getattr(form, item).data})
                    else:
                        if getattr(user, item) != getattr(form, item).data:
                            itemsToUpdate.append({"op": "replace", "path": f'/{item}', "value": getattr(form, item).data})
            if itemsToUpdate:
                response = requests.patch(f'{request.host_url}api/v1/users/{user.id}', json=itemsToUpdate, headers={'Cookie': request.headers['Cookie'], 'Content-Type': 'application/json'})
                if response.status_code == 200:
                    flash(f'User {user.username!r} saved successfully!', 'success')
                else:
                    flash(f'Failed to update user {user.username!r}', 'error')
            if usernameChanged:
                # noinspection PyUnboundLocalVariable
                return redirect(f'{newUsername}')
        else:
            return jsonify(status='error', errors=form.errors)
    for key, value in kwargs.items():
        if isinstance(value, ModelForm):
            if 'owner' in value:
                value.owner.data = user or current_user
            for defaultSetting, settingValue in user.default_settings.items():
                if defaultSetting in value.data:
                    getattr(value, defaultSetting).data = settingValue
    return render_template('edit_user.html', user=user, usersForm=form, defaultSettings=json.dumps([{"Setting": key,"Default Value": value} for key, value in newDefaultSettings.items()]), **kwargs)


# noinspection PyUnresolvedReferences
@login_required
@usersBlueprint.route('/u/<User:user>/<item>/', methods=['GET', 'POST'])
def itemsPerUser(user, item):
    validItems = {
        'bots': [BotTable, BotForm, Bot, []],
        'reddit_apps': [RedditAppTable, RedditAppForm, RedditApp, []],
        'sentry_tokens': [SentryTokenTable, SentryTokenForm, SentryToken, []],
        'database_credentials': [DatabaseCredentialTable, DatabaseCredentialForm, DatabaseCredential, []],
        'api_tokens': [ApiTokenTable, ApiTokenForm, ApiToken, ['length']]
    }
    item = item.lower()
    if not item in validItems:
        abort(404)
    items = getattr(user, item).all()
    table = validItems[item][0](items, current_user=current_user)
    Model = validItems[item][2]
    form = validItems[item][1]()
    if request.method == 'POST':
        if form.validate_on_submit():
            data = form.data
            if item == 'api_tokens':
                length = int(data['length'])
            # del data['csrf_token']
            for delAttr in validItems[item][3]:
                del data[delAttr]
            model = Model(owner_id = data['owner'].id, **data)
            if item == 'api_tokens':
                model.generate_token(length)
            db.session.add(model)
            items = getattr(user, item).all()
            table = validItems[item][0](items, current_user=current_user)
        else:
            return jsonify(status='error', errors=form.errors)
    kwargs = {
        f'{item}Table': table,
        f'{item}Form': form,
    }
    # for key, value in kwargs:
    #     if isinstance(value, )
    return render_template(f'{item}.html', user=user, **kwargs)

# @login_required
# @usersBlueprint.route('/u/<User:user>/<item>/<int:item_id>', methods=['GET', 'POST'])
# @verifyEditable('user')
# def editItemsPerUser(user, item, item_id):
#     validItems = {
#         'api_tokens': [PatchApiTokenDetailsParameters, ApiToken, ApiTokenForm, ['length']],
#         'bots': [None, None, None, []], 'reddit_apps': [None, None, None, []],
#         'sentry_tokens': [PatchSentryTokenDetailsParameters, SentryToken, SentryTokenForm, []],
#         'database_credentials': [None, None, None, []]
#     }
#     item = item.lower()
#     if not item in validItems:
#         abort(404)
#     itemPatchParameters = validItems[item][0]
#     Model = validItems[item][1]
#     model = Model.query.filter(Model.id==item_id).first()
#     if not model:
#         abort(404)
#     form = validItems[item][2](obj=model)
#     if request.method == 'POST':
#         if form.validate_on_submit():
#             itemsToUpdate = []
#             for field in itemPatchParameters.fields:
#                 if getattr(form, field, None) is not None:
#                     if not isinstance(getattr(form, field), BooleanField):
#                         if getattr(form, field).data:
#                             if getattr(model, field) != getattr(form, field).data:
#                                 itemsToUpdate.append({"op": "replace", "path": f'/{field}', "value": getattr(form, field).data})
#                     else:
#                         if getattr(model, field) != getattr(form, field).data:
#                             itemsToUpdate.append({"op": "replace", "path": f'/{field}', "value": getattr(form, field).data})
#             if itemsToUpdate:
#                 response = requests.patch(f'{request.host_url}api/v1/api_tokens/{model.id}', json=itemsToUpdate, headers={'Cookie': request.headers['Cookie'], 'Content-Type': 'application/json'})
#                 if response.status_code == 200:
#                     flash(f'API Token {model.name!r} saved successfully!', 'success')
#                 else:
#                     flash(f'Failed to update API Token {model.name!r}', 'error')
#         else:
#             return jsonify(status='error', errors=form.errors)
#     kwargs = {
#         'form': form,
#         item[:-1]: model
#     }
#     return render_template(f'edit_{item[:-1]}.html', user=user, **kwargs)
