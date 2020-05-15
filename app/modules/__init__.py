def init_app(app, **kwargs):
    from importlib import import_module

    for module_name in app.config['ENABLED_MODULES']:
        import_module(f'.{module_name}', package=__name__).init_app(app, **kwargs)

def getViewableItems(args, model):
    from flask_login import current_user

    from app.modules.users.models import User
    query = model.query
    if 'owner_id' in args:
        query = query.filter(model.owner_id == args['owner_id'])
    else:
        if not (current_user.is_admin or current_user.is_internal):
            query = query.filter(model.owner == current_user)
        elif current_user.is_admin:
            query = query.filter(model.owner.has(internal=False))
    if hasattr(model, 'enabled'):
        query = query.filter(model.enabled==True)
    return query