from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
import random

app = Flask(__name__)
CORS(app)

# ── API Keys ──────────────────────────────────────────────────────────
# Free OpenWeatherMap key: https://openweathermap.org/api
# Free Hugging Face key:   https://huggingface.co/settings/tokens
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
HF_API_KEY          = os.environ.get("HF_API_KEY", "")

# Hugging Face model for AI report generation
HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"


# ── Weather ───────────────────────────────────────────────────────────
def get_weather(lat, lon):
    if OPENWEATHER_API_KEY:
        try:
            url = (f"https://api.openweathermap.org/data/2.5/weather"
                   f"?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric")
            r = requests.get(url, timeout=5)
            r.raise_for_status()
            d = r.json()
            return {
                "temperature": round(d["main"]["temp"], 1),
                "feels_like":  round(d["main"]["feels_like"], 1),
                "humidity":    d["main"]["humidity"],
                "wind_speed":  round(d["wind"]["speed"], 1),
                "condition":   d["weather"][0]["main"],
                "description": d["weather"][0]["description"],
                "icon":        d["weather"][0]["icon"],
                "source": "live"
            }
        except Exception:
            pass

    # Simulated fallback
    conditions = [
        ("Clear","clear sky","01d"),("Clouds","scattered clouds","03d"),
        ("Rain","moderate rain","10d"),("Thunderstorm","thunderstorm","11d"),
        ("Drizzle","light drizzle","09d"),("Snow","light snow","13d"),("Fog","dense fog","50d"),
    ]
    cond, desc, icon = random.choice(conditions)
    return {
        "temperature": round(random.uniform(15, 38), 1),
        "feels_like":  round(random.uniform(14, 40), 1),
        "humidity":    random.randint(30, 95),
        "wind_speed":  round(random.uniform(0, 15), 1),
        "condition":   cond, "description": desc, "icon": icon,
        "source": "simulated"
    }


# ── Risk engine ───────────────────────────────────────────────────────
WEATHER_RISK = {
    "Thunderstorm":40,"Snow":35,"Fog":30,"Rain":25,
    "Drizzle":15,"Clouds":5,"Clear":0
}

def score_breakdown(traffic, time_hour, weather, is_weekend):
    # Small realistic randomness (±3 pts) so repeated calls feel dynamic
    jitter = random.uniform(-3, 3)

    traffic_pts = min(traffic * 8, 40)

    if   7  <= time_hour <= 9:  time_pts = 30
    elif 17 <= time_hour <= 20: time_pts = 30
    elif time_hour >= 22 or time_hour <= 5: time_pts = 20
    else: time_pts = 5

    weather_pts = WEATHER_RISK.get(weather["condition"], 10)
    if weather["wind_speed"] > 10:  weather_pts += 15
    elif weather["wind_speed"] > 6: weather_pts += 8
    if weather["humidity"] > 85:    weather_pts += 8

    weekend_discount = -10 if is_weekend else 0
    raw   = traffic_pts + time_pts + weather_pts + weekend_discount + jitter
    total = min(max(round(raw), 0), 100)

    # Percentage contributions (of raw positive score, ignoring discount)
    pos_total = max(traffic_pts + time_pts + weather_pts, 1)
    return {
        "total":          total,
        "traffic":        round(traffic_pts),
        "time":           round(time_pts),
        "weather":        round(min(weather_pts, 40)),
        "weekend":        round(weekend_discount),
        "pct_traffic":    round(traffic_pts  / pos_total * 100),
        "pct_time":       round(time_pts     / pos_total * 100),
        "pct_weather":    round(min(weather_pts, 40) / pos_total * 100),
    }

def risk_label(score):
    if score < 30: return ("Low",      "Safe to travel. Roads look clear.",          "🟢")
    if score < 55: return ("Moderate", "Stay alert. Some risk factors present.",     "🟡")
    if score < 75: return ("High",     "Drive carefully. Conditions are difficult.", "🟠")
    return              ("Critical",   "Avoid travel if possible. High danger.",     "🔴")


