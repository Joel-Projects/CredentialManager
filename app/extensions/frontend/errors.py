from flask import render_template


def unauthorized_error(error):
    return render_template("errors/403.html", error=error), 403


def not_found_error(error):
    return render_template("errors/404.html", error=error), 404
