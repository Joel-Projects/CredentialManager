import logging
import os
from datetime import datetime, timezone

import requests
from flask import Blueprint, render_template, request
from flask_login import current_user, login_required
from sqlalchemy import or_

from ...extensions import db, paginate_args, verify_editable
from ..reddit_apps.models import RedditApp
from ..user_verifications.models import UserVerification
from ..users.models import User
from .forms import RefreshTokenForm
from .models import RefreshToken
from .tables import RefreshTokenTable

log = logging.getLogger(__name__)

refresh_tokens_blueprint = Blueprint(
    "refresh_tokens",
    __name__,
    template_folder="./templates",
    static_folder="./static",
    static_url_path="/refresh_tokens/static/",
)


@refresh_tokens_blueprint.route("/refresh_tokens", methods=["GET", "POST"])
@login_required
@paginate_args(RefreshToken)
def refresh_tokens(page, per_page, order_by, sort_columns, sort_directions):
    show_old = request.args.get("show_old", "false").lower() == "true"
    if current_user.is_internal:
        query = RefreshToken.query
    elif current_user.is_admin:
        query = RefreshToken.query.filter(RefreshToken.owner.has(internal=False))
    else:
        query = current_user.refresh_tokens
    if not order_by:
        order_by = [RefreshToken.redditor.asc()]
    if "reddit_app" in sort_columns:
        query = query.outerjoin(RedditApp)
    if "owner" in sort_columns:
        query = query.outerjoin(User)
    paginator = query.order_by(*order_by).paginate(page, per_page, error_out=False)
    table = RefreshTokenTable(
        paginator.items,
        sort_columns=sort_columns,
        sort_directions=sort_directions,
        show_old=show_old,
    )
    form = RefreshTokenForm()
    return render_template(
        "refresh_tokens.html",
        refresh_tokens_table=table,
        refresh_tokens_form=form,
        paginator=paginator,
        route="refresh_tokens.refresh_tokens",
        per_page=per_page,
        show_old=show_old,
    )


@refresh_tokens_blueprint.route("/refresh_tokens/<RefreshToken:refresh_token>/")
@login_required
@verify_editable("refresh_token")
def edit_refresh_token(refresh_token):
    return render_template("edit_refresh_token.html", refresh_token=refresh_token)


@refresh_tokens_blueprint.route("/oauth2/reddit_callback")
def reddit_callback():
    state = request.args.get("state", "")
    code = request.args.get("code")
    header = "Reddit Account Verification"
    if state == "" or code == "":
        return render_template("oauth_result.html", success=False, header=header)
    try:
        now = datetime.now(timezone.utc)
        now.replace(tzinfo=timezone.utc)
        refresh_token = None
        reddit_app, user_id = RedditApp().get_app_from_state(state)
        if reddit_app:
            reddit = reddit_app.reddit_instance
            token = reddit.auth.authorize(code)
            redditor = reddit.user.me().name
            if token:
                scopes = reddit.auth.scopes()
                existing = RefreshToken.query.filter(
                    RefreshToken.reddit_app == reddit_app,
                    RefreshToken.redditor == redditor,
                    RefreshToken.revoked == False,
                ).first()
                if existing:  # pragma: no cover
                    existing.revoke()
                refresh_token = RefreshToken(
                    reddit_app=reddit_app,
                    redditor=redditor,
                    refresh_token=token,
                    scopes=list(scopes),
                    issued_at=now,
                    owner=reddit_app.owner,
                )
                with db.session.begin():
                    db.session.add(refresh_token)
            if user_id:
                user_verification = UserVerification.query.filter_by(user_id=user_id).first()
                if user_verification and user_verification.reddit_app == reddit_app:
                    user_verification.redditor = redditor
                    user_verification.verified_at = now
                with db.session.begin():
                    db.session.merge(user_verification)
                if user_verification.extra_data:
                    if "sioux_bot" in user_verification.extra_data:  # pragma: no cover
                        webhook = os.getenv("SIOUX_BOT_WEBHOOK")
                        if webhook:
                            requests.post(webhook, data={"content": f".done {user_id}"})
                    elif "webhook" in user_verification.extra_data:  # pragma: no cover
                        if isinstance(user_verification.extra_data["webhook"], dict):
                            if {"prefix", "command", "url"} == set(user_verification.extra_data["webhook"]):
                                prefix = user_verification.extra_data["webhook"]["prefix"]
                                command = user_verification.extra_data["webhook"]["command"]
                                webhook = user_verification.extra_data["webhook"]["url"]
                                requests.post(
                                    webhook,
                                    data={"content": f"{prefix}{command} {user_id}"},
                                )
                        elif isinstance(user_verification.extra_data["webhook"], str):
                            requests.post(
                                user_verification.extra_data["webhook"],
                                data={"content": user_id},
                            )
            if refresh_token:
                app_name = refresh_token.reddit_app.app_name
                header = f"Reddit Authorization Complete"
            else:
                app_name = reddit_app.app_name
                header = f"Reddit Verification Complete"
            return render_template(
                "oauth_result.html",
                success=True,
                header=header,
                user=redditor,
                message=f', your Reddit account has been {("verified", "authenticated")[bool(refresh_token)]} with {app_name!r} successfully!',
            )
    except Exception as error:  # pragma: no cover
        log.error(error)
    return render_template("oauth_result.html", error=True)