# ── Hugging Face AI report ────────────────────────────────────────────
def generate_ai_report(traffic, time_hour, weather, score, level, breakdown):
    if not HF_API_KEY:
        # Fallback rule-based report
        factors = []
        if breakdown["traffic"] >= 24: factors.append("heavy traffic congestion")
        if breakdown["time"] >= 25:    factors.append("peak rush hour conditions")
        if breakdown["weather"] >= 20: factors.append(f"hazardous {weather['condition'].lower()}")
        if weather["wind_speed"] > 10: factors.append("strong winds")
        if not factors: factors.append("generally clear conditions")
        joined = ", ".join(factors[:-1]) + (" and " if len(factors)>1 else "") + factors[-1]
        return (f"Current mobility risk is {level} ({score}/100). "
                f"Primary factors: {joined}. "
                f"Temperature is {weather['temperature']}°C with {weather['description']}. "
                f"{'Recommend delaying travel.' if score >= 75 else 'Exercise appropriate caution.'}")

    prompt = f"""<s>[INST] You are a smart mobility AI assistant. Generate a concise 2-sentence travel risk report.

Data:
- Risk Score: {score}/100 ({level})
- Traffic Level: {traffic}/5
- Time: {time_hour}:00
- Weather: {weather['condition']}, {weather['temperature']}°C, wind {weather['wind_speed']} m/s, humidity {weather['humidity']}%
- Breakdown: Traffic={breakdown['traffic']}pts, Time={breakdown['time']}pts, Weather={breakdown['weather']}pts

Write a professional, actionable 2-sentence report for a driver. Be specific about the conditions. [/INST]"""

    try:
        r = requests.post(
            f"https://api-inference.huggingface.co/models/{HF_MODEL}",
            headers={"Authorization": f"Bearer {HF_API_KEY}"},
            json={"inputs": prompt, "parameters": {"max_new_tokens": 120, "temperature": 0.6}},
            timeout=15
        )
        r.raise_for_status()
        result = r.json()
        if isinstance(result, list) and result:
            text = result[0].get("generated_text", "")
            # Extract only the response after [/INST]
            if "[/INST]" in text:
                text = text.split("[/INST]")[-1].strip()
            return text[:400]
    except Exception:
        pass

    return (f"Risk level is {level} at {score}/100 due to current conditions. "
            f"Weather shows {weather['description']} at {weather['temperature']}°C.")


# ── Hourly forecast (best time to travel) ────────────────────────────
def hourly_forecast(traffic, weather, is_weekend):
    """Generate risk scores for next 12 hours from now."""
    current_hour = __import__('datetime').datetime.now().hour
    forecast = []
    for i in range(12):
        h = (current_hour + i) % 24
        # Slightly vary weather for realism
        sim_weather = dict(weather)
        sim_weather["wind_speed"] = max(0, weather["wind_speed"] + random.uniform(-2, 2))
        sim_weather["humidity"]   = min(100, max(0, weather["humidity"] + random.randint(-5, 5)))
        bd = score_breakdown(traffic, h, sim_weather, is_weekend)
        label, _, emoji = risk_label(bd["total"])
        forecast.append({
            "hour":  h,
            "score": bd["total"],
            "level": label,
            "emoji": emoji
        })
    return forecast


# ── Routes ────────────────────────────────────────────────────────────
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')


@app.route('/predict', methods=['POST'])
def predict():
    data       = request.get_json(force=True)
    traffic    = float(data.get("traffic_level", 3))
    time_hour  = int(data.get("time_hour", 12))
    lat        = float(data.get("lat", 0))
    lon        = float(data.get("lon", 0))
    is_weekend = bool(data.get("is_weekend", False))

    weather    = get_weather(lat, lon)
    breakdown  = score_breakdown(traffic, time_hour, weather, is_weekend)
    score      = breakdown["total"]
    level, advice, emoji = risk_label(score)
    ai_report  = generate_ai_report(traffic, time_hour, weather, score, level, breakdown)
    forecast   = hourly_forecast(traffic, weather, is_weekend)

    # Best hour = lowest score in forecast
    best       = min(forecast, key=lambda x: x["score"])

    return jsonify({
        "risk_score":   score,
        "risk_level":   level,
        "risk_emoji":   emoji,
        "advice":       advice,
        "ai_report":    ai_report,
        "breakdown":    breakdown,
        "weather":      weather,
        "forecast":     forecast,
        "best_time":    best,
        "hf_enabled":   bool(HF_API_KEY),
        "inputs": {
            "traffic_level": traffic,
            "time_hour":     time_hour,
            "is_weekend":    is_weekend
        }
    })


if __name__ == '__main__':
    print(f"🚦 Starting → http://127.0.0.1:5000")
    print(f"   Weather : {'LIVE' if OPENWEATHER_API_KEY else 'simulated'}")
    print(f"   AI      : {'Hugging Face ON' if HF_API_KEY else 'rule-based fallback'}")
    app.run(debug=True)
