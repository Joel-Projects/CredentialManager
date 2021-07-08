import logging
from datetime import datetime, timezone

from flask import Blueprint, flash, jsonify, render_template, request
from flask_login import current_user, login_required
from wtforms import BooleanField

from ...extensions import db, paginate_args, verify_editable
from .. import get_paginator
from ..users.models import User
from .parameters import PatchSentryTokenDetailsParameters
from .resources import api
from .sentry_requestor import SentryRequestor

log = logging.getLogger(__name__)
from .forms import EditSentryTokenForm, SentryTokenForm
from .models import SentryToken
from .tables import SentryTokenTable

sentry_tokens_blueprint = Blueprint(
    "sentry_tokens",
    __name__,
    template_folder="./templates",
    static_folder="./static",
    static_url_path="/sentry_tokens/static/",
)


@sentry_tokens_blueprint.route("/sentry_tokens", methods=["GET", "POST"])
@login_required
@paginate_args(SentryToken)
def sentry_tokens(page, per_page, order_by, sort_columns, sort_directions):
    code = 200
    form = SentryTokenForm()
    requestor = SentryRequestor(current_user.sentry_auth_token)
    sentrydsn = None
    if request.method == "POST":
        if form.validate_on_submit():
            if not current_user.is_admin and not current_user.is_internal:
                if current_user != form.data["owner"]:
                    code = 403
                    return (
                        jsonify(
                            status="error",
                            message="You can't create Sentry Tokens for other users",
                        ),
                        code,
                    )
            if form.create_sentry_app.data:  # pragma: no cover
                if form.sentry_organization.data and form.sentry_team.data:
                    response = requestor.post(
                        f"/api/0/teams/{form.sentry_organization.data}/{form.sentry_team.data}/projects/",
                        item_name="project",
                        json={"name": form.app_name.data},
                    )
                    if hasattr(response, "slug"):
                        keys = requestor.get(
                            f"/api/0/projects/{form.sentry_organization.data}/{response.slug}/keys/",
                            item_name="key",
                        )
                        sentrydsn = keys[0].dsn.public
                        if form.sentry_platform.data:
                            requestor.put(
                                f"/api/0/projects/{form.sentry_organization.data}/{response.slug}/",
                                item_name="project",
                                json={"platform": form.sentry_platform.data},
                            )
                    else:
                        code = 400
                        return (
                            jsonify(
                                status="error", message="Failed to create Sentry token"
                            ),
                            code,
                        )
            code = 201
            data = {key: value for key, value in form.data.items() if value is not None}
            if sentrydsn:  # pragma: no cover
                data["dsn"] = sentrydsn
            data.pop("create_sentry_app")
            data.pop("sentry_organization")
            data.pop("sentry_team")
            data.pop("sentry_platform")
            sentry_token = SentryToken(**data)
            db.session.add(sentry_token)
        else:
            return jsonify(status="error", errors=form.errors)
    paginator = get_paginator(SentryToken, page, per_page, order_by, sort_columns)
    if current_user.sentry_auth_token:
        response = requestor.get(
            "/api/0/organizations/", "organization", params={"member": True}
        )
        organizations = [("", "")] + [(i.slug, i.name) for i in response]
        form.sentry_organization.choices = organizations
    table = SentryTokenTable(
        paginator.items, sort_columns=sort_columns, sort_directions=sort_directions
    )
    return (
        render_template(
            "sentry_tokens.html",
            sentry_tokens_table=table,
            sentry_tokens_form=form,
            paginator=paginator,
            route="sentry_tokens.sentry_tokens",
            per_page=per_page,
        ),
        code,
    )


@sentry_tokens_blueprint.route(
    "/sentry_tokens/<SentryToken:sentry_token>/", methods=["GET", "POST"]
)
@login_required
@verify_editable("sentry_token")
def edit_sentry_token(sentry_token):
    form = EditSentryTokenForm(obj=sentry_token)
    code = 200
    if request.method == "POST":
        if form.validate_on_submit():
            items_to_update = []
            for item in PatchSentryTokenDetailsParameters.fields:
                if (
                    getattr(form, item, None) is not None
                    and getattr(sentry_token, item) != getattr(form, item).data
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
                    PatchSentryTokenDetailsParameters().validate_patch_structure(item)
                try:
                    with api.commit_or_abort(
                        db.session,
                        default_error_message="Failed to update Sentry Token details.",
                    ):
                        PatchSentryTokenDetailsParameters.perform_patch(
                            items_to_update, sentry_token
                        )
                        db.session.merge(sentry_token)
                        code = 202
                        flash(
                            f"Sentry Token {sentry_token.app_name!r} saved successfully!",
                            "success",
                        )
                except Exception as error:  # pragma: no cover
                    log.exception(error)
                    code = 400
                    flash(
                        f"Failed to update Sentry Token {sentry_token.app_name!r}",
                        "error",
                    )
        else:
            code = 422
    return (
        render_template("edit_sentry_token.html", sentry_token=sentry_token, form=form),
        code,
    )


#
# @sentry_tokens_blueprint.route('/setup')
# def sentry_callback():
#     code = request.args.get('code')
#     installation_id = request.args.get('installation_id')
#
#     url = f'https://sentry.jesassn.org/api/0/sentry-app-installations/{installation_id}/authorizations/'
#
#     payload = {
#         'grant_type': 'authorization_code',
#         'code': code,
#         'client_id': BaseConfig.SENTRY_INTEGRATION_CLIENT_ID,
#         'client_secret': BaseConfig.SENTRY_INTEGRATION_CLIENT_SECRET
#     }
#     response = requests.post(url, json=payload)
#     data = response.json()
#
#     token = data['token']
#     refresh_token = data['refresh_token']
#     data.pop('scopes')
#     data['expires_at'] = datetime.fromisoformat(data['expires_at'].strip('Z')).replace(tzinfo=timezone.utc).astimezone()
#     data['date_created'] = datetime.fromisoformat(data['date_created'].strip('Z')).replace(tzinfo=timezone.utc).astimezone()
#     data['installation_id'] = installation_id
#     requestor = SentryRequestor(token)
#     organizations = requestor.get('/api/0/organizations/')
#     with api.commit_or_abort(db.session, default_error_message='Failed to update Sentry Token details.'):
#         sentry_instance_token = SentryRefreshToken(**data)
#         db.session.merge(sentry_instance_token)
#     sentry_instance_token._refresh('https://sentry.jesassn.org')
#     return redirect('https://sentry.jesassn.org/settings/')
#
# @sentry_tokens_blueprint.route('/webhook', methods=['POST'])
# def sentry_webhook():
#     code = request.args.get('code')
#     install_id = request.args.get('installation_id')
#
#     url = f'https://sentry.jesassn.org/api/0/sentry-app-installations/{install_id}/authorizations/'
#
#     payload = {
#         'grant_type': 'authorization_code',
#         'code': code,
#         'client_id': '507804f7282640068261600cc37e76b7a6b8ed5d64a3442fba06c859656f26e0',
#         'client_secret': 'a86a514e90b3432b88a2a19321cf38a6bd944ec7c318475498706e981bb092cb',
#     }
#
#     response = requests.post(url, json=payload)
#     data = response.json()
#
#     token = data['token']
#     refresh_token = data['refresh_token']
#     with api.commit_or_abort(db.session, default_error_message='Failed to update Sentry Token details.'):
#         sentry_instance_token = SentryRefreshToken(**data)
#         db.session.merge(sentry_instance_token)
#
#     return redirect('https://sentry.jesassn.org/settings/')
