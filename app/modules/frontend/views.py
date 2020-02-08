import logging
from functools import wraps

from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user, login_required

log = logging.getLogger(__name__)

main = Blueprint('main', __name__)

@main.route('/')
def root():
    if current_user.is_authenticated:
        return render_template('dash.html')
    else:
        return redirect('/login')

@main.route('/dash')
@login_required
def dash():
    return render_template('dash.html')
#
# def requiresAdmin(func):
#     @wraps(func)
#     def decorated(*args, **kwargs):
#         if current_user and not current_user.is_admin and not current_user.is_internal:
#             abort(403)
#         return func(*args, **kwargs)
#     return decorated
#
#
# @main.route('/bots')
# @login_required
# def bots():
#     bots = Bot.query.all()
#     return render_template('bots.html', users=bots)
#
# @main.route('/database_creds')
# @login_required
# def database_creds():
#     database_creds = Database.query.all()
#     return render_template('database_creds.html', users=database_creds)
# #
# # @main.route('/reddit_apps')
# # @login_required
# # def reddit_apps():
# #     reddit_apps = RedditApp.query.all()
# #     return render_template('reddit_apps.html', users=reddit_apps)
#
# @main.route('/refresh_tokens')
# @login_required
# def refresh_tokens():
#     refresh_tokens = RefreshToken.query.all()
#     return render_template('refresh_tokens.html', users=refresh_tokens)


#
# @app.route('/reddit_oauth')
# def reddit_callback():
#     state = request.args.get('state', '')
#     code = request.args.get('code')
#     if state == '' or code == '':
#         return 'Hello, please contact <a href="https://www.reddit.com/message/compose?to=Lil_SpazJoekp&amp;subject=Reddit%20Auth">u/Lil_SpazJoekp</a> for help.'
#     try:
#         encodedAuthor = None
#         redditapps = getRedditApps()
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

@main.route('/profile')
@login_required
def profile():
    return render_template('edit_user.html', user=current_user)
