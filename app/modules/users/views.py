import logging
from functools import wraps

from flask import Blueprint, render_template
from flask_login import current_user, login_required

from .forms import UserForm
from .tables import UserTable
from ..api_tokens.views import TokenTable
from .models import User
from ...extensions.api import abort

log = logging.getLogger(__name__)

usersBlueprint = Blueprint('users', __name__, template_folder='./templates', static_folder='./app/models/users/static')

def requiresAdmin(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if current_user and not current_user.is_admin and not current_user.is_internal:
            abort(403)
        return func(*args, **kwargs)
    return decorated


@usersBlueprint.route('/users')
@login_required
@requiresAdmin
def users():
    query = User.query
    users = []
    if current_user.is_internal:
        users = query.all()
    elif current_user.is_admin:
        users = [i for i in query.all() if not i.is_internal]
    form = UserForm()
    table = UserTable(users, current_user, 'username')
    return render_template('users.html', users=users, form=form, table=table)

@login_required
@usersBlueprint.route('/u/<User:user>/')
def editUser(user):
    # api_tokens = user.api_tokens.all()
    # table = TokenTable(api_tokens, current_user=current_user)
    return render_template('edit_user.html', user=user)


@login_required
@usersBlueprint.route('/u/<User:user>/api_tokens')
def api_tokensPerUser(user):
    api_tokens = user.api_tokens.all()
    table = TokenTable(api_tokens, current_user=current_user)
    return render_template('api_tokens.html', table=table, user=user)
