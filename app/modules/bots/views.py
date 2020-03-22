import logging

from flask import Blueprint, flash, jsonify, render_template, request
from flask_login import current_user, login_required
from wtforms import BooleanField

from .parameters import PatchBotDetailsParameters
from .resources import api
from ..users.models import User
from ...extensions import db, paginateArgs, verifyEditable


log = logging.getLogger(__name__)
from .models import Bot
from .forms import BotForm
from .tables import BotTable


botsBlueprint = Blueprint('bots', __name__, template_folder='./templates', static_folder='./static', static_url_path='/bots/static/')

@botsBlueprint.route('/bots', methods=['GET', 'POST'])
@login_required
@paginateArgs(Bot)
def bots(page, perPage):
    form = BotForm()
    code = 200
    if request.method == 'POST':
        if form.validate_on_submit():
            if not current_user.is_admin and not current_user.is_internal:
                if current_user != form.data['owner']:
                    code = 403
                    return jsonify(status='error', message="You can't create Bots for other users"), code
            code = 201
            data = form.data
            bot = Bot(**data)
            db.session.add(bot)
        else:
            code = 422
            return jsonify(status='error', errors=form.errors), code
    if current_user.is_admin and not current_user.is_internal:
        paginator = Bot.query.filter(*(Bot.owner_id != i.id for i in User.query.filter(User.internal == True).all())).paginate(page, perPage, error_out=False)
    elif current_user.is_internal:
        paginator = Bot.query.paginate(page, perPage, error_out=False)
    else:
        paginator = current_user.bots.paginate(page, perPage, error_out=False)
    table = BotTable(paginator.items, current_user=current_user)
    form = BotForm()
    return render_template('bots.html', botsTable=table, botsForm=form, paginator=paginator, route='bots.bots', perPage=perPage), code

@botsBlueprint.route('/bots/<Bot:bot>/', methods=['GET', 'POST'])
@login_required
@verifyEditable('bot')
def editBots(bot):
    form = BotForm(obj=bot)
    code = 200
    if request.method == 'POST':
        if form.validate_on_submit():
            itemsToUpdate = []
            for item in PatchBotDetailsParameters.fields:
                if getattr(form, item, None) is not None and getattr(bot, item) != getattr(form, item).data:
                    itemsToUpdate.append({'op': 'replace', 'path': f'/{item}', 'value': getattr(form, item).data})
            if itemsToUpdate:
                for item in itemsToUpdate:
                    PatchBotDetailsParameters().validate_patch_structure(item)
                try:
                    with api.commit_or_abort(db.session, default_error_message='Failed to update Bot details.'):
                        PatchBotDetailsParameters.perform_patch(itemsToUpdate, bot)
                        db.session.merge(bot)
                        code = 202
                        flash(f'Bot {bot.app_name!r} saved successfully!', 'success')
                except Exception as error:
                    log.exception(error)
                    code = 400
                    flash(f'Failed to update Bot {bot.app_name!r}', 'error')
        else:
            code = 422
    return render_template('edit_bot.html', bot=bot, form=form), code