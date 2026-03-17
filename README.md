# 🔍 TruthLens — Fake News & AI Content Detector

A full-stack web application that detects **fake news** and **AI-generated content** using machine learning and statistical analysis.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey?logo=flask)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

- **Fake News Detection** — ML-powered classifier trained to identify misinformation patterns
- **AI Content Detection** — 8 statistical metrics to detect AI-generated text
- **Real-time Analysis** — Instant credibility reports with confidence scores
- **Beautiful Dark UI** — Premium glassmorphism design with smooth animations
- **Sample Texts** — Pre-loaded examples for quick testing
- **Detailed Metrics** — Expandable breakdown of each detection metric

## 🏗️ Architecture

```
┌─────────────────┐      POST /api/analyze      ┌──────────────────┐
│                 │ ──────────────────────────►  │                  │
│   Frontend      │                              │   Flask API      │
│   (HTML/CSS/JS) │  ◄──────────────────────────  │   (Python)       │
│                 │      JSON Response           │                  │
└─────────────────┘                              └──────┬───────────┘
                                                        │
                                              ┌─────────┴─────────┐
                                              │                   │
                                    ┌─────────▼──────┐  ┌────────▼────────┐
                                    │  Fake News      │  │  AI Content     │
                                    │  Classifier     │  │  Detector       │
                                    │  (TF-IDF+LogReg)│  │  (8 Heuristics) │
                                    └─────────────────┘  └─────────────────┘
```

## 📂 Project Structure

```
fake-news-detector/
├── backend/
│   ├── app.py              # Flask server (serves frontend + API)
│   ├── train_model.py      # ML model training script
│   ├── ai_detector.py      # AI content detection engine
│   ├── requirements.txt    # Python dependencies
│   └── model/              # Trained model files (generated)
├── frontend/
│   ├── index.html          # Main UI
│   ├── style.css           # Design system (dark theme)
│   └── app.js              # Frontend logic & animations
├── .gitignore
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+** installed on your system

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/fake-news-detector.git
   cd fake-news-detector
   ```

2. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Train the model** (one-time setup)
   ```bash
   python train_model.py
   ```

4. **Start the server**
   ```bash
   python app.py
   ```

5. **Open in browser**
   ```
   http://localhost:5000
   ```

## 🧠 How It Works

### Engine 1: Fake News Classifier
- **Model**: TF-IDF Vectorizer → Logistic Regression pipeline
- **Features**: Uni-gram and bi-gram text analysis (5,000 max features)
- **Indicators**: Sensationalist keywords, excessive capitalization, exclamation patterns

### Engine 2: AI Content Detector
Analyzes 8 statistical metrics to identify AI writing patterns:

| Metric | What It Detects |
|--------|----------------|
| Sentence Uniformity | AI writes sentences of similar length |
| Vocabulary Richness | AI uses moderate, "safe" vocabulary |
| AI Phrase Density | Phrases like "delve", "furthermore", "it's important to note" |
| Transition Density | Overuse of formal transition words |
| Burstiness | Lack of natural complexity variation |
| Punctuation Variety | AI avoids dashes, semicolons, etc. |
| Paragraph Structure | AI paragraphs tend to be uniform in length |
| Repetition Patterns | Repeated bigram structures in the text |

## 🎨 Screenshots

### Landing Page
Premium dark-mode hero with animated gradient text and stats.

### Content Analyzer
Paste any text, load a sample, and hit Analyze for instant results.

### Analysis Results
Risk score ring, individual detection bars, confidence levels, and detailed explanations.

## 🛠️ Tech Stack

- **Frontend**: HTML5, CSS3 (vanilla), JavaScript (vanilla)
- **Backend**: Python, Flask, Flask-CORS
- **ML**: scikit-learn (TF-IDF + Logistic Regression)
- **Analysis**: Custom statistical heuristic engine

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---

> Built with ❤️ for truth in the age of AI.
