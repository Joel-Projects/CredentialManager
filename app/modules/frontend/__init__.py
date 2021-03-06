"""
Front End module
============
"""


def init_app(app, **kwargs):
    """
    Init main frontend module.
    """

    from . import views

    app.register_blueprint(views.main)
