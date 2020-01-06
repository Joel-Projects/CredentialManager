from flask import Blueprint, jsonify, request
from flask_login import login_required
from . import *

reddit_api = Blueprint('reddit_api', __name__, url_prefix='/api/reddit')

@reddit_api.route('/', methods=['GET'])
def getReddit():
    redditId = request.form['id']
    notification = {'success': None, 'error': None}
    try:
        reddit = RemovalReddit.query.filter_by(id=redditId).first()
        reddit.enabled = not reddit.enabled
        db.session.merge(reddit)
        db.session.commit()
        notification['success'] = True
    except Exception as error:
        notification['error'] = error
    return jsonify({'success': notification['success'], 'error': notification['error'], 'id': redditId, 'enabled': reddit.enabled}), 202

@reddit_api.route('/create', methods=['POST'])
@login_required
@requiresAdmin
def createRedditApp():
    subreddit = request.form['subreddit']
    flair_text = request.form['flair_text']
    description = request.form['description']
    commentToggle = request.form['commentToggle'] == 'true'
    if commentToggle:
        commentInput = request.form['commentInput']
    else:
        commentInput = None
    lockToggle = request.form['lockToggle'] == 'true'
    commentLockToggle = request.form['commentLockToggle'] == 'true'
    banToggle = request.form['banToggle'] == 'true'
    if banToggle:
        ban_duration = request.form['ban_duration']
        ban_reddit = request.form['ban_reddit']
        ban_message = request.form['ban_message']
        ban_note = request.form['ban_note']
    else:
        ban_duration = None
        ban_reddit = None
        ban_message = None
        ban_note = None
    usernoteToggle = request.form['usernoteToggle'] == 'true'
    if usernoteToggle:
        usernote_note = request.form['usernote_note']
        usernote_warning_type = request.form['usernote_warning_type']
    else:
        usernote_note = None
        usernote_warning_type = None
    enableOnAdd = request.form['enableOnAdd'] == 'true'
    success = None
    error = None
    redditExists = False
    try:
        reddit = RemovalReddit(subreddit=subreddit, flair_text=flair_text.lower(), description=description, comment=commentInput, lock=lockToggle, lock_comment=commentLockToggle, ban=banToggle, ban_duration=ban_duration, ban_reddit=ban_reddit, ban_message=ban_message, ban_note=ban_note, usernote=usernoteToggle, usernote_note=usernote_note, usernote_warning_type=usernote_warning_type, enabled=enableOnAdd)
        existing = RemovalReddit.query.filter_by(subreddit=subreddit, flair_text=flair_text).first()
        if existing:
            redditExists = True
        else:
            db.session.add(reddit)
            db.session.commit()
            success = f'Created removal reddit for r/{reddit.subreddit} successfully!'
    except Exception as err:
        error = str(err)
    redditData = {'id': reddit.id, 'subreddit': reddit.subreddit, 'flair_text': reddit.flair_text, 'description': reddit.description, 'comment': reddit.comment, 'lock': reddit.lock, 'lock_comment': reddit.lock_comment, 'ban': reddit.ban, 'ban_duration': reddit.ban_duration, 'ban_reddit': reddit.ban_reddit, 'ban_message': reddit.ban_message, 'ban_note': reddit.ban_note, 'usernote': reddit.usernote, 'usernote_note': reddit.usernote_note, 'usernote_warning_type': reddit.usernote_warning_type,
                  'enabled': reddit.enabled}
    return jsonify({'success': success, 'error': error, 'redditExists': redditExists, 'reddit': redditData}), 202

@reddit_api.route('/edit', methods=['POST'])
@login_required
@requiresAdmin
def editReddit():
    redditId = request.form['reddit_id']
    subreddit = request.form['subreddit']
    flair_text = request.form['flair_text']
    description = request.form['description']
    commentToggle = request.form['commentToggle'] == 'on'
    if commentToggle:
        commentInput = request.form['commentInput']
    else:
        commentInput = None
    lockToggle = request.form['lockToggle'] == 'true'
    commentLockToggle = request.form['commentLockToggle'] == 'on'
    banToggle = request.form['banToggle'] == 'true'
    if banToggle:
        ban_duration = request.form['ban_duration']
        ban_reddit = request.form['ban_reddit']
        ban_message = request.form['ban_message']
        ban_note = request.form['ban_note']
    else:
        ban_duration = None
        ban_reddit = None
        ban_message = None
        ban_note = None
    usernoteToggle = request.form['usernoteToggle'] == 'on'
    if usernoteToggle:
        usernote_note = request.form['usernote_note']
        usernote_warning_type = request.form['usernote_warning_type']
    else:
        usernote_note = None
        usernote_warning_type = None
    reddit = RemovalReddit.query.filter_by(id=redditId).first()
    notification = {'success': None, 'error': None}
    try:
        if reddit:
            reddit.subreddit = subreddit
            reddit.flair_text = flair_text.lower()
            reddit.description = description
            reddit.comment = commentInput
            reddit.lock = lockToggle
            reddit.lock_comment = commentLockToggle
            reddit.ban = banToggle
            reddit.ban_duration = ban_duration
            reddit.ban_reddit = ban_reddit
            reddit.ban_message = ban_message
            reddit.ban_note = ban_note
            reddit.usernote = usernoteToggle
            reddit.usernote_note = usernote_note
            reddit.usernote_warning_type = usernote_warning_type
            db.session.merge(reddit)
            redditEditType = 'Updated'
        else:
            reddit = RemovalReddit(subreddit=subreddit, flair_text=flair_text.lower(), description=description, comment=commentInput, lock=lockToggle, lock_comment=commentLockToggle, ban=banToggle, ban_duration=ban_duration, ban_reddit=ban_reddit, ban_message=ban_message, ban_note=ban_note, usernote=usernoteToggle, usernote_note=usernote_note, usernote_warning_type=usernote_warning_type)
            db.session.add(subreddit)
            redditEditType = 'Created'
        db.session.commit()

        notification['success'] = f'{redditEditType} "{reddit.flair_text}" for r/{reddit.subreddit} successfully!'
    except Exception as error:
        notification['error'] = error
    return jsonify({'notification': notification, 'reddit': reddit.flair_text}), 202

@reddit_api.route('/delete', methods=['POST'])
@login_required
@requiresAdmin
def deleteReddit():
    notification = {'success': None, 'error': None}
    redditId = request.form['reddit_id']
    reddit = RemovalReddit.query.filter_by(id=redditId).first()
    try:
        if reddit:
            db.session.delete(reddit)
            db.session.commit()
            notification['success'] = True
        else:
            notification['error'] = "That reddit isn't valid!"
    except Exception as error:
        notification['error'] = error
    return jsonify({'success': notification['success'], 'error': notification['error'], 'notification': notification, 'subreddit': reddit.subreddit, 'flair_text': reddit.flair_text}), 202

@reddit_api.route('/toggle', methods=['POST'])
@login_required
@requiresAdmin
def toggleReddit():
    redditId = request.form['id']
    notification = {'success': None, 'error': None}
    try:
        reddit = RemovalReddit.query.filter_by(id=redditId).first()
        reddit.enabled = not reddit.enabled
        db.session.merge(reddit)
        db.session.commit()
        notification['success'] = True
    except Exception as error:
        notification['error'] = error
    return jsonify({'success': notification['success'], 'error': notification['error'], 'id': redditId, 'enabled': reddit.enabled}), 202