import json
import logging

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_
from unflatten import unflatten

from ...extensions import ModelForm, db, paginate_args, requires_admin, verify_editable
from ...extensions.api import abort
from .. import get_model
from ..api_tokens.forms import ApiTokenForm
from ..api_tokens.models import ApiToken
from ..api_tokens.views import ApiTokenTable
from ..bots.forms import BotForm
from ..bots.models import Bot
from ..bots.tables import BotTable
from ..database_credentials.forms import DatabaseCredentialForm
from ..database_credentials.models import DatabaseCredential
from ..database_credentials.tables import DatabaseCredentialTable
from ..reddit_apps.forms import RedditAppForm
from ..reddit_apps.models import RedditApp
from ..reddit_apps.tables import RedditAppTable
from ..refresh_tokens.forms import RefreshTokenForm
from ..refresh_tokens.models import RefreshToken
from ..refresh_tokens.views import RefreshTokenTable
from ..sentry_tokens.forms import SentryTokenForm
from ..sentry_tokens.models import SentryToken
from ..sentry_tokens.tables import SentryTokenTable
from ..user_verifications.forms import UserVerificationForm
from ..user_verifications.models import UserVerification
from ..user_verifications.views import UserVerificationTable
from .forms import EditUserForm, UserForm
from .models import User
from .parameters import PatchUserDetailsParameters
from .resources import api
from .tables import UserTable

log = logging.getLogger(__name__)

users_blueprint = Blueprint(
    "users",
    __name__,
    template_folder="./templates",
    static_folder="./static",
    static_url_path="/users/static/",
)


@users_blueprint.route("/users", methods=["GET", "POST"])
@login_required
@requires_admin
@paginate_args(User)
def users(page, per_page, order_by, sort_columns, sort_directions):
    form = UserForm()
    code = 200
    if request.method == "POST":
        if form.validate_on_submit():
            data = {key: value for key, value in form.data.items() if value is not None}
            if "default_settings" in request.form:
                data["default_settings"] = {
                    item["key"]: item["value"] for item in json.loads(request.form["default_settings"])
                }
            user = User(**data)
            user.created_by = current_user.id
            user.updated_by = current_user.id
            with api.commit_or_abort(db.session, default_error_message="Failed to create a new User."):
                db.session.add(user)
            code = 201
        else:
            # code = 422
            return jsonify(status="error", errors=form.errors), code

    if not order_by:
        order_by = [User.id.asc()]
    if current_user.is_internal:
        query = User.query
    elif current_user.is_admin:
        query = User.query.filter_by(internal=current_user.is_internal)
    else:
        query = User.query.filter_by(id=current_user.id)
    for column in sort_columns:
        if get_model(column):
            query = query.outerjoin(get_model(column))
    paginator = query.order_by(*order_by).paginate(page, per_page, error_out=False)
    table = UserTable(paginator.items, sort_columns=sort_columns, sort_directions=sort_directions)
    return (
        render_template(
            "users.html",
            users_table=table,
            users_form=form,
            paginator=paginator,
            route="users.users",
            per_page=per_page,
        ),
        code,
    )


@users_blueprint.route("/u/<User:user>/", methods=["GET", "POST"])
@users_blueprint.route("/profile", methods=["GET", "POST"], defaults={"user": current_user})
@login_required
@verify_editable("user")
def edit_user(user):
    kwargs = {}
    show_old = request.args.get("show_old", "False") == "True"

    items = {
        "bots": "Bot",
        "reddit_apps": "RedditApp",
        "sentry_tokens": "SentryToken",
        "database_credentials": "DatabaseCredential",
        "api_tokens": "ApiToken",
        "refresh_tokens": "RefreshToken",
        "user_verifications": "UserVerification",
    }
    for item, model_name in items.items():
        locals()[item] = getattr(user, item).all()
        kwargs[f"{item}_table"] = globals()[f"{model_name}Table"](
            locals()[item],
            allow_sort=False,
            route_kwargs=dict(
                endpoint="users.edit_user",
                user=user,
                item=item,
                _anchor=item,
            ),
        )
        kwargs[f"{item}_form"] = globals()[f"{model_name}Form"]()

    form = EditUserForm(obj=user)
    new_username = None
    new_default_settings = user.default_settings
    code = 200
    if request.method == "POST":
        if form.validate_on_submit():
            items_to_update = []
            unflattened_form = unflatten(
                dict(
                    [
                        (
                            a.replace("[Setting]", ".setting").replace("[Default Value]", ".value"),
                            b,
                        )
                        for a, b in dict(request.form).items()
                        if a.startswith("root")
                    ]
                )
            )
            default_settings = {}
            if "root" in unflattened_form:
                default_settings = {item["setting"]: item["value"] for item in unflattened_form["root"]}
            if user.default_settings != default_settings:
                items_to_update.append(
                    {
                        "op": "replace",
                        "path": f"/default_settings",
                        "value": default_settings,
                    }
                )
                new_default_settings = default_settings
            else:
                new_default_settings = user.default_settings
            for item in PatchUserDetailsParameters.fields:
                if getattr(form, item, None) is not None and getattr(user, item) != getattr(form, item).data:
                    if item == "username":
                        new_username = getattr(form, item).data
                    if item == "password" and not form.update_password.data:
                        continue
                    items_to_update.append(
                        {
                            "op": "replace",
                            "path": f"/{item}",
                            "value": getattr(form, item).data,
                        }
                    )
            if items_to_update:
                for item in items_to_update:
                    PatchUserDetailsParameters().validate_patch_structure(item)
                try:
                    with api.commit_or_abort(
                        db.session,
                        default_error_message="Failed to update User details.",
                    ):
                        PatchUserDetailsParameters.perform_patch(items_to_update, user)
                        db.session.merge(user)
                        code = 202
                        flash(f"User {user.username!r} saved successfully!", "success")
                except Exception as error:
                    log.exception(error)
                    code = 400
                    flash(f"Failed to update User {user.username!r}", "error")
            if new_username:
                if request.path == "/profile":
                    new_path = "/profile"
                else:
                    new_path = f"{new_username}"
                return redirect(new_path), 202
        else:
            code = 422
    for key, value in kwargs.items():
        if isinstance(value, ModelForm):
            if "owner" in value:
                value.owner.data = user or current_user
            for default_setting, setting_value in user.default_settings.items():
                if default_setting in value.data:
                    getattr(value, default_setting).data = setting_value
    return (
        render_template(
            "edit_user.html",
            user=user,
            users_form=form,
            enable_tablesorter=True,
            default_settings=json.dumps(
                [{"Setting": key, "Default Value": value} for key, value in new_default_settings.items()]
            ),
            show_old=show_old,
            **kwargs,
        ),
        code,
    )


# noinspection PyUnresolvedReferences
@users_blueprint.route("/u/<User:user>/<item>/", methods=["GET", "POST"])
@users_blueprint.route("/profile/<item>/", methods=["GET", "POST"], defaults={"user": current_user})
@login_required
def items_per_user(user, item):
    valid_items = {
        "bots": [BotTable, BotForm, Bot],
        "reddit_apps": [RedditAppTable, RedditAppForm, RedditApp],
        "sentry_tokens": [SentryTokenTable, SentryTokenForm, SentryToken],
        "database_credentials": [
            DatabaseCredentialTable,
            DatabaseCredentialForm,
            DatabaseCredential,
        ],
        "api_tokens": [ApiTokenTable, ApiTokenForm, ApiToken],
        "refresh_tokens": [RefreshTokenTable, RefreshTokenForm, RefreshToken],
        "user_verifications": [
            UserVerificationTable,
            UserVerificationForm,
            UserVerification,
        ],
    }
    item = item.lower()
    if not item in valid_items:
        abort(404)
    items = getattr(user, item).all()

    table = valid_items[item][0](items, allow_sort=False)
    Model = valid_items[item][2]
    form = valid_items[item][1]()
    code = 200
    if request.method == "POST":
        if form.validate_on_submit():
            data = {key: value for key, value in form.data.items() if value is not None}
            if data.get("create_sentry_app", None) is not None:  # pragma: no cover
                if data.get("sentry_organization", None) and data.get("sentry_team", None):
                    requestor = SentryRequestor(current_user.sentry_auth_token)
                    response = requestor.post(
                        f"/api/0/teams/{data['sentry_organization']}/{data['sentry_team']}/projects/",
                        item_name="project",
                        json={"name": data["app_name"]},
                    )
                    if hasattr(response, "slug"):
                        keys = requestor.get(
                            f"/api/0/projects/{data['sentry_organization']}/{response.slug}/keys/",
                            item_name="key",
                        )
                        sentrydsn = keys[0].dsn.public
                        if data["sentry_platform"]:
                            requestor.put(
                                f"/api/0/projects/{data['sentry_organization']}/{response.slug}/",
                                item_name="project",
                                json={"platform": data["sentry_platform"]},
                            )
                        data["dsn"] = sentrydsn
                    else:
                        code = 400
                        return (
                            jsonify(status="error", message="Failed to create Sentry token"),
                            code,
                        )
                data.pop("create_sentry_app")
                data.pop("sentry_organization")
                data.pop("sentry_team")
                data.pop("sentry_platform")
            if item == "api_tokens":
                length = int(data["length"])
            model = Model(owner_id=data["owner"].id, **data)
            if item == "api_tokens":
                model.token = model.generate_token(length)
            with api.commit_or_abort(
                db.session,
                default_error_message=f"Failed to create a new {' '.join(item[:-1].split('_')).title()}.",
            ):
                db.session.add(model)
            items = getattr(user, item).all()
            table = valid_items[item][0](items)
            code = 201
        else:
            code = 422
            return jsonify(status="error", errors=form.errors), code
    kwargs = {
        f"{item}_table": table,
        f"{item}_form": form,
    }
    return (
        render_template(f"{item}.html", enable_tablesorter=True, user=user, **kwargs),
        code,
    )
