"""
run.py — Application entry point.
Run this file to start the server: python3 run.py
"""
from flask import Flask
from flask_cors import CORS
from backend.config       import DEBUG, FRONTEND_DIR
from backend.routes.predict       import predict_bp
from backend.routes.static_routes import static_bp
from backend.utils.logger import logger


def create_app() -> Flask:
    """App factory — creates and configures the Flask application."""
    app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="/static")
    CORS(app)
    app.register_blueprint(predict_bp)
    app.register_blueprint(static_bp)
    return app


if __name__ == "__main__":
    app = create_app()
    logger.info("🚦 Smart Mobility Risk Predictor starting...")
    logger.info("   Open → http://127.0.0.1:5000")
    app.run(debug=DEBUG, port=5000)
from app import app

if __name__ == "__main__":
    app.run()