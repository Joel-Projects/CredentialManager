from flask import Blueprint

from app.extensions import api


def init_app(app, **kwargs):
    api_v1_blueprint = Blueprint("api", __name__, url_prefix="/api/v1")
    api.api_v1.init_app(api_v1_blueprint)
    app.register_blueprint(api_v1_blueprint)
