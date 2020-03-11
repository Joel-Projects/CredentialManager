from functools import wraps
from flask import request
from flask_login import current_user

from app.extensions.api import abort
from app.modules.users.models import User


def paginateArgs(model):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            page = request.args.get('page', 1, int)
            perPage = request.args.get('perPage', 10, int)
            if perPage == 0:
                perPage = model.query.count()
            kwargs['page'] = page
            kwargs['perPage'] = perPage
            return func(*args, **kwargs)
        return wrapper
    return decorator

def requiresAdmin(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if current_user and (current_user.is_admin or current_user.is_internal):
            return func(*args, **kwargs)
        abort(403)
    return decorated

def verifyEditable(kwargName):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            currentObject = kwargs[kwargName]
            if current_user and (current_user.is_admin or current_user.is_internal or currentObject.check_owner(current_user)):
                if isinstance(currentObject, User):
                    if currentObject.is_internal and not current_user.is_internal:
                        abort(403)
                elif current_user.is_internal != currentObject.owner.is_internal:
                    abort(403)
            else:
                abort(403)
            return func(*args, **kwargs)
        return wrapper
    return decorator