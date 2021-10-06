import logging

from flask import Blueprint, flash, jsonify, render_template, request
from flask_login import current_user, login_required
from wtforms import BooleanField

from ...extensions import db, paginate_args, verify_editable
from .. import get_paginator
from ..users.models import User
from .forms import ApiTokenForm, EditApiTokenForm
from .models import ApiToken
from .parameters import PatchApiTokenDetailsParameters
from .resources import api
from .tables import ApiTokenTable

log = logging.getLogger(__name__)

api_tokens_blueprint = Blueprint(
    "api_tokens",
    __name__,
    template_folder="./templates",
    static_folder="./static",
    static_url_path="/api_tokens/static/",
)


@api_tokens_blueprint.route("/api_tokens", methods=["GET", "POST"])
@login_required
@paginate_args(ApiToken)
def api_tokens(page, per_page, order_by, sort_columns, sort_directions):
    form = ApiTokenForm()
    code = 200
    if request.method == "POST":
        if form.validate_on_submit():
            if not current_user.is_admin and not current_user.is_internal:
                if current_user != form.data["owner"]:
                    code = 403
                    return (
                        jsonify(
                            status="error",
                            message="You can't create API Tokens for other users",
                        ),
                        code,
                    )
            code = 201
            data = {key: value for key, value in form.data.items() if value is not None}
            data["token"] = ApiToken.generate_token(data["length"])
            api_token = ApiToken(**data)
            with api.commit_or_abort(
                db.session, default_error_message="Failed to create API Token."
            ):
                db.session.add(api_token)
        else:
            return jsonify(status="error", errors=form.errors), code
    paginator = get_paginator(ApiToken, page, per_page, order_by, sort_columns)
    table = ApiTokenTable(
        paginator.items, sort_columns=sort_columns, sort_directions=sort_directions
    )
    return (
        render_template(
            "api_tokens.html",
            api_tokens_table=table,
            api_tokens_form=form,
            paginator=paginator,
            route="api_tokens.api_tokens",
            per_page=per_page,
        ),
        code,
    )


@api_tokens_blueprint.route(
    "/api_tokens/<ApiToken:api_token>/", methods=["GET", "POST"]
)
@login_required
@verify_editable("api_token")
def edit_api_token(api_token):
    form = EditApiTokenForm(obj=api_token)
    code = 200
    if request.method == "POST":
        if form.validate_on_submit():
            items_to_update = []
            for item in PatchApiTokenDetailsParameters.fields:
                if (
                    getattr(form, item, None) is not None
                    and getattr(api_token, item) != getattr(form, item).data
                ):
                    items_to_update.append(
                        {
                            "op": "replace",
                            "path": f"/{item}",
                            "value": getattr(form, item).data,
                        }
                    )
            if items_to_update:
                for item in items_to_update:
                    PatchApiTokenDetailsParameters().validate_patch_structure(item)
                try:
                    with api.commit_or_abort(
                        db.session,
                        default_error_message="Failed to update API Token details.",
                    ):
                        PatchApiTokenDetailsParameters.perform_patch(
                            items_to_update, api_token
                        )
                        db.session.merge(api_token)
                        code = 202
                        flash(
                            f"API Token {api_token.name!r} saved successfully!",
                            "success",
                        )
                except Exception as error:  # pragma: no cover
                    log.exception(error)
                    code = 400
                    flash(f"Failed to update API Token {api_token.name!r}", "error")
        else:
            code = 422
    return render_template("edit_api_token.html", api_token=api_token, form=form), code
