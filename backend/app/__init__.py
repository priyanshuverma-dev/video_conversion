# app/__init__.py
from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config["UPLOAD_FOLDER"] = "app/static/uploads"

    from .routes import bp as routes_bp

    app.register_blueprint(routes_bp)

    return app
