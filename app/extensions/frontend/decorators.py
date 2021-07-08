from functools import wraps

from flask import request
from flask_login import current_user

from app.extensions.api import abort
from app.modules.users.models import User


def paginate_args(model):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from ...modules.bots.models import Bot
            from ...modules.database_credentials.models import DatabaseCredential
            from ...modules.reddit_apps.models import RedditApp
            from ...modules.sentry_tokens.models import SentryToken

            page = request.args.get("page", 1, int)
            per_page = request.args.get("per_page", 10, int)
            sort_columns = request.args.get("order_by", type=str)
            kwargs["sort_columns"] = sort_columns.split(",") if sort_columns else []
            sort_directions = request.args.get("direction", type=str)
            kwargs["sort_directions"] = (
                sort_directions.split(",") if sort_directions else []
            )
            nonlocal model
            if model is None:
                from ...modules import get_model

                model = get_model(request.path.strip("/").split("/")[-1])
                per_page = 0
            if per_page == 0:  # pragma: no cover
                per_page = model.query.count()
            kwargs["page"] = page
            kwargs["per_page"] = per_page
            sorts = []
            if request.endpoint == "users.items_per_user":
                del kwargs["page"]
                del kwargs["per_page"]
            for column, direction in zip(
                kwargs["sort_columns"], kwargs["sort_directions"]
            ):
                try:
                    sorts.append(getattr(getattr(model, column), direction)())
                except NotImplementedError:
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
            kwargs["order_by"] = sorts
            return func(*args, **kwargs)

        return wrapper

    return decorator


def requires_admin(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if current_user and (current_user.is_admin or current_user.is_internal):
            return func(*args, **kwargs)
        abort(403)

    return decorated


def verify_editable(kwarg_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_object = kwargs[kwarg_name]
            if current_user and (
                current_user.is_admin
                or current_user.is_internal
                or current_object.check_owner(current_user)
            ):
                if current_object._sa_class_manager.class_ == User:
                    if (
                        current_object.is_internal and not current_user.is_internal
                    ):  # pragma: no cover
                        abort(403)
                elif (
                    current_object.owner.is_internal
                    and current_user.is_internal != current_object.owner.is_internal
                ):
                    abort(403)
            else:
                abort(403)
            return func(*args, **kwargs)

        return wrapper

    return decorator
