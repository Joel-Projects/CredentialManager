import logging, os

import requests
from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from flask_restplus._http import HTTPStatus
from wtforms import BooleanField

from .parameters import PatchBotDetailsParameters
from ..users.models import User
from ...extensions import db, paginateArgs, verifyEditable

log = logging.getLogger(__name__)
from .models import Bot
from .forms import BotForm
from .tables import BotTable

botsBlueprint = Blueprint('bots', __name__, template_folder='./templates', static_folder='./static', static_url_path='/bots/static/')

@login_required
@botsBlueprint.route('/bots', methods=['GET', 'POST'])
@paginateArgs(Bot)
def bots(page, perPage):
    form = BotForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            data = form.data
            # del data['csrf_token']
            bot = Bot(**data)
            db.session.add(bot)
        else:
            return jsonify(status='error', errors=form.errors)
    if current_user.is_admin and not current_user.is_internal:
        paginator = Bot.query.filter(*(Bot.owner_id!=i.id for i in User.query.filter(User.internal==True).all())).paginate(page, perPage, error_out=False)
    elif current_user.is_internal:
        paginator = Bot.query.paginate(page, perPage, error_out=False)
    else:
        paginator = current_user.bots.paginate(page, perPage, error_out=False)
    table = BotTable(paginator.items, current_user=current_user)
    form = BotForm()
    return render_template('bots.html', botsTable=table, botsForm=form, paginator=paginator, route='bots.bots', perPage=perPage)

@login_required
@botsBlueprint.route('/bots/<Bot:bot>/', methods=['GET', 'POST'])
@verifyEditable('bot')
def editBot(bot):
    form = BotForm(obj=bot)
    if request.method == 'POST':
        if form.validate_on_submit():
            itemsToUpdate = []
            for item in PatchBotDetailsParameters.fields:
                if getattr(form, item, None) is not None:
                    if not isinstance(getattr(form, item), BooleanField):
                        if getattr(form, item).data:
                            if getattr(bot, item) != getattr(form, item).data:
                                itemsToUpdate.append({"op": "replace", "path": f'/{item}', "value": getattr(form, item).data})
                    else:
                        if getattr(bot, item) != getattr(form, item).data:
                            itemsToUpdate.append({"op": "replace", "path": f'/{item}', "value": getattr(form, item).data})
            if itemsToUpdate:
                response = requests.patch(f'{request.host_url}api/v1/bots/{bot.id}', json=itemsToUpdate, headers={'Cookie': request.headers['Cookie'], 'Content-Type': 'application/json'})
                if response.status_code == 200:
                    flash(f'Bot {bot.app_name!r} saved successfully!', 'success')
                else:
                    flash(f'Failed to update Bot {bot.app_name!r}', 'error')
        else:
            return jsonify(status='error', errors=form.errors)
    return render_template('edit_bot.html', bot=bot, form=form)
