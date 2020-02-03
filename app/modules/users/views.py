import logging, requests, json
from functools import wraps

from flask import Blueprint, render_template, request, flash, current_app, redirect
from flask_login import current_user, login_required

from .forms import UserForm, EditUserForm
from .parameters import PatchUserDetailsParameters
from .tables import UserTable
from ..api_tokens.views import TokenTable
from .models import User
from ...extensions import db
from ...extensions.api import abort

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
def users():
    query = User.query
    users = []
    form = UserForm()
    if request.method == 'POST' and form.validate_on_submit():
        data = form.data
        del data['csrf_token']
        user = User(**data)
        db.session.add(user)
    if current_user.is_internal:
        users = query.all()
    elif current_user.is_admin:
        users = [i for i in query.all() if not i.is_internal]
    table = UserTable(users, current_user, 'username')
    return render_template('users.html', users=users, form=form, table=table)

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
        for item in PatchUserDetailsParameters.fields:
            if getattr(form, item).data:
                if getattr(user, item) != getattr(form, item).data:
                    if item == 'username':
                        usernameChanged = True
                        newUsername = getattr(form, item).data
                    itemsToUpdate.append({"op": "replace", "path": f'/{item}', "value": getattr(form, item).data})
        if itemsToUpdate:
            response = requests.patch(f'{request.host_url}api/v1/users/{user.id}', json=itemsToUpdate, headers={'Cookie': request.headers['Cookie'], 'Content-Type': 'application/json'})
            if response.status_code == 200:
                flash(f'User {user.username!r} saved successfully!', 'success')
            else:
                flash(f'Failed to update user {user.username!r}', 'error')
        if usernameChanged:
            return redirect(f'{newUsername}')
    # form.validate()
    return render_template('edit_user.html', user=user, form=form)


@login_required
@usersBlueprint.route('/u/<User:user>/api_tokens')
def api_tokensPerUser(user):
    api_tokens = user.api_tokens.all()
    table = TokenTable(api_tokens, current_user=current_user)
    return render_template('api_tokens.html', table=table, user=user)
