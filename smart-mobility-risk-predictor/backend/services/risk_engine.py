"""
risk_engine.py — Core risk calculation module.
Computes weighted risk scores from traffic, time, and weather inputs.
All scoring logic lives here — easy to tune weights without touching routes.
"""
import random
import datetime

# ── Weather risk weights ──────────────────────────────────────────────
WEATHER_RISK: dict[str, int] = {
    "Thunderstorm": 40,
    "Snow":         35,
    "Fog":          30,
    "Rain":         25,
    "Drizzle":      15,
    "Clouds":        5,
    "Clear":         0,
}


def score_breakdown(
    traffic: float,
    time_hour: int,
    weather: dict,
    is_weekend: bool
) -> dict:
    """
    Returns a full breakdown dict with:
      total, traffic pts, time pts, weather pts,
      weekend discount, and % contribution of each factor.
    """
    jitter = random.uniform(-3, 3)  # ±3 pt realism noise

    # 1. Traffic (0–5 scale → 0–40 pts)
    traffic_pts = min(traffic * 8, 40)

    # 2. Time of day
    if   7  <= time_hour <= 9:              time_pts = 30  # morning rush
    elif 17 <= time_hour <= 20:             time_pts = 30  # evening rush
    elif time_hour >= 22 or time_hour <= 5: time_pts = 20  # night
    else:                                   time_pts = 5

    # 3. Weather condition + wind + humidity
    weather_pts = WEATHER_RISK.get(weather["condition"], 10)
    if   weather["wind_speed"] > 10: weather_pts += 15
    elif weather["wind_speed"] > 6:  weather_pts += 8
    if   weather["humidity"]   > 85: weather_pts += 8

    # 4. Weekend discount
    weekend_discount = -10 if is_weekend else 0

    raw   = traffic_pts + time_pts + weather_pts + weekend_discount + jitter
    total = min(max(round(raw), 0), 100)

    # Percentage contributions (positive factors only)
    pos_total = max(traffic_pts + time_pts + weather_pts, 1)
    return {
        "total":       total,
        "traffic":     round(traffic_pts),
        "time":        round(time_pts),
        "weather":     round(min(weather_pts, 40)),
        "weekend":     round(weekend_discount),
        "pct_traffic": round(traffic_pts              / pos_total * 100),
        "pct_time":    round(time_pts                 / pos_total * 100),
        "pct_weather": round(min(weather_pts, 40)     / pos_total * 100),
    }


def risk_label(score: int) -> tuple[str, str, str]:
    """Maps a numeric score to (level, advice, emoji)."""
    if score < 30: return ("Low",      "Safe to travel. Roads look clear.",          "🟢")
    if score < 55: return ("Moderate", "Stay alert. Some risk factors present.",     "🟡")
    if score < 75: return ("High",     "Drive carefully. Conditions are difficult.", "🟠")
    return              ("Critical",   "Avoid travel if possible. High danger.",     "🔴")


def hourly_forecast(
    traffic: float,
    weather: dict,
    is_weekend: bool,
    hours: int = 12
) -> list[dict]:
    """
    Generates a risk forecast for the next `hours` hours.
    Slightly varies weather per hour for realism.
    """
    current_hour = datetime.datetime.now().hour
    forecast = []
    for i in range(hours):
        h = (current_hour + i) % 24
        sim_weather = dict(weather)
        sim_weather["wind_speed"] = max(0, weather["wind_speed"] + random.uniform(-2, 2))
        sim_weather["humidity"]   = min(100, max(0, weather["humidity"] + random.randint(-5, 5)))
        bd = score_breakdown(traffic, h, sim_weather, is_weekend)
        label, _, emoji = risk_label(bd["total"])
        forecast.append({"hour": h, "score": bd["total"], "level": label, "emoji": emoji})
    return forecast
