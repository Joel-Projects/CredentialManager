import logging

from flask import Blueprint, flash, jsonify, render_template, request
from flask_login import current_user, login_required

from .parameters import PatchRedditAppDetailsParameters
from .resources import api
from ..users.models import User
from ...extensions import db, paginateArgs, verifyEditable


log = logging.getLogger(__name__)
from .models import RedditApp
from .forms import RedditAppForm
from .tables import RedditAppTable


redditAppsBlueprint = Blueprint('reddit_apps', __name__, template_folder='./templates', static_folder='./static', static_url_path='/reddit_apps/static/')

@redditAppsBlueprint.route('/reddit_apps', methods=['GET', 'POST'])
@login_required
@paginateArgs(RedditApp)
def reddit_apps(page, perPage):
    code = 200
    form = RedditAppForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if not current_user.is_admin and not current_user.is_internal and current_user != form.data['owner']:
                code = 403
                return jsonify(status='error', message="You can't create Reddit Apps for other users"), code
            code = 201
            data = {key: value for key, value in form.data.items() if value is not None}
            redditApp = RedditApp(**data)
            db.session.add(redditApp)
        else:
            return jsonify(status='error', errors=form.errors), code
    if current_user.is_admin and not current_user.is_internal:
        paginator = RedditApp.query.filter(*(RedditApp.owner_id != i.id for i in User.query.filter(User.internal == True).all())).paginate(page, perPage, error_out=False)
    elif current_user.is_internal:
        paginator = RedditApp.query.paginate(page, perPage, error_out=False)
    else:
        paginator = current_user.reddit_apps.paginate(page, perPage, error_out=False)
    table = RedditAppTable(paginator.items, current_user=current_user)
    form = RedditAppForm()
    return render_template('reddit_apps.html', reddit_appsTable=table, reddit_appsForm=form, paginator=paginator, route='reddit_apps.reddit_apps', perPage=perPage), code

@redditAppsBlueprint.route('/reddit_apps/<RedditApp:reddit_app>/', methods=['GET', 'POST'])
@login_required
@verifyEditable('reddit_app')
def editRedditApp(reddit_app):
    form = RedditAppForm(obj=reddit_app)
    code = 200
    if request.method == 'POST':
        if form.validate_on_submit():
            itemsToUpdate = []
            for item in PatchRedditAppDetailsParameters.fields:
                if getattr(form, item, None) is not None and getattr(reddit_app, item) != getattr(form, item).data:
                    itemsToUpdate.append({'op': 'replace', 'path': f'/{item}', 'value': getattr(form, item).data})
            if itemsToUpdate:
                for item in itemsToUpdate:
                    PatchRedditAppDetailsParameters().validate_patch_structure(item)
                try:
                    with api.commit_or_abort(db.session, default_error_message='Failed to update Reddit App details.'):
                        PatchRedditAppDetailsParameters.perform_patch(itemsToUpdate, reddit_app)
                        db.session.merge(reddit_app)
                        code = 202
                        flash(f'Reddit App {reddit_app.app_name!r} saved successfully!', 'success')
                except Exception as error: # pragma: no cover
                    log.exception(error)
                    code = 400
                    flash(f'Failed to update Reddit App {reddit_app.app_name!r}', 'error')
        else:
            code = 422
    return render_template('edit_reddit_app.html', reddit_app=reddit_app, form=form), code