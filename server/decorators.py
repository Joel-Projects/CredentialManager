import re, requests
from functools import wraps
from flask import session, request, abort
from flask_login import current_user, login_user

from . import items
from .models import User, ApiToken

def validateUser(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        try:
            user = User.query.filter(User.username.ilike(kwargs['user'])).first()
            username = user.username
        except AttributeError:
            username = kwargs['user']
        kwargs['user'] = username
        return func(*args, **kwargs)
    return decorated

def validateUsername(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        try:
            username = request.form.get('username')
            if not 3 <= len(username) <= 22:
                kwargs['reason'] = 'Username must be between 3 and 22 characters'
            elif not re.match(r'^[\w-]+$', username):
                kwargs['reason'] = 'Letters, numbers, dashes, and underscores only. Please try again without symbols.'
            else:
                kwargs['username'] = username
        except Exception as reason:
            kwargs['reason'] = reason
        return func(*args, **kwargs)
    return decorated

def validateUserForm(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if request.form['username'] == session['username']:
            try:
                user = User.query.filter(User.username.ilike(request.form['username'])).first()
                username = user.username
            except AttributeError:
                username = request.form['username']
            kwargs['user'] = username
        else:
            abort(409)
        return func(*args, **kwargs)

    return decorated

def requiresAdmin(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if current_user and not current_user.admin:
            abort(403)
        return func(*args, **kwargs)
    return decorated

def match_api_key(key):
    if key is None:
        return False
    api_key = ApiToken.query.filter_by(token=key).first()
    if api_key is None:
        return False
    elif api_key.token == key:
        return True
    return False

def getApiItem(item_type, id):
    itemModel = items.get(item_type, {}).get('model', None)
    if itemModel:
        item = itemModel.query.filter_by(id=id).first()
    return item

def verifyOwnership(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        apiKey = ApiToken.query.filter_by(token=request.form.to_dict().get('key')).first()
        id = request.form.to_dict().get('id', None)
        item_type = request.form.to_dict().get('item_type', None)
        if getApiItem(item_type, id).owner == apiKey.owner or apiKey.owner.admin:
            return f(*args, **kwargs)
        else:
            return {'status': 'fail', 'message': "You don't have the permission to access the requested resource.", 'name': None}, 403
    return decorated

def apiAccessible(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        validKey = match_api_key(request.form.to_dict().get('key'))

        if validKey or current_user.is_authenticated:
            apiKey = ApiToken.query.filter_by(token=request.form.to_dict().get('key')).first()
            if apiKey:
                login_user(apiKey.owner)
            return f(*args, **kwargs)
        else:
            return {'status': 'fail', 'message': "You don't have the permission to access the requested resource.", 'name': None}, 403
    return decorated