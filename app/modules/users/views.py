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

from flask import Blueprint, render_template
from flask_login import current_user, login_required

from ..api_tokens.views import TokenTable

log = logging.getLogger(__name__)

usersBlueprint = Blueprint('users', __name__)

@login_required
@usersBlueprint.route('/u/<User:user>/api_tokens')
def api_tokensPerUser(user):
    api_tokens = user.api_tokens.all()
    table = TokenTable(api_tokens, current_user=current_user)
    return render_template('api_tokens.html', table=table, user=user)
