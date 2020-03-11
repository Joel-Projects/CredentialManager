import logging

from flask import Blueprint, flash, jsonify, render_template, request
from flask_login import current_user, login_required
from wtforms import BooleanField

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
    form = RedditAppForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            data = form.data
            redditApp = RedditApp(**data)
            db.session.add(redditApp)
        else:
            return jsonify(status='error', errors=form.errors)
    if current_user:
        if current_user.is_admin and not current_user.is_internal:
            paginator = RedditApp.query.filter(*(RedditApp.owner_id != i.id for i in User.query.filter(User.internal == True).all())).paginate(page, perPage, error_out=False)
        elif current_user.is_internal:
            paginator = RedditApp.query.paginate(page, perPage, error_out=False)
        else:
            paginator = current_user.reddit_apps.paginate(page, perPage, error_out=False)
    else:
        paginator = current_user.reddit_apps.paginate(page, perPage, error_out=False)
    table = RedditAppTable(paginator.items, current_user=current_user)
    form = RedditAppForm()
    return render_template('reddit_apps.html', reddit_appsTable=table, reddit_appsForm=form, paginator=paginator, route='reddit_apps.reddit_apps', perPage=perPage)

@redditAppsBlueprint.route('/reddit_apps/<RedditApp:reddit_app>/', methods=['GET', 'POST'])
@login_required
@verifyEditable('reddit_app')
def editRedditApp(reddit_app):
    form = RedditAppForm(obj=reddit_app)
    if request.method == 'POST':
        if form.validate_on_submit():
            itemsToUpdate = []
            for item in PatchRedditAppDetailsParameters.fields:
                if getattr(form, item, None) is not None:
                    if not isinstance(getattr(form, item), BooleanField):
                        if getattr(form, item).data:
                            if getattr(reddit_app, item) != getattr(form, item).data:
                                itemsToUpdate.append({'op': 'replace', 'path': f'/{item}', 'value': getattr(form, item).data})
                    else:
                        if getattr(reddit_app, item) != getattr(form, item).data:
                            itemsToUpdate.append({'op': 'replace', 'path': f'/{item}', 'value': getattr(form, item).data})
            if itemsToUpdate:
                for item in itemsToUpdate:
                    PatchRedditAppDetailsParameters().validate_patch_structure(item)
                try:
                    with api.commit_or_abort(db.session, default_error_message='Failed to update Reddit App details.'):
                        PatchRedditAppDetailsParameters.perform_patch(itemsToUpdate, reddit_app)
                        db.session.merge(reddit_app)
                        flash(f'Reddit App {reddit_app.app_name!r} saved successfully!', 'success')
                except Exception as error:
                    log.exception(error)
                    flash(f'Failed to update Reddit App {reddit_app.app_name!r}', 'error')
    return render_template('edit_reddit_app.html', reddit_app=reddit_app, form=form)