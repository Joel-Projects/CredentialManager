import re, requests
from functools import wraps
from flask import session, request, abort
from flask_login import current_user
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

def get_apiauth_object_by_key(key):
    return ApiToken.query.filter_by(key=key).first()

def match_api_keys(key):
    if key is None:
        return False
    api_key = get_apiauth_object_by_key(key)
    if api_key is None:
        return False
    elif api_key.key == key:
        return True
    return False

def apiKey(f):
   @wraps(f)
   def decorated(*args, **kwargs):
      if match_api_keys(request.args.get('key')):
         return f(*args, **kwargs)
      else:
         abort(401)
      return decorated