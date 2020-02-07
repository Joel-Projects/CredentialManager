import logging, requests, json
from functools import wraps

from flask import Blueprint, render_template, request, flash, current_app, redirect, jsonify
from flask_login import current_user, login_required
from wtforms import BooleanField

from .forms import UserForm, EditUserForm
from .parameters import PatchUserDetailsParameters
from .tables import UserTable
from .models import User
from ...extensions import db, paginateArgs
from ...extensions.api import abort

from ..api_tokens.views import ApiTokenTable
from ..api_tokens.forms import ApiTokenForm
from ..api_tokens.models import ApiToken
from ..sentry_tokens.tables import SentryTokenTable
from ..sentry_tokens.forms import SentryTokenForm
from ..sentry_tokens.models import SentryToken


log = logging.getLogger(__name__)

usersBlueprint = Blueprint('users', __name__, template_folder='./templates', static_folder='./static', static_url_path='/users/static/')

def requiresAdmin(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if current_user and not current_user.is_admin and not current_user.is_internal:
            abort(403)
        return func(*args, **kwargs)
    return decorated

def verifyEditable(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if current_user and not current_user.is_admin and not current_user.is_internal and (current_user.is_internal or (kwargs['user'].is_internal != current_user.is_internal)):
            abort(403)
        return func(*args, **kwargs)
    return decorated

@requiresAdmin
@login_required
@usersBlueprint.route('/users', methods=['GET', 'POST'])
@paginateArgs(User)
def users(page, perPage):
    query = User.query
    users = []
    form = UserForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            data = form.data
            del data['csrf_token']
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
    return render_template('users.html', table=table, form=form, paginator=paginator, route='users.users', perPage=perPage)

@usersBlueprint.route('/u/<User:user>/', methods=['GET', 'POST'])
@login_required
@verifyEditable
def editUser(user):
    # api_tokens = user.api_tokens.all()
    # table = TokenTable(api_tokens, current_user=current_user)
    form = EditUserForm(obj=user)
    usernameChanged = False
    if request.method == 'POST' and form.validate_on_submit():
        itemsToUpdate = []
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
    # else:
        # form.populate_obj(user)
    # form.validate()
    return render_template('edit_user.html', user=user, form=form)


# noinspection PyUnresolvedReferences
@login_required
@usersBlueprint.route('/u/<User:user>/<item>', methods=['GET', 'POST'])
def itemsPerUser(user, item):
    validItems = {'api_tokens': [ApiTokenTable, ApiTokenForm, ApiToken, ['length']], 'bots': [None, None, None, []], 'reddit_apps': [None, None, None, []], 'sentry_tokens': [SentryTokenTable, SentryTokenForm, SentryToken, []], 'database_credentials': [None, None, None, []]}
    item = item.lower()
    if not item in validItems:
        abort(404)
    items = getattr(user, item).all()
    table = validItems[item][0](items, current_user=current_user)
    Model = validItems[item][2]
    form = validItems[item][1]()
    if request.method == 'POST' and form.validate_on_submit():
        data = form.data
        del data['csrf_token']
        for delAttr in validItems[item][3]:
            del data[delAttr]
        model = Model(**data)
        db.session.add(model)
    return render_template(f'{item}.html', user=user, table=table, form=form)
