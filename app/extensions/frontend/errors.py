from flask import render_template


def unauthorizedError(error):
    return render_template('errors/403.html', error=error), 403

def notFoundError(error):
    return render_template('errors/404.html', error=error), 404