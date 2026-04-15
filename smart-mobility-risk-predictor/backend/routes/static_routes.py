"""
static_routes.py — Serves the frontend HTML.
Keeps static file serving separate from API logic.
"""
from flask import Blueprint, send_from_directory
from backend.config import FRONTEND_DIR

static_bp = Blueprint("static", __name__)


@static_bp.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")
