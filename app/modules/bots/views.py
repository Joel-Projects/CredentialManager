import logging, os

from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user, login_required
from flask_restplus._http import HTTPStatus

log = logging.getLogger(__name__)
from .models import Bot
from .forms import BotForm
from .tables import BotTable

botsBlueprint = Blueprint('bots', __name__, template_folder='./templates', static_folder='./static', static_url_path='/bots/static/')

@login_required
@botsBlueprint.route('/bots')
def bots():
    if current_user.is_admin or current_user.is_internal:
        bots = Bot.query.all()
    else:
        bots = current_user.bots.all()
    table = BotTable(bots, current_user=current_user)
    form = BotForm()
    return render_template('bots.html', table=table, form=form)
