import logging, praw

import requests
from flask import Blueprint, request, render_template, flash, jsonify
from flask_login import current_user, login_required
from wtforms import BooleanField

from .parameters import PatchRefreshTokenDetailsParameters
from ..user_verifications.forms import UserVerificationForm
from ..user_verifications.models import UserVerification
from ..user_verifications.tables import UserVerificationTable
from ..users.models import User
from ...extensions import db, paginateArgs, verifyEditable

log = logging.getLogger(__name__)
from .models import RefreshToken
from .forms import GenerateRefreshTokenForm
from .tables import RefreshTokenTable

refreshTokensBlueprint = Blueprint('refresh_tokens', __name__, template_folder='./templates', static_folder='./static', static_url_path='/refresh_tokens/static/')

@login_required
@refreshTokensBlueprint.route('/refresh_tokens', methods=['GET', 'POST'])
@paginateArgs(RefreshToken)
def refresh_tokens(page, perPage):
    form = GenerateRefreshTokenForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            data = form.data
            redditKwargs = ['client_id', 'client_secret', 'user_agent', 'redirect_uri']
            reddit = praw.Reddit(**{key: getattr(form.reddit_app_id.data, key) for key in redditKwargs})
            # del data['csrf_token']
            # refreshToken = RefreshToken(**data)
            # db.session.add(refreshToken)
        else:
            return jsonify(status='error', errors=form.errors)
    if current_user:
        if current_user.is_admin and not current_user.is_internal:
            refreshTokenPaginator = RefreshToken.query.filter(*(RefreshToken.owner_id!=i.id for i in User.query.filter(User.internal==True).all())).paginate(page, perPage, error_out=False)
            userVerificationPaginator = UserVerification.query.filter(*(UserVerification.owner_id!=i.id for i in User.query.filter(User.internal==True).all())).paginate(page, perPage, error_out=False)
        elif current_user.is_internal:
            refreshTokenPaginator = RefreshToken.query.paginate(page, perPage, error_out=False)
            userVerificationPaginator = UserVerification.query.paginate(page, perPage, error_out=False)
        else:
            refreshTokenPaginator = current_user.refresh_tokens.paginate(page, perPage, error_out=False)
            userVerificationPaginator = current_user.verified.paginate(page, perPage, error_out=False)
    else:
        refreshTokenPaginator = current_user.refresh_tokens.paginate(page, perPage, error_out=False)
        userVerificationPaginator = current_user.verified.paginate(page, perPage, error_out=False)
    table = RefreshTokenTable(refreshTokenPaginator.items, current_user=current_user)
    form = GenerateRefreshTokenForm()
    userVerificationsTable = UserVerificationTable(refreshTokenPaginator.items, current_user=current_user)
    userVerificationsForm = UserVerificationForm()
    return render_template('refresh_tokens.html', refresh_tokensTable=table, refresh_tokensForm=form, refresh_token_paginator=refreshTokenPaginator, route='refresh_tokens.refresh_tokens', perPage=perPage, user_verificationsTable=userVerificationsTable, user_verificationsForm=userVerificationsForm, user_verification_paginator=userVerificationPaginator)

# @refreshTokensBlueprint.route('/reddit_callback')
# def reddit_callback():
#     state = request.args.get('state', '')
#     code = request.args.get('code')
#     if state == '' or code == '':
#         return 'Hello, please contact <a href="https://www.reddit.com/message/compose?to=Lil_SpazJoekp&amp;subject=Reddit%20Auth">u/Lil_SpazJoekp</a> for help.'
#     try:
#         encodedAuthor = None
#         redditapps = getRefreshTokens()
#         if len(state) == 128:
#             encodedAuthor = state[64:]
#             state = state[:64]
#         if state in redditapps:
#             redditConfig = redditapps[state]
#             appType = redditConfig['type']
#             client_id = redditConfig['client_id']
#             client_secret = redditConfig['client_secret']
#             redirect_uri = redditConfig['redirect_uri']
#             user_agent = redditConfig['user_agent']
#             appName = redditConfig['app_name']
#             webhookUrl = 'https://discordapp.com/api/webhooks/638068060044918802/0jdPhgxwt-0IEVOfXyKj03xQC-xDFKJk8Dr4TcfKf3_nmsW9t3QzpRIOE4dmS5l2aMoL'
#             crypto = services._BotServices__TokenCrypto(appName, sql)
#             reddit = praw.Reddit(**redditConfig)
#             if encodedAuthor:
#                 webhook = Webhook.from_url(webhookUrl, adapter=RequestsWebhookAdapter())
#                 state = encodedAuthor
#                 try:
#                     token = reddit.auth.authorize(code)
#                 except prawcore.exceptions.OAuthException as error:
#                     return handleError(error, appName)
#                 user = reddit.user.me(use_cache=False).name
#                 logger.info(f'user: {user}')
#                 sql.execute('SELECT * FROM verified WHERE encoded_id=%s', (state,))
#                 results = sql.fetchone()
#                 logger.info(f'results: {results}')
#                 newUser = True
#                 if results:
#                     if results.redditor:
#                         newUser = False
#                     sql.execute('UPDATE verified SET redditor=%s WHERE encoded_id=%s',  (user, state))
#                     if newUser:
#                         webhook.send(f'.done {results.member_id}')
#                     return render_template('success.html', user=user)
#                 else:
#                     return render_template('help.html')
#             else:
#                 # redirect_uri = 'http://localhost:5000/reddit_oauth'
#                 try:
#                     token = reddit.auth.authorize(code)
#                 except prawcore.exceptions.OAuthException as error:
#                     return handleError(error, appName)
#                 redditor = reddit.user.me(use_cache=False).name
#                 scopes = list(reddit.auth.scopes())
#                 issued = psycopg2.TimestampFromTicks(time.time())
#                 data = (base64.b64encode(crypto.encrypt(token)).decode(), redditor, client_id, scopes, appName, appType, issued)
#                 print(f'data: {data}')
#                 log(f'data: {data}')
#                 sql.execute("SELECT * FROM oauth.refreshtokens WHERE redditor=%s AND appname=%s AND NOT revoked", (redditor, appName))
#                 results = sql.fetchall()
#                 if results:
#                     for result in results:
#                         sql.execute('UPDATE oauth.refreshtokens SET refreshtoken = %s, scopes = %s, issued = %s WHERE redditor=%s AND appname=%s', (base64.b64encode(crypto.encrypt(token)).decode(), scopes, issued, redditor, appName))
#                         sql.execute('INSERT INTO oauth.oldrefreshtokens(refreshtoken, redditor, clientid, scopes, appname, apptype, issued, revoked) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', result)
#                 else:
#                     sql.execute('INSERT INTO oauth.refreshtokens(refreshtoken, redditor, clientid, scopes, appname, apptype, issued) VALUES (%s, %s, %s, %s, %s, %s, %s)', data)
#                 data = ()
#                 return render_template('success.html', user=redditor, app=appName)
#         else:
#             return 'Hello, please contact <a href="https://www.reddit.com/message/compose?to=Lil_SpazJoekp&amp;subject=Reddit%20Auth">u/Lil_SpazJoekp</a> for help.'
#     except Exception as error:
#         return handleError(error, appName)