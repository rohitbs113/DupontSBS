from flask import Flask
from flask import Blueprint


def create_app(debug=False):
    """
    sbs application factory
    """

    app_instance = Flask(__name__)
    app_instance.debug = debug

    sbs_blueprint = Blueprint('sbs_blueprint', __name__)

    app_instance.register_blueprint(sbs_blueprint)
    return app_instance
