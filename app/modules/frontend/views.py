import logging

from flask import Blueprint, redirect, render_template
from flask_login import current_user, login_required


log = logging.getLogger(__name__)

main = Blueprint("main", __name__)


@main.route("/")
def root():
    if current_user.is_authenticated:
        return render_template("dash.html")
    else:
        return redirect("/login")


@main.route("/dash")
@login_required
def dash():
    return render_template("dash.html")
