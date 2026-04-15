"""
predict.py — /predict route blueprint.
Handles POST /predict requests, orchestrates all services,
and returns the full JSON response to the frontend.
"""
from flask import Blueprint, request, jsonify
from backend.services.weather_service import get_weather
from backend.services.risk_engine     import score_breakdown, risk_label, hourly_forecast
from backend.services.ai_service      import generate_ai_report

predict_bp = Blueprint("predict", __name__)


@predict_bp.route("/predict", methods=["POST"])
def predict():
    data       = request.get_json(force=True)
    traffic    = float(data.get("traffic_level", 3))
    time_hour  = int(data.get("time_hour", 12))
    lat        = float(data.get("lat", 0))
    lon        = float(data.get("lon", 0))
    is_weekend = bool(data.get("is_weekend", False))

    weather   = get_weather(lat, lon)
    breakdown = score_breakdown(traffic, time_hour, weather, is_weekend)
    score     = breakdown["total"]
    level, advice, emoji = risk_label(score)
    ai_report = generate_ai_report(traffic, time_hour, weather, score, level, breakdown)
    forecast  = hourly_forecast(traffic, weather, is_weekend)
    best_time = min(forecast, key=lambda x: x["score"])

    return jsonify({
        "risk_score":  score,
        "risk_level":  level,
        "risk_emoji":  emoji,
        "advice":      advice,
        "ai_report":   ai_report,
        "breakdown":   breakdown,
        "weather":     weather,
        "forecast":    forecast,
        "best_time":   best_time,
        "inputs": {
            "traffic_level": traffic,
            "time_hour":     time_hour,
            "is_weekend":    is_weekend,
        },
    })
