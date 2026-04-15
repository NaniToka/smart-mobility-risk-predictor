"""
ai_service.py — Hugging Face AI report generation module.
Calls Mistral-7B via HF Inference API to generate natural language risk reports.
Falls back to a rule-based report if no API key is configured.
"""

import requests
from typing import Optional
from backend.config import HF_API_KEY, HF_API_URL


def generate_ai_report(
    traffic: float,
    time_hour: int,
    weather: dict,
    score: int,
    level: str,
    breakdown: dict
) -> str:
    """
    Returns a travel risk report.
    Uses Hugging Face if HF_API_KEY is set, otherwise rule-based fallback.
    """
    if HF_API_KEY:
        report = _call_huggingface(traffic, time_hour, weather, score, level, breakdown)
        if report:
            return report

    return _rule_based_report(weather, score, level, breakdown)


# ✅ FIXED HERE (Python 3.9 compatible)
def _call_huggingface(
    traffic, time_hour, weather, score, level, breakdown
) -> Optional[str]:

    prompt = (
        f"<s>[INST] You are a smart mobility AI assistant. "
        f"Generate a concise 2-sentence travel risk report.\n\n"
        f"Data:\n"
        f"- Risk Score: {score}/100 ({level})\n"
        f"- Traffic Level: {traffic}/5\n"
        f"- Time: {time_hour}:00\n"
        f"- Weather: {weather.get('condition', 'Unknown')}, {weather.get('temperature', 0)}°C, "
        f"wind {weather.get('wind_speed', 0)} m/s, humidity {weather.get('humidity', 0)}%\n"
        f"- Breakdown: Traffic={breakdown.get('traffic', 0)}pts, "
        f"Time={breakdown.get('time', 0)}pts, Weather={breakdown.get('weather', 0)}pts\n\n"
        f"Write a professional, actionable 2-sentence report for a driver. [/INST]"
    )

    try:
        r = requests.post(
            HF_API_URL,
            headers={"Authorization": f"Bearer {HF_API_KEY}"},
            json={
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 120,
                    "temperature": 0.6
                }
            },
            timeout=15,
        )

        r.raise_for_status()
        result = r.json()

        if isinstance(result, list) and len(result) > 0:
            text = result[0].get("generated_text", "")

            if "[/INST]" in text:
                text = text.split("[/INST]")[-1].strip()

            return text[:400] if text else None

    except Exception as e:
        print("HF API Error:", e)
        return None


def _rule_based_report(weather, score, level, breakdown) -> str:
    factors = []

    if breakdown.get("traffic", 0) >= 24:
        factors.append("heavy traffic congestion")

    if breakdown.get("time", 0) >= 25:
        factors.append("peak rush hour conditions")

    if breakdown.get("weather", 0) >= 20:
        factors.append(f"hazardous {weather.get('condition', 'conditions').lower()}")

    if weather.get("wind_speed", 0) > 10:
        factors.append("strong winds")

    if not factors:
        factors.append("generally clear conditions")

    # Join nicely
    if len(factors) == 1:
        joined = factors[0]
    else:
        joined = ", ".join(factors[:-1]) + " and " + factors[-1]

    action = "Recommend delaying travel." if score >= 75 else "Exercise appropriate caution."

    return (
        f"Current mobility risk is {level} ({score}/100). "
        f"Primary factors: {joined}. "
        f"Temperature is {weather.get('temperature', 0)}°C with {weather.get('description', 'clear weather')}. "
        f"{action}"
    )