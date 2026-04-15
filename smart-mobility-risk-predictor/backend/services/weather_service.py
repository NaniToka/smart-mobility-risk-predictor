"""
weather_service.py — Weather data module.
Fetches live weather from OpenWeatherMap API.
Falls back to realistic simulated data if no API key is set.
"""
import random
import requests
from backend.config import OPENWEATHER_API_KEY


def get_weather(lat: float, lon: float) -> dict:
    """
    Returns weather data for the given coordinates.
    Source will be 'live' or 'simulated'.
    """
    if OPENWEATHER_API_KEY:
        try:
            url = (
                f"https://api.openweathermap.org/data/2.5/weather"
                f"?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
            )
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
                "source":      "live",
            }
        except Exception:
            pass  # fall through to simulation

    return _simulate_weather()


def _simulate_weather() -> dict:
    """Generates realistic random weather when no API key is available."""
    conditions = [
        ("Clear",        "clear sky",        "01d"),
        ("Clouds",       "scattered clouds", "03d"),
        ("Rain",         "moderate rain",    "10d"),
        ("Thunderstorm", "thunderstorm",     "11d"),
        ("Drizzle",      "light drizzle",    "09d"),
        ("Snow",         "light snow",       "13d"),
        ("Fog",          "dense fog",        "50d"),
    ]
    cond, desc, icon = random.choice(conditions)
    return {
        "temperature": round(random.uniform(15, 38), 1),
        "feels_like":  round(random.uniform(14, 40), 1),
        "humidity":    random.randint(30, 95),
        "wind_speed":  round(random.uniform(0, 15), 1),
        "condition":   cond,
        "description": desc,
        "icon":        icon,
        "source":      "simulated",
    }
