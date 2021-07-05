import logging

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_user, logout_user

log = logging.getLogger(__name__)
from app.modules.api_tokens.models import db
from app.modules.users.models import User

auth_blueprint = Blueprint("auth", __name__)


@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        remember = True if request.form.get("remember") else False
        try:
            user = User.query.filter(
                User.username.ilike(request.form["username"])
            ).first()
            if user and user.password == password and user.is_active:
                login_user(user, remember=remember, fresh=False)
                return redirect(url_for("main.dash"))
            elif not user:
                return failLogin(password, username)
            elif not user.is_active:
                flash("Your account is disabled.", "error")
                return (
                    render_template("login.html", username=username, password=password),
                    403,
                )
            else:  # pragma: no cover
                return failLogin(password, username)
        except Exception as error:  # pragma: no cover
            log.exception(error)
            flash("Login failed.")
    user = User.query.first()
    if not user:
        return redirect(url_for("auth.initial_user"))
    return render_template("login.html"), 200


@auth_blueprint.route("/create_initial_user", methods=["GET", "POST"])
def initial_user():
    user = User.query.first()
    if not user:
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            user = User(username=username, password=password)
            user.is_internal = True
            user.is_active = True
            user.is_regular_user = True
            db.session.add(user)
            newUser = User.query.first()
            if newUser:
                log.info(f"Created user: '{user.username}' successfully!")
                login_user(newUser)
            return redirect(url_for("main.dash"))
        return render_template("create_initial_user.html"), 200
    abort(404)


def failLogin(password, username):
    flash("Please check your login details and try again.", "error")
    return render_template("login.html", username=username, password=password), 403


@auth_blueprint.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
