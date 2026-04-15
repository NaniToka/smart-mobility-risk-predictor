<div align="center">

# 🚦 Smart Mobility Risk Predictor

### AI-Powered Travel Risk Analysis · Real-Time Weather · Interactive Maps

[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-black?style=flat-square&logo=flask)](https://flask.palletsprojects.com)
[![Leaflet](https://img.shields.io/badge/Leaflet.js-1.9-green?style=flat-square&logo=leaflet)](https://leafletjs.com)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Mistral--7B-yellow?style=flat-square&logo=huggingface)](https://huggingface.co)
[![License](https://img.shields.io/badge/License-MIT-purple?style=flat-square)](LICENSE)

</div>

---

## 🌍 Problem & Solution

**Problem:** Every day, millions of people make travel decisions without knowing the real risk on the road. Traffic congestion, bad weather, and peak hours combine to create dangerous conditions — yet most navigation apps only show routes, not risk.

**Solution:** Smart Mobility Risk Predictor analyses real-time weather, traffic level, and time of day to generate an AI-powered risk score (0–100) for any location on Earth. It tells you *whether* to travel, not just *how* to travel.

---

## ✨ Key Features

- 🤖 **AI Risk Reports** — Hugging Face Mistral-7B generates natural language explanations of risk factors
- 🗺 **Interactive Map** — Click any point on the globe to instantly set your location
- 🔍 **City Search** — Nominatim-powered search with live autocomplete suggestions
- 🎤 **Voice Input** — Say a city name and the app navigates and predicts automatically
- 🌦 **Live Weather** — OpenWeatherMap integration with simulated fallback
- 📊 **Risk Breakdown** — Visual bars showing Traffic %, Weather %, Time % contribution
- 📈 **Chart.js History** — Line chart of your last 6 predictions over time
- ⏱ **12-Hour Forecast** — Hourly risk grid to find the safest travel window
- 🗺 **Route A→B Mode** — Set start and end points, get midpoint risk analysis
- 🔴 **Live Mode** — Auto-refreshes every 60 seconds with a pulsing indicator
- 📸 **Export PNG** — Save your risk report as an image
- 💾 **Persistent History** — localStorage keeps your last 6 predictions across sessions
- 📱 **Responsive Design** — Side-by-side desktop layout, stacked on mobile

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3 (Glassmorphism), Vanilla JavaScript |
| Maps | Leaflet.js 1.9 + OpenStreetMap tiles |
| Charts | Chart.js 4.4 |
| Backend | Python 3.10+, Flask 3.0, Flask-CORS |
| AI / NLP | Hugging Face Inference API (Mistral-7B-Instruct) |
| Weather | OpenWeatherMap API (live) + simulated fallback |
| Geocoding | Nominatim (OpenStreetMap) — free, no key needed |
| Voice | Web Speech API (browser-native) |
| Export | html2canvas |

---

## 🏗 Architecture

```
User (Browser)
     │
     │  Click map / Search / Voice / Form input
     ▼
┌─────────────────────────────────────┐
│           Frontend (index.html)     │
│  Leaflet Map · Chart.js · Fetch API │
└──────────────┬──────────────────────┘
               │  POST /predict  { lat, lon, traffic, time }
               ▼
┌─────────────────────────────────────┐
│         Flask Backend (run.py)      │
│                                     │
│  routes/predict.py                  │
│       │                             │
│       ├── weather_service.py ──────►│ OpenWeatherMap API
│       │                             │
│       ├── risk_engine.py            │ (pure calculation, no I/O)
│       │                             │
│       └── ai_service.py ──────────►│ Hugging Face API
│                                     │
└──────────────┬──────────────────────┘
               │  JSON response
               ▼
┌─────────────────────────────────────┐
│  Frontend renders:                  │
│  Gauge · Breakdown · AI Report      │
│  Forecast · Chart · Toast Alert     │
└─────────────────────────────────────┘
```

---

## 📁 Project Structure

```
smart-mobility-risk-predictor/
│
├── run.py                          ← entry point
├── requirements.txt
├── .env.example                    ← API key template
│
├── frontend/
│   └── index.html                  ← complete UI
│
├── backend/
│   ├── config.py                   ← env vars & constants
│   ├── routes/
│   │   ├── predict.py              ← POST /predict blueprint
│   │   └── static_routes.py        ← GET / serves frontend
│   ├── services/
│   │   ├── weather_service.py      ← OpenWeatherMap + fallback
│   │   ├── risk_engine.py          ← scoring logic & forecast
│   │   └── ai_service.py           ← Hugging Face + rule-based
│   └── utils/
│       ├── validators.py           ← input validation
│       └── logger.py               ← centralised logging
│
└── data/
    └── sample_predictions.json     ← demo data
```

---

## 🚀 Getting Started

### 1. Clone & install

```bash
git clone https://github.com/your-username/smart-mobility-risk-predictor.git
cd smart-mobility-risk-predictor
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Set API keys (optional but recommended)

```bash
cp .env.example .env
# Edit .env and add your keys:
#   OPENWEATHER_API_KEY  →  https://openweathermap.org/api  (free)
#   HF_API_KEY           →  https://huggingface.co/settings/tokens  (free)
source .env
```

> The app works fully without keys — weather and AI reports fall back to realistic simulation.

### 3. Run

```bash
python3 run.py
```

Open **http://127.0.0.1:5000** in your browser.

---

## ⚙️ How It Works

1. **Set location** — Click the map, search a city, use GPS, or type coordinates manually
2. **Set conditions** — Adjust traffic level (0–5), hour of day, and weekend toggle
3. **Predict** — Frontend sends `POST /predict` with `{ lat, lon, traffic_level, time_hour }`
4. **Weather fetch** — `weather_service.py` calls OpenWeatherMap (or simulates if no key)
5. **Risk calculation** — `risk_engine.py` applies weighted formula: Traffic (up to 40pts) + Time (up to 30pts) + Weather (up to 40pts) ± jitter
6. **AI report** — `ai_service.py` sends context to Mistral-7B on Hugging Face, gets a 2-sentence natural language report
7. **Forecast** — Risk is calculated for the next 12 hours with slight weather variation per hour
8. **Response** — Flask returns full JSON: score, level, breakdown, weather, forecast, best time
9. **Render** — Frontend animates the gauge, draws breakdown bars, types out the AI report, updates the chart

---

## 📡 API Reference

### `POST /predict`

**Request**
```json
{
  "traffic_level": 3,
  "time_hour": 18,
  "lat": 40.7128,
  "lon": -74.0060,
  "is_weekend": false
}
```

**Response**
```json
{
  "risk_score": 68,
  "risk_level": "High",
  "risk_emoji": "🟠",
  "advice": "Drive carefully. Conditions are difficult.",
  "ai_report": "Risk is elevated due to peak rush hour and wet roads from rain...",
  "breakdown": {
    "total": 68,
    "traffic": 24, "time": 30, "weather": 25,
    "pct_traffic": 42, "pct_time": 35, "pct_weather": 23
  },
  "weather": {
    "temperature": 18.4, "feels_like": 16.1,
    "humidity": 78, "wind_speed": 5.2,
    "condition": "Rain", "source": "live"
  },
  "forecast": [ { "hour": 18, "score": 68, "level": "High", "emoji": "🟠" }, "..." ],
  "best_time": { "hour": 11, "score": 22, "level": "Low", "emoji": "🟢" }
}
```

---

## 🖼 Screenshots

### Main UI — Input Panel
![Main UI](docs/screenshots/main-ui.png)
*Side-by-side layout: input form with interactive map on the left*

### Risk Result — AI Report & Gauge
![Risk Result](docs/screenshots/risk-result.png)
*Animated gauge, weather strip, AI-generated report with typewriter effect*

### 12-Hour Forecast & Chart
![Forecast](docs/screenshots/forecast-chart.png)
*Hourly risk grid and Chart.js prediction history*

> 📸 Add your own screenshots to `docs/screenshots/`

---

## 🔮 Future Improvements

- **ML model** — Train a real regression model on historical accident + weather data for higher accuracy
- **Live traffic API** — Integrate Google Maps Traffic or HERE API for real congestion data
- **Route risk** — Full A→B route analysis with per-segment risk heatmap overlay on the map
- **Push alerts** — Browser notifications when risk at a saved location exceeds a threshold
- **Mobile app** — React Native or Flutter wrapper for iOS/Android
- **Multi-language** — i18n support for global hackathon audiences
- **Dashboard** — Admin view showing aggregate risk trends across cities over time

---

## 💡 Project Value

This project addresses a real-world problem at the intersection of **smart cities**, **road safety**, and **AI**. By combining live environmental data with machine learning-style scoring, it gives everyday commuters actionable intelligence before they get in a car.

**Real-world impact:**
- Reduces accident risk by helping drivers make informed decisions
- Scalable to city-level dashboards for traffic management authorities
- Foundation for insurance telematics and fleet risk management systems
- Demonstrates how open APIs (weather, maps, AI) can be combined into a meaningful civic tool

---

## 👤 Author

**[Your Name]**
Built for [Hackathon Name] · [Year]

- GitHub: [@your-username](https://github.com/your-username)
- LinkedIn: [your-linkedin](https://linkedin.com/in/your-linkedin)

---

## 📄 License

MIT — free to use, modify, and distribute.

---

<div align="center">
  <sub>Built with ❤️ using Flask · Leaflet · Hugging Face · OpenWeatherMap</sub>
</div>
