import logging

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_user, logout_user


log = logging.getLogger(__name__)
from app.modules.users.models import User
from app.modules.api_tokens.models import db


auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        try:
            user = User.query.filter(User.username.ilike(request.form['username'])).first()
            if user and user.password == password and user.is_active:
                login_user(user, remember=remember, fresh=False)
                return redirect(url_for('main.dash'))
            elif not user:
                return failLogin(password, username)
            elif not user.is_active:
                flash('Your account is disabled.', 'error')
                return render_template('login.html', username=username, password=password), 403
            else:
                return failLogin(password, username)
        except Exception as error:
            log.exception(error)
            flash('Login failed.')
    user = User.query.first()
    if not user:
        user = User(username='root', admin=True, password='password', created_by=None)
        db.session.add(user)
        db.session.commit()
        log.info(f"Created user: '{user.username}' successfully!")
    return render_template('login.html'), 200

def failLogin(password, username):
    flash('Please check your login details and try again.', 'error')
    return render_template('login.html', username=username, password=password), 403

@auth_blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))