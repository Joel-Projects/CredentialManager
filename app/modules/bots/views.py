import logging

from flask import Blueprint, flash, jsonify, render_template, request
from flask_login import current_user, login_required
from wtforms import BooleanField

from ...extensions import db, paginate_args, verify_editable
from .. import get_paginator
from ..users.models import User
from .parameters import PatchBotDetailsParameters
from .resources import api

log = logging.getLogger(__name__)
from .forms import BotForm
from .models import Bot
from .tables import BotTable

bots_blueprint = Blueprint(
    "bots",
    __name__,
    template_folder="./templates",
    static_folder="./static",
    static_url_path="/bots/static/",
)


@bots_blueprint.route("/bots", methods=["GET", "POST"])
@login_required
@paginate_args(Bot)
def bots(page, per_page, order_by, sort_columns, sort_directions):
    form = BotForm()
    code = 200
    if request.method == "POST":
        if form.validate_on_submit():
            if not current_user.is_admin and not current_user.is_internal:
                if current_user != form.data["owner"]:
                    code = 403
                    return (
                        jsonify(
                            status="error",
                            message="You can't create Bots for other users",
                        ),
                        code,
                    )
            code = 201
            data = form.get_db_data()
            bot = Bot(**data)
            with api.commit_or_abort(db.session, default_error_message="Failed to create a new Bot."):
                db.session.add(bot)
        else:
            return jsonify(status="error", errors=form.errors), code
    paginator = get_paginator(Bot, page, per_page, order_by, sort_columns)
    table = BotTable(paginator.items, sort_columns=sort_columns, sort_directions=sort_directions)
    form = BotForm()
    return (
        render_template(
            "bots.html",
            bots_table=table,
            bots_form=form,
            paginator=paginator,
            route="bots.bots",
            per_page=per_page,
        ),
        code,
    )


@bots_blueprint.route("/bots/<Bot:bot>/", methods=["GET", "POST"])
@login_required
@verify_editable("bot")
def edit_bots(bot):
    form = BotForm(obj=bot)
    code = 200
    if request.method == "POST":
        if form.validate_on_submit():
            items_to_update = []
            for item in PatchBotDetailsParameters.fields:
                if item in [
                    "reddit_app_id",
                    "sentry_token_id",
                    "database_credential_id",
                ]:
                    item = item[:-3]
                if getattr(form, item, None) is not None and getattr(bot, item) != getattr(form, item).data:
                    if item in ["reddit_app", "sentry_token", "database_credential"]:
                        value = getattr(form, item).data.id
                        item = f"{item}_id"
                    else:
                        value = getattr(form, item).data
                    items_to_update.append({"op": "replace", "path": f"/{item}", "value": value})
            if items_to_update:
                for item in items_to_update:
                    PatchBotDetailsParameters().validate_patch_structure(item)
                try:
                    with api.commit_or_abort(
                        db.session,
                        default_error_message="Failed to update Bot details.",
                    ):
                        PatchBotDetailsParameters.perform_patch(items_to_update, bot)
                        db.session.merge(bot)
                        code = 202
                        flash(f"Bot {bot.app_name!r} saved successfully!", "success")
                except Exception as error:  # pragma: no cover
                    log.exception(error)
                    code = 400
                    flash(f"Failed to update Bot {bot.app_name!r}", "error")
        else:
            code = 422
    return render_template("edit_bot.html", bot=bot, form=form), code
