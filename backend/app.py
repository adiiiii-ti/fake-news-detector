"""
Fake News & AI Content Detector — Flask API Server
Endpoints:
  POST /api/analyze          — Analyze text for fake news + AI detection
  GET  /api/health           — Health check
"""

import os
import sys
import joblib
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from ai_detector import AIContentDetector

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
CORS(app)

# ---------------------------------------------------------------------------
# Load models on startup
# ---------------------------------------------------------------------------

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "fake_news_model.pkl")

fake_news_model = None
ai_detector = AIContentDetector()


def load_fake_news_model():
    global fake_news_model
    if os.path.exists(MODEL_PATH):
        fake_news_model = joblib.load(MODEL_PATH)
        print("✅ Fake news detection model loaded successfully.")
    else:
        print("⚠️  Model file not found. Run train_model.py first.")
        print(f"   Expected at: {MODEL_PATH}")


# ---------------------------------------------------------------------------
# Frontend Route
# ---------------------------------------------------------------------------

@app.route("/")
def serve_frontend():
    return send_from_directory(FRONTEND_DIR, "index.html")


# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "fake_news_model_loaded": fake_news_model is not None,
    })


@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided in request body."}), 400

    text = ""
    if "url" in data and data["url"].strip():
        url = data["url"].strip()
        try:
            import requests
            from bs4 import BeautifulSoup
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Remove scripts, styles, metadata
            for script in soup(["script", "style", "meta", "noscript", "header", "footer"]):
                script.extract()
                
            text = soup.get_text(separator=" ", strip=True)
            if len(text) < 50:
                raise ValueError("Could not extract enough meaningful text from the page.")
        except Exception as e:
            return jsonify({"error": f"Failed to extract text from URL: {str(e)}"}), 400
    elif "text" in data and data["text"].strip():
        text = data["text"].strip()
    else:
        return jsonify({"error": "Please provide either 'text' or 'url' in the request."}), 400

    if len(text) < 20:
        return jsonify({"error": "Text is too short for meaningful analysis. Please provide at least 20 characters."}), 400

    result = {}

    # --- Fake News Detection ---
    if fake_news_model is not None:
        proba = fake_news_model.predict_proba([text])[0]
        fake_prob = float(proba[1])  # probability of being fake
        real_prob = float(proba[0])

        fake_score = int(fake_prob * 100)

        if fake_score >= 60:
            fake_verdict = "FAKE NEWS"
            fake_confidence = "high"
        elif fake_score >= 45:
            fake_verdict = "LIKELY FAKE"
            fake_confidence = "medium"
        elif fake_score >= 30:
            fake_verdict = "LIKELY REAL"
            fake_confidence = "medium"
        else:
            fake_verdict = "REAL NEWS"
            fake_confidence = "high"

        # Generate explanation
        fake_indicators = []
        text_upper_ratio = sum(1 for c in text if c.isupper()) / max(1, len(text))
        if text_upper_ratio > 0.3:
            fake_indicators.append("• Excessive use of capital letters, commonly seen in sensationalist fake news.")
        if any(word in text.upper() for word in ["BREAKING", "SHOCKING", "EXPOSED", "BOMBSHELL", "URGENT", "ALERT", "EXCLUSIVE", "REVEALED"]):
            fake_indicators.append("• Contains sensationalist keywords (BREAKING, SHOCKING, etc.) often used in fake news.")
        if "!" in text and text.count("!") >= 2:
            fake_indicators.append("• Multiple exclamation marks suggest sensationalism.")
        if fake_score < 30:
            fake_indicators.append("• The writing style, vocabulary, and structure are consistent with legitimate news reporting.")
        if not fake_indicators:
            if fake_score >= 45:
                fake_indicators.append("• The language patterns and claims in this text resemble known fake news patterns.")
            else:
                fake_indicators.append("• No strong fake news indicators detected.")

        result["fake_news"] = {
            "score": fake_score,
            "verdict": fake_verdict,
            "confidence": fake_confidence,
            "details": "\n".join(fake_indicators),
        }
    else:
        result["fake_news"] = {
            "score": -1,
            "verdict": "Model Not Loaded",
            "confidence": "none",
            "details": "The fake news detection model is not loaded. Please run train_model.py first.",
        }

    # --- AI Content Detection ---
    ai_result = ai_detector.analyze(text)
    result["ai_detection"] = ai_result

    # --- Overall Assessment ---
    if fake_news_model is not None:
        overall_score = int(0.5 * result["fake_news"]["score"] + 0.5 * result["ai_detection"]["score"])
    else:
        overall_score = result["ai_detection"]["score"]

    if overall_score >= 60:
        overall_verdict = "FAKE/AI NEWS"
        overall_label = "This news appears to be Fake or AI-Generated."
    elif overall_score >= 45:
        overall_verdict = "SUSPICIOUS"
        overall_label = "This content shows concerning patterns. Verify with trusted sources."
    elif overall_score >= 30:
        overall_verdict = "LIKELY REAL"
        overall_label = "This content appears mostly authentic, with minor flags."
    else:
        overall_verdict = "REAL NEWS"
        overall_label = "This news appears to be authentic and human-written."

    result["overall"] = {
        "score": overall_score,
        "verdict": overall_verdict,
        "label": overall_label,
    }

    return jsonify(result)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    load_fake_news_model()
    print("\n🚀 Server running at http://localhost:5000\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
