from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"message": "Smart Mobility Risk Predictor Running 🚀"})

@app.route("/predict", methods=["POST"])
def predict():
    return jsonify({
        "risk_score": 60,
        "risk_level": "Medium",
        "advice": "Drive carefully",
        "reason": "Moderate traffic and weather conditions",
        "weather": {
            "temperature": 28,
            "condition": "Cloudy"
        }
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
