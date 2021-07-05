from app.extensions.api import api_v1


def init_app(app, **kwargs):
    """
    Init users module.
    """
    from . import converters, models, resources, views

    api_v1.add_namespace(resources.api)
    app.url_map.converters["User"] = converters.UserConverter
    app.register_blueprint(views.usersBlueprint)
