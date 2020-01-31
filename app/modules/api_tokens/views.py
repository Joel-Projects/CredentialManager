# coding: utf-8
"""
OAuth2 provider setup.

It is based on the code from the example:
https://github.com/lepture/example-oauth2-server

More details are available here:
* http://flask-oauthlib.readthedocs.org/en/latest/oauth2.html
* http://lepture.com/en/2013/create-oauth-server
"""
import logging


from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user, login_required
from flask_restplus._http import HTTPStatus

from .tables import TokenTable

log = logging.getLogger(__name__)
from .models import ApiToken

apiTokensBlueprint = Blueprint('api_tokens', __name__, template_folder='./templates', static_folder='./app/models/api_tokens/static')

@login_required
@apiTokensBlueprint.route('/api_tokens')
def api_tokens():
    if current_user.is_admin or current_user.is_internal:
        api_tokens = ApiToken.query.all()
    else:
        api_tokens = current_user.api_tokens.all()
    table = TokenTable(api_tokens, current_user=current_user)
    return render_template('api_tokens.html', table=table)
