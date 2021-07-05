from functools import wraps

from flask import request
from flask_login import current_user

from app.extensions.api import abort
from app.modules.users.models import User


def paginateArgs(model):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            page = request.args.get("page", 1, int)
            perPage = request.args.get("perPage", 10, int)
            sort_columns = request.args.get("orderBy", type=str)
            kwargs["sort_columns"] = sort_columns.split(",") if sort_columns else []
            sort_directions = request.args.get("direction", type=str)
            kwargs["sort_directions"] = (
                sort_directions.split(",") if sort_directions else []
            )
            if perPage == 0:  # pragma: no cover
                perPage = model.query.count()
            kwargs["page"] = page
            kwargs["perPage"] = perPage
            sorts = []
            for column, direction in zip(
                kwargs["sort_columns"], kwargs["sort_directions"]
            ):
                try:
                    sorts.append(getattr(getattr(model, column), direction)())
                except NotImplementedError:
                    from ...modules.bots.models import Bot
                    from ...modules.database_credentials.models import (
                        DatabaseCredential,
                    )
                    from ...modules.reddit_apps.models import RedditApp
                    from ...modules.sentry_tokens.models import SentryToken

                    mapping = {
                        "owner": getattr(User.username, direction),
                        "bot": getattr(Bot.app_name, direction),
                        "bots": getattr(Bot.app_name, direction),
                        "reddit_app": getattr(RedditApp.app_name, direction),
                        "reddit_apps": getattr(RedditApp.app_name, direction),
                        "database_credential": getattr(
                            DatabaseCredential.app_name, direction
                        ),
                        "database_credentials": getattr(
                            DatabaseCredential.app_name, direction
                        ),
                        "sentry_token": getattr(SentryToken.app_name, direction),
                        "sentry_tokens": getattr(SentryToken.app_name, direction),
                    }
                    sorts.append(mapping[column]())
            kwargs["orderBy"] = sorts
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
            if current_user and (
                current_user.is_admin
                or current_user.is_internal
                or currentObject.check_owner(current_user)
            ):
                if currentObject._sa_class_manager.class_ == User:
                    if (
                        currentObject.is_internal and not current_user.is_internal
                    ):  # pragma: no cover
                        abort(403)
                elif (
                    currentObject.owner.is_internal
                    and current_user.is_internal != currentObject.owner.is_internal
                ):
                    abort(403)
            else:
                abort(403)
            return func(*args, **kwargs)

        return wrapper

    return decorator
