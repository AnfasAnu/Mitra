# 🏛️ K-AI Scheme Mitra — Kerala Government Scheme Navigator

> **AI-powered citizen welfare navigator aligned with Kerala IT Policy 2026**

K-AI Scheme Mitra is an intelligent system that automatically detects which Kerala government welfare schemes a citizen is eligible for based on their profile. It combines a **rule engine** with **Google Gemini 2.0 Flash** for AI-ranked recommendations & guidance, **Sarvam AI** for multilingual chatbot (sarvam-m1), voice/translation/vision, and a **conversational chatbot** — with optional privacy-first data storage.

---

## ✨ Features

| Feature | Description |
|:---|:---|
| **🧠 AI Recommendation Engine** | Gemini ranks schemes by relevance with detailed eligibility explanations |
| **🌐 Multilingual Support** | Translate results to Malayalam, Hindi, Tamil, Telugu, Kannada via Sarvam |
| **🎤 Voice Interaction** | Speak profile → AI auto-extracts income/category/district → finds schemes |
| **📄 Document Scanning** | Upload Ration Card, Aadhar, Income Cert → Vision API extracts data |
| **📊 Scheme Comparison** | Compare any two schemes side-by-side with AI analysis |
| **📍 Location-Aware** | District-specific scheme filtering and prioritization |
| **🔔 Notifications** | Upcoming deadlines and newly added scheme alerts |
| **🧾 Application Guidance** | Step-by-step: documents, where to apply, links, offices |
| **🤖 AI Chatbot** | Ask anything about schemes in any language — natural conversation |

---

## ⚡ Quick Start

### Prerequisites
- Python 3.9+
- [Google Gemini API key](https://aistudio.google.com/apikey)
- [Sarvam AI API key](https://dashboard.sarvam.ai/)

### 1. Install
```bash
git clone https://github.com/your-username/scheme-navigator.git
cd scheme-navigator
pip install -r requirements.txt
```

### 2. Set up `.env`
```
GEMINI_API_KEY=your_gemini_api_key_here
SARVAM_API_KEY=your_sarvam_api_key_here
```

### 3. Start backend
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

### 4. Start frontend (new terminal)
```bash
cd frontend
python -m streamlit run app.py --server.port 8501
```

### 5. Open http://localhost:8501

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|:---|:---|:---|
| `/analyze` | POST | Eligibility analysis with AI-ranked results |
| `/upload` | POST | Document scan + auto eligibility |
| `/voice/stt` | POST | Speech-to-text (Sarvam Saaras v3) |
| `/voice/tts` | POST | Text-to-speech (Sarvam Bulbul v3) |
| `/voice/parse` | POST | AI extracts profile from voice transcript |
| `/chat` | POST | Conversational AI chatbot |
| `/compare` | POST | Scheme comparison with AI analysis |
| `/translate` | POST | Text translation (Sarvam Mayura v1) |
| `/notifications` | GET | Upcoming deadlines & new schemes |
| `/schemes` | GET | All schemes grouped by category |

---

## 📜 License

MIT License

---

<p align="center">
  Built with ❤️ for Kerala • Aligned with <strong>Kerala IT Policy 2026</strong>
</p>
