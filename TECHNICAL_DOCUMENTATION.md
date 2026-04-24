# 🏛️ K-AI Scheme Mitra — Technical Documentation

## 1. Project Overview
**K-AI Scheme Mitra** is an agentic, AI-powered welfare navigator designed to bridge the gap between complex government bureaucracy and the everyday citizen. Aligned with the **Kerala IT Policy 2026**, it provides a "Predictive Governance" model—proactively identifying eligibility and providing actionable guidance rather than making users search through lists.

---

## 2. Core Architecture
The project follows a **Modular Dual-AI Architecture**, distributing tasks between engines based on their specific strengths (indic language vs. deep reasoning).

### 📐 High-Level Stack
- **Frontend**: Streamlit (Python-based reactive UI)
- **Backend API**: FastAPI (High-performance Python framework)
- **Database**: SQLite (Local storage for opt-in user profiles)
- **Intelligence Layer**: 
    - **Google Gemini 1.5 Flash**: Structural reasoning, eligibility analysis, and profile parsing.
    - **Sarvam AI**: Multilingual voice (Saaras/Bulbul), translation (Mayura), and OCR (Vision).
    - **Sarvam M1**: Dedicated Indic-optimized chatbot engine.

---

## 3. Key Features & Implementation

### A. 🧭 Intelligent Navigator
- **Logic**: A **Hybrid Rule Engine** first filters 45+ schemes based on hard constraints (Income ceilings, Category, District).
- **Ranking**: Surfaced schemes are then passed to **Gemini 1.5 Flash**, which calculates a "Relevance Score" (0-100) based on the user's life situation (e.g., prioritizing "Housing" for low-income families).

### B. 📸 AI Document Scanner
- **Tool**: Sarvam Vision API.
- **Innovation**: Instead of simple OCR, it uses **Semantic Extraction**. It identifies Name, DOB (calculates Age), Gender, Income, and Category directly from images of Ration Cards, Aadhaar, or Income Certificates.
- **Sync**: Extracted fields are automatically pushed to the session state, auto-filling the Navigator form.

### C. 🎙️ Multilingual Voice Assistant
- **STT/TTS**: Sarvam Saaras (Speech-to-Text) and Bulbul (Text-to-Speech).
- **Agentic Logic**: Users can mention their whole profile in a single sentence (e.g., *"I'm a 30yo student from Wayanad..."*). Gemini parses this transcript into a structured JSON profile.

### D. 🪄 On-Demand AI Guidance (Contextual Roadmap)
- **Logic**: To optimize API usage and user focus, guidance is no longer global.
- **Implementation**: Each scheme card has a "Generate Guide" button. Upon clicking, the system sends the *specific user profile* and *specific scheme* to Gemini to create a 5-point application roadmap (Documents, First Step, Deadlines, etc.).

### E. 🤖 Dual-AI Chatbot
- **Engine**: Sarvam M1 (OpenAI-compatible).
- **Benefit**: Handles native Malayalam/Hindi/Tamil conversation much more naturally than standard LLMs by understanding regional nuances without internal translation steps.
- **Context**: The chatbot maintains a conversation history for multi-turn support.

---

## 4. Logical Flow (User Journey)
1. **Perception Stage**: User provides data via Manual form, Voice, or Document Scan.
2. **Analysis Stage**: 
    - `backend/function/matcher.py` (Local Rule Engine) filters the database.
    - `backend/function/gemini_service.py` (GenAI) ranks the filtered results.
3. **Guidance Stage**: User explores matches and generates on-demand AI Guides for preferred schemes.
4. **Action Stage**: Chatbot answers logistical questions; UI provides direct application links and office locations.

---

## 5. Security & Privacy
- **Privacy-First**: The system defaults to **Guest Mode**. All data (scans, chat, profile) is held in RAM (Browser Session) and is wiped upon closing or clicking "End Session."
- **Opt-in Storage**: Users can explicitly choose to "Save Profile." This persists core eligibility data (not ID numbers) to SQLite for personalized notifications across devices.

