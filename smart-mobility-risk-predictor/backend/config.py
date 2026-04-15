"""
config.py — Central configuration for the backend.
All environment variables and constants live here.
Import this module anywhere you need a setting.
"""
import os

# ── API Keys ──────────────────────────────────────────────────────────
# Set these before running:
#   export OPENWEATHER_API_KEY="your_key"
#   export HF_API_KEY="your_key"
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
HF_API_KEY          = os.environ.get("HF_API_KEY", "")

# ── Hugging Face ──────────────────────────────────────────────────────
HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

# ── App settings ──────────────────────────────────────────────────────
DEBUG        = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
