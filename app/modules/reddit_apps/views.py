import logging

from flask import Blueprint, flash, jsonify, render_template, request
from flask_login import current_user, login_required

from ...extensions import db, paginate_args, verify_editable
from .. import get_paginator
from .parameters import PatchRedditAppDetailsParameters
from .resources import api

log = logging.getLogger(__name__)
from .forms import RedditAppForm
from .models import RedditApp
from .tables import RedditAppTable

reddit_apps_blueprint = Blueprint(
    "reddit_apps",
    __name__,
    template_folder="./templates",
    static_folder="./static",
    static_url_path="/reddit_apps/static/",
)


@reddit_apps_blueprint.route("/reddit_apps", methods=["GET", "POST"])
@login_required
@paginate_args(RedditApp)
def reddit_apps(page, per_page, order_by, sort_columns, sort_directions):
    code = 200
    form = RedditAppForm()
    if request.method == "POST":
        if form.validate_on_submit():
            if not current_user.is_admin and not current_user.is_internal and current_user != form.data["owner"]:
                code = 403
                return (
                    jsonify(
                        status="error",
                        message="You can't create Reddit Apps for other users",
                    ),
                    code,
                )
            code = 201
            data = form.get_db_data()
            reddit_app = RedditApp(**data)
            db.session.add(reddit_app)
        else:
            return jsonify(status="error", errors=form.errors), code
    paginator = get_paginator(RedditApp, page, per_page, order_by, sort_columns)
    table = RedditAppTable(paginator.items, sort_columns=sort_columns, sort_directions=sort_directions)
    form = RedditAppForm()
    return (
        render_template(
            "reddit_apps.html",
            reddit_apps_table=table,
            reddit_apps_form=form,
            paginator=paginator,
            route="reddit_apps.reddit_apps",
            per_page=per_page,
        ),
        code,
    )


@reddit_apps_blueprint.route("/reddit_apps/<RedditApp:reddit_app>/", methods=["GET", "POST"])
@login_required
@verify_editable("reddit_app")
def edit_reddit_app(reddit_app):
    form = RedditAppForm(obj=reddit_app)
    code = 200
    if request.method == "POST":
        if form.validate_on_submit():
            items_to_update = []
            for item in PatchRedditAppDetailsParameters.fields:
                if getattr(form, item, None) is not None and getattr(reddit_app, item) != getattr(form, item).data:
                    items_to_update.append(
                        {
                            "op": "replace",
                            "path": f"/{item}",
                            "value": getattr(form, item).data,
                        }
                    )
            if items_to_update:
                for item in items_to_update:
                    PatchRedditAppDetailsParameters().validate_patch_structure(item)
                try:
                    with api.commit_or_abort(
                        db.session,
                        default_error_message="Failed to update Reddit App details.",
                    ):
                        PatchRedditAppDetailsParameters.perform_patch(items_to_update, reddit_app)
                        db.session.merge(reddit_app)
                        code = 202
                        flash(
                            f"Reddit App {reddit_app.app_name!r} saved successfully!",
                            "success",
                        )
                except Exception as error:  # pragma: no cover
                    log.exception(error)
                    code = 400
                    flash(f"Failed to update Reddit App {reddit_app.app_name!r}", "error")
        else:
            code = 422
    return (
        render_template("edit_reddit_app.html", reddit_app=reddit_app, form=form),
        code,
    )