---

## 6. Directory Structure
```text
├── backend/
│   ├── main.py              # FastAPI Endpoints & Logic Orchestration
│   ├── database.py          # SQLite Operations (Profiles & Preferences)
│   ├── function/
│   │   ├── gemini_service.py# Analysis, Roadmap, and Comparison
│   │   ├── sarvam_chat.py   # Sarvam-powered Chatbot logic
│   │   ├── vision_service.py# Document extraction (Sarvam Vision)
│   │   ├── voice_service.py # STT, TTS, and Translation (Sarvam)
│   │   ├── matcher.py       # Local Rule Engine (Logic)
│   │   └── profile_builder.py# Data cleaning and normalization
│   └── data/                # Scheme database & SQLite file
└── frontend/
    └── app.py               # Streamlit UI & State Management
```

---

## 7. Function Registry (Detailed Logic)

### 🔹 Backend Orchestration (`main.py`)
- **`analyze(data: UserInput)`**: The gateway for the Navigator. It triggers the `profile_builder`, runs the `matcher` rule-engine, and returns eligible/ineligible schemes sorted by importance.
- **`get_scheme_guide(data: SchemeGuideRequest)`**: The on-demand guide generator. It receives a specific scheme and user profile, then calls Gemini to produce a laser-focused roadmap.
- **`upload_document(file)`**: Orchestrates the scanning flow. It feeds the file to `vision_service`, merges the results with any manual overrides, and returns the updated profile.
- **`chat(data: ChatRequest)`**: The interface for the Sarvam-powered assistant. It passes the current message and full chat history to ensure the AI remembers prior context.
- **`compare_schemes(data: CompareRequest)`**: Takes two scheme objects and the user profile to provide a detailed AI-driven pro/con analysis.

### 🔹 Intelligence Services (`function/`)

#### [gemini_service.py]
- **`generate_ai_output(user, schemes)`**: Uses Gemini's large context window to explain exactly why a user qualifies for a set of schemes and ranks them by impact.
- **`generate_scheme_guide(user, scheme)`**: **(Contextual Agent)** Constructs a specific prompt with the user's variables to create a 3rd-person application "concierge" guide.
- **`parse_voice_to_profile(transcript)`**: A zero-shot extraction function. It uses the LLM to find schema fields (age, income, etc.) hidden inside natural, casual spoken language.

#### [vision_service.py]
- **`extract_from_sarvam(file)`**: Sends raw image data to Sarvam Vision with a custom prompt tailored for Indian Government IDs.
- **`parse_vision_output(data)`**: The critical "Cleanup" function. It uses optimized regex and heuristic patterns to extract numerical values (Income/Age) and categorical values (Caste/District) from messy OCR text.

#### [sarvam_chat.py]
- **`generate_chat_response(message, history, profile)`**: Manages a stateful conversation using Sarvam M1. It injects the user's live profile into the system prompt so the bot always knows who it is talking to.

#### [matcher.py]
- **`match_schemes(user, schemes)`**: The **"Rule-Engine"**. This is cold, hard logic. It iterates through every scheme and checks if `user.income <= scheme.income_limit` and if the user category/district matches the scheme. This ensures AI never "hallucinates" eligibility.

### 🔹 Persistence Layer (`database.py`)
- **`init_db()`**: Sets up SQLite tables for `user_profiles` and `preferences`.
- **`save_profile(username, profile)`**: Upserts user data. It ensures that when you "Save Info," it persists for the next login.
- **`delete_profile(username)`**: The "Privacy Kill-Switch." Instantly purges all stored data for a specific user.

---

## 8. Developer Notes
- **Extensibility**: Adding a new scheme is as simple as adding a JSON entry to the scheme database; the Rule Engine and AI automatically pick it up.
- **Quota Management**: On-demand AI Guide generation reduces API tokens by ~80% compared to global roadmaps.
- **Compliance**: Designed to be a modular "plug-and-play" system for government departments.
