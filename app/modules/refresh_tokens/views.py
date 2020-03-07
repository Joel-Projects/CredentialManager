import logging, praw, os, requests
from datetime import datetime, timezone
from flask import Blueprint, request, render_template
from flask_login import current_user, login_required
from sqlalchemy import or_
from .models import RefreshToken
from .forms import GenerateRefreshTokenForm
from .tables import RefreshTokenTable
from ..reddit_apps.models import RedditApp
from ..user_verifications.models import UserVerification
from ..users.models import User
from ...extensions import db, paginateArgs, verifyEditable

log = logging.getLogger(__name__)

refreshTokensBlueprint = Blueprint('refresh_tokens', __name__, template_folder='./templates', static_folder='./static', static_url_path='/refresh_tokens/static/')

@refreshTokensBlueprint.route('/refresh_tokens', methods=['GET', 'POST'])
@login_required
@paginateArgs(RefreshToken)
def refresh_tokens(page, perPage):
    showOld = request.args.get('showOld', 'False') == 'True'
    if current_user:
        if current_user.is_admin and not current_user.is_internal:
            paginator = RefreshToken.query.filter(*(RefreshToken.owner_id!=i.id for i in User.query.filter(User.internal==True).all()), or_(RefreshToken.revoked==False, RefreshToken.revoked==showOld)).paginate(page, perPage, error_out=False)
        elif current_user.is_internal:
            paginator = RefreshToken.query.filter(or_(RefreshToken.revoked==False, RefreshToken.revoked==showOld)).paginate(page, perPage, error_out=False)
        else:
            paginator = current_user.refresh_tokens.filter(or_(RefreshToken.revoked==False, RefreshToken.revoked==showOld)).paginate(page, perPage, error_out=False)
    else:
        paginator = current_user.refresh_tokens.filter(or_(RefreshToken.revoked==False, RefreshToken.revoked==showOld)).paginate(page, perPage, error_out=False)
    table = RefreshTokenTable(paginator.items, current_user=current_user, showOld=showOld)
    form = GenerateRefreshTokenForm()
    return render_template('refresh_tokens.html', refresh_tokensTable=table, refresh_tokensForm=form, paginator=paginator, route='refresh_tokens.refresh_tokens', perPage=perPage, showOld=showOld)

@refreshTokensBlueprint.route('/refresh_tokens/<RefreshToken:refresh_token>/')
@login_required
@verifyEditable('refresh_token')
def editRefreshToken(refresh_token):
    return render_template('edit_refresh_token.html', refresh_token=refresh_token)

@refreshTokensBlueprint.route('/oauth2/reddit_callback')
def reddit_callback():
    state = request.args.get('state', '')
    code = request.args.get('code')
    header = 'Reddit Account Verification'
    if state == '' or code == '':
        return render_template('oauth_result.html', success=False, header=header)
    try:
        now = datetime.now(timezone.utc)
        now.replace(tzinfo=timezone.utc)
        refreshToken = None
        redditApp: RedditApp
        redditApp, discord_id = RedditApp().getAppFromState(state)
        if redditApp:
            reddit = redditApp.redditInstance
            token = reddit.auth.authorize(code)
            redditor = reddit.user.me().name
            if token:
                scopes = reddit.auth.scopes()
                existing = RefreshToken.query.filter(RefreshToken.reddit_app==redditApp, RefreshToken.redditor==redditor, RefreshToken.revoked==False).first()
                if existing:
                    existing.revoke()
                refreshToken = RefreshToken(reddit_app=redditApp, redditor=redditor, refresh_token=token, scopes=list(scopes), issued_at=now, owner=redditApp.owner)
                db.session.add(refreshToken)
            if discord_id:
                userVerification = UserVerification.query.filter_by(discord_id=discord_id).first()
                if userVerification and userVerification.reddit_app == redditApp:
                    userVerification.redditor = redditor
                    userVerification.verified_at = now
                if 'sioux_bot' in userVerification.extra_data:
                    webhook = os.getenv('SIOUX_BOT_WEBHOOK')
                    if webhook:
                        requests.post(webhook, data={'content': f'.done {discord_id}'})
            if refreshToken:
                appName = refreshToken.reddit_app.app_name
                header = f'Reddit Authorization Complete'
            else:
                appName = redditApp.app_name
                header = f'Reddit Verification Complete'
            return render_template('oauth_result.html', success=True, header=header, user=redditor, message=f', your Reddit account has been {("verified", "authenticated")[bool(refreshToken)]} with {appName!r} successfully!')
    except Exception as error:
        log.error(error)
        return render_template('oauth_result.html', error=True)