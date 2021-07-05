import logging

from flask import Blueprint, flash, jsonify, render_template, request
from flask_login import current_user, login_required
from wtforms import BooleanField

from ...extensions import db, paginateArgs, verifyEditable
from .. import getPaginator
from ..users.models import User
from .forms import ApiTokenForm, EditApiTokenForm
from .models import ApiToken
from .parameters import PatchApiTokenDetailsParameters
from .resources import api
from .tables import ApiTokenTable

log = logging.getLogger(__name__)

apiTokensBlueprint = Blueprint(
    "api_tokens",
    __name__,
    template_folder="./templates",
    static_folder="./static",
    static_url_path="/api_tokens/static/",
)


@apiTokensBlueprint.route("/api_tokens", methods=["GET", "POST"])
@login_required
@paginateArgs(ApiToken)
def api_tokens(page, perPage, orderBy, sort_columns, sort_directions):
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
            apiToken = ApiToken(**data)
            db.session.add(apiToken)
        else:
            return jsonify(status="error", errors=form.errors), code
    paginator = getPaginator(ApiToken, page, perPage, orderBy, sort_columns)
    table = ApiTokenTable(
        paginator.items, sort_columns=sort_columns, sort_directions=sort_directions
    )
    return (
        render_template(
            "api_tokens.html",
            api_tokensTable=table,
            api_tokensForm=form,
            paginator=paginator,
            route="api_tokens.api_tokens",
            perPage=perPage,
        ),
        code,
    )


@apiTokensBlueprint.route("/api_tokens/<ApiToken:api_token>/", methods=["GET", "POST"])
@login_required
@verifyEditable("api_token")
def editApiToken(api_token):
    form = EditApiTokenForm(obj=api_token)
    code = 200
    if request.method == "POST":
        if form.validate_on_submit():
            itemsToUpdate = []
            for item in PatchApiTokenDetailsParameters.fields:
                if (
                    getattr(form, item, None) is not None
                    and getattr(api_token, item) != getattr(form, item).data
                ):
                    itemsToUpdate.append(
                        {
                            "op": "replace",
                            "path": f"/{item}",
                            "value": getattr(form, item).data,
                        }
                    )
            if itemsToUpdate:
                for item in itemsToUpdate:
                    PatchApiTokenDetailsParameters().validate_patch_structure(item)
                try:
                    with api.commit_or_abort(
                        db.session,
                        default_error_message="Failed to update API Token details.",
                    ):
                        PatchApiTokenDetailsParameters.perform_patch(
                            itemsToUpdate, api_token
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
