import logging

from flask import Blueprint, flash, jsonify, render_template, request
from flask_login import current_user, login_required

from ...extensions import db, paginate_args, verify_editable
from .. import get_paginator
from ..users.models import User
from .parameters import PatchDatabaseCredentialDetailsParameters
from .resources import api

log = logging.getLogger(__name__)
from .forms import DatabaseCredentialForm
from .models import DatabaseCredential
from .tables import DatabaseCredentialTable

DatabaseCredentialsBlueprint = Blueprint(
    "database_credentials",
    __name__,
    template_folder="./templates",
    static_folder="./static",
    static_url_path="/database_credentials/static/",
)


@DatabaseCredentialsBlueprint.route("/database_credentials", methods=["GET", "POST"])
@login_required
@paginate_args(DatabaseCredential)
def database_credentials(page, per_page, order_by, sort_columns, sort_directions):
    form = DatabaseCredentialForm()
    code = 200
    if request.method == "POST":
        if form.validate_on_submit():
            if not current_user.is_admin and not current_user.is_internal:
                if current_user != form.data["owner"]:
                    code = 403
                    return (
                        jsonify(
                            status="error",
                            message="You can't create Database Credentials for other users",
                        ),
                        code,
                    )
            code = 201
            data = form.get_db_data()
            database_credential = DatabaseCredential(**data)
            db.session.add(database_credential)
        else:
            return jsonify(status="error", errors=form.errors), code
    paginator = get_paginator(DatabaseCredential, page, per_page, order_by, sort_columns)
    table = DatabaseCredentialTable(paginator.items, sort_columns=sort_columns, sort_directions=sort_directions)
    form = DatabaseCredentialForm()
    return (
        render_template(
            "database_credentials.html",
            database_credentials_table=table,
            database_credentials_form=form,
            paginator=paginator,
            per_page=per_page,
            route="database_credentials.database_credentials",
        ),
        code,
    )


@DatabaseCredentialsBlueprint.route(
    "/database_credentials/<DatabaseCredential:database_credential>/",
    methods=["GET", "POST"],
)
@login_required
@verify_editable("database_credential")
def edit_database_credential(database_credential):
    code = 200
    form = DatabaseCredentialForm(obj=database_credential)
    if request.method == "POST":
        if form.validate_on_submit():
            items_to_update = []
            for item in PatchDatabaseCredentialDetailsParameters.fields:
                if (
                    getattr(form, item, None) is not None
                    and getattr(database_credential, item) != getattr(form, item).data
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
                    PatchDatabaseCredentialDetailsParameters().validate_patch_structure(item)
                try:
                    with api.commit_or_abort(
                        db.session,
                        default_error_message="Failed to update Database Credentials details.",
                    ):
                        PatchDatabaseCredentialDetailsParameters.perform_patch(items_to_update, database_credential)
                        db.session.merge(database_credential)
                        code = 202
                        flash(
                            f"Database Credentials {database_credential.app_name!r} saved successfully!",
                            "success",
                        )
                except Exception as error:  # pragma: no cover
                    log.exception(error)
                    code = 400
                    flash(
                        f"Failed to update Database Credentials {database_credential.app_name!r}",
                        "error",
                    )
        else:
            code = 422
    return (
        render_template(
            "edit_database_credential.html",
            database_credential=database_credential,
            form=form,
        ),
        code,
    )
