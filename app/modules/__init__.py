from flask_login import current_user


def init_app(app, **kwargs):
    from importlib import import_module

    for module_name in app.config["ENABLED_MODULES"]:
        import_module(f".{module_name}", package=__name__).init_app(app, **kwargs)


def getViewableItems(args, model):
    from flask_login import current_user

    from app.modules.users.models import User

    query = model.query
    if "owner_id" in args:
        query = query.filter(model.owner_id == args["owner_id"])
    else:
        if not (current_user.is_admin or current_user.is_internal):
            query = query.filter(model.owner == current_user)
        elif current_user.is_admin and not current_user.is_internal:
            query = query.filter(model.owner.has(internal=False))
    if hasattr(model, "enabled"):
        query = query.filter(model.enabled == True)
    return query


def get_model(item):
    from .api_tokens.models import ApiToken
    from .bots.models import Bot
    from .database_credentials.models import DatabaseCredential
    from .reddit_apps.models import RedditApp
    from .refresh_tokens.models import RefreshToken
    from .sentry_tokens.models import SentryToken
    from .user_verifications.models import UserVerification
    from .users.models import User

    return {
        "api_token": ApiToken,
        "api_tokens": ApiToken,
        "bot": Bot,
        "bots": Bot,
        "database_credential": DatabaseCredential,
        "database_credentials": DatabaseCredential,
        "owner": User,
        "reddit_app": RedditApp,
        "reddit_apps": RedditApp,
        "refresh_tokens": RefreshToken,
        "sentry_token": SentryToken,
        "sentry_tokens": SentryToken,
        "user_verifications": UserVerification,
    }.get(item, None)


def getPaginator(model, page, perPage, orderBy, order_by_raw):
    if current_user.is_internal:
        query = model.query
    elif current_user.is_admin:
        query = model.query.filter(model.owner.has(internal=False))
    else:
        query = getattr(current_user, model.__tablename__)

    for column in order_by_raw:
        if column in get_model(column):
            query = query.outerjoin(get_model(column))
    if not orderBy:
        orderBy = [getattr(model, model._nameAttr).asc()]
    return query.order_by(*orderBy).paginate(page, perPage, error_out=False)
