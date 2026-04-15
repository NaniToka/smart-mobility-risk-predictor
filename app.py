from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"message": "Running 🚀"})

@app.route("/predict", methods=["POST"])
def predict():
    return jsonify({
        "risk_score": 50,
        "risk_level": "Medium",
        "advice": "Be careful",
        "reason": "Test response",
        "weather": {
            "temperature": 25,
            "condition": "Clear"
        }
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
