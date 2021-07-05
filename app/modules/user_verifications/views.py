import json
import logging

from flask import Blueprint, flash, jsonify, render_template, request
from flask_login import current_user, login_required

from ...extensions import db, paginateArgs, verifyEditable
from .. import getPaginator
from ..users.models import User
from .forms import UserVerificationForm
from .models import UserVerification
from .parameters import PatchUserVerificationDetailsParameters
from .resources import api
from .tables import UserVerificationTable

log = logging.getLogger(__name__)

userVerificationsBlueprint = Blueprint(
    "user_verifications",
    __name__,
    template_folder="./templates",
    static_folder="./static",
    static_url_path="/user_verifications/static/",
)


@userVerificationsBlueprint.route("/user_verifications", methods=["GET", "POST"])
@login_required
@paginateArgs(UserVerification)
def user_verifications(page, perPage, orderBy, sort_columns, sort_directions):
    code = 200
    form = UserVerificationForm()
    if request.method == "POST":
        if form.validate_on_submit():
            if (
                not current_user.is_admin
                and not current_user.is_internal
                and current_user.id != form.data["owner"].id
            ):
                code = 403
                return (
                    jsonify(
                        status="error",
                        message="You can't create User Verifications for other users",
                    ),
                    code,
                )  # pragma: no cover
            code = 201
            data = {key: value for key, value in form.data.items() if value is not None}
            if "extra_data" in form.data and form.data["extra_data"]:
                data["extra_data"] = json.loads(form.data["extra_data"])

            userVerification = UserVerification(**data)
            db.session.add(userVerification)
        else:
            return jsonify(status="error", errors=form.errors), code
    paginator = getPaginator(UserVerification, page, perPage, orderBy, sort_columns)
    table = UserVerificationTable(
        paginator.items, sort_columns=sort_columns, sort_directions=sort_directions
    )
    form = UserVerificationForm()
    return (
        render_template(
            "user_verifications.html",
            user_verificationsTable=table,
            user_verificationsForm=form,
            user_verification_paginator=paginator,
            route="user_verifications.user_verifications",
            perPage=perPage,
        ),
        code,
    )


@userVerificationsBlueprint.route(
    "/user_verifications/<UserVerification:user_verification>/", methods=["GET", "POST"]
)
@login_required
@verifyEditable("user_verification")
def editUserVerification(user_verification):
    form = UserVerificationForm(obj=user_verification)
    code = 200
    if request.method == "POST":
        if form.validate_on_submit():
            itemsToUpdate = []
            for item in PatchUserVerificationDetailsParameters.fields:
                if (
                    getattr(form, item, None) is not None
                    and getattr(user_verification, item) != getattr(form, item).data
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
                    PatchUserVerificationDetailsParameters().validate_patch_structure(
                        item
                    )
                try:
                    with api.commit_or_abort(
                        db.session,
                        default_error_message="Failed to update User Verification details.",
                    ):
                        PatchUserVerificationDetailsParameters.perform_patch(
                            itemsToUpdate, user_verification
                        )
                        db.session.merge(user_verification)
                        code = 202
                        flash(
                            f"User Verification for User ID {user_verification.user_id} saved successfully!",
                            "success",
                        )
                except Exception as error:  # pragma: no cover
                    log.exception(error)
                    code = 400
                    flash(
                        f"Failed to update User Verification for User ID {user_verification.user_id}",
                        "error",
                    )
        else:
            code = 422
    return (
        render_template(
            "edit_user_verification.html",
            user_verification=user_verification,
            form=form,
        ),
        code,
    )
