from functools import wraps
from flask import request

def paginateArgs(model):
    def actual_decorator(func):
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
    return actual_decorator