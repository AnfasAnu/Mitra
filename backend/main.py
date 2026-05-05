from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import json
from typing import Optional, List
from datetime import datetime, timedelta
import traceback

from fastapi.middleware.cors import CORSMiddleware



from function.profile_builder import build_profile
from function.matcher import match_schemes
from function.gemini_service import (
    generate_ai_output,
    generate_scheme_guide,
    generate_comparison,
)
from function.sarvam_chat import (
    generate_chat_response,
    parse_voice_to_profile,
)
from function.vision_service import extract_from_sarvam, parse_vision_output
from function.voice_service import speech_to_text, text_to_speech, translate_text
from database import init_db, create_user, verify_user, save_profile, load_profile, delete_profile, save_preferences, load_preferences

app = FastAPI(title="Kerala Scheme Navigator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later restrict
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_db()

# Allow Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Resolve schemes.json relative to this file so it works from any CWD
SCHEMES_PATH = Path(__file__).resolve().parent / "data" / "schemes.json"

with open(SCHEMES_PATH, encoding="utf-8") as f:
    schemes = json.load(f)


class UserInput(BaseModel):
    email: str = Field(default="", description="User email for notifications")
    phone: str = Field(default="", description="User phone for notifications")
    income: int = Field(default=0, ge=0, description="Annual income in INR")
    category: str = Field(default="", description="Category e.g. SC, ST, OBC, GENERAL")
    district: str = Field(default="", description="District name in Kerala")
    age: int = Field(default=0, ge=0, description="Age of the applicant")
    gender: str = Field(default="", description="Gender: Male, Female, Other")
    occupation: str = Field(default="", description="Occupation: Farmer, Student, Unemployed, Employed, etc.")
    education: str = Field(default="", description="Education: Student, Graduate, Below 10th, etc.")
    disability: bool = Field(default=False, description="Whether applicant has 40%+ disability")
    marital_status: str = Field(default="", description="Marital status: Single, Married, Widow, Divorced")


REQUIRED_FIELDS = ["income", "category", "district"]


# ──────────────────────────────────────────────────
# 0. Authentication
# ──────────────────────────────────────────────────
class AuthRequest(BaseModel):
    username: str
    password: str

@app.post("/auth/register")
def register(data: AuthRequest):
    success = create_user(data.username, data.password)
    if success:
        return {"success": True, "message": "User created successfully"}
    return {"success": False, "error": "Username already exists"}

@app.post("/auth/login")
def login(data: AuthRequest):
    success = verify_user(data.username, data.password)
    if success:
        profile = load_profile(data.username)
        return {"success": True, "message": "Login successful", "saved_profile": profile}
    return {"success": False, "error": "Invalid username or password"}


# ──────────────────────────────────────────────────
# 0b. Profile Save/Load (Personal Info)
# ──────────────────────────────────────────────────
class ProfileSaveRequest(BaseModel):
    username: str
    email: str = ""
    phone: str = ""
    income: int = 0
    category: str = ""
    district: str = ""
    age: int = 0
    gender: str = ""
    occupation: str = ""
    education: str = ""
    disability: bool = False
    marital_status: str = ""


@app.post("/profile/save")
def profile_save(data: ProfileSaveRequest):
    """Save user personal profile to database."""
    success = save_profile(data.username, data.model_dump())
    if success:
        return {"success": True, "message": "Profile saved"}
    return {"success": False, "error": "Could not save profile"}


@app.get("/profile/load/{username}")
def profile_load(username: str):
    """Load saved user profile."""
    profile = load_profile(username)
    if profile:
        return {"success": True, "profile": profile}
    return {"success": True, "profile": {}, "message": "No saved profile found"}
 
 
@app.delete("/profile/delete/{username}")
def profile_delete(username: str):
    """Delete user personal profile."""
    success = delete_profile(username)
    if success:
        return {"success": True, "message": "Profile data deleted"}
    return {"success": False, "error": "Could not delete profile"}


# ──────────────────────────────────────────────────
# 0c. Preferences Save/Load (General Settings)
# ──────────────────────────────────────────────────
class PreferencesSaveRequest(BaseModel):
    username: str
    preferred_language: str = "ml-IN"
    preferred_speaker: str = "anila"
    notifications_enabled: bool = True
    auto_translate: bool = False
    theme: str = "dark"


@app.post("/preferences/save")
def preferences_save(data: PreferencesSaveRequest):
    """Save user general preferences/settings to database."""
    success = save_preferences(data.username, data.model_dump())
    if success:
        return {"success": True, "message": "Preferences saved"}
    return {"success": False, "error": "Could not save preferences"}


@app.get("/preferences/load/{username}")
def preferences_load(username: str):
    """Load saved user preferences."""
    prefs = load_preferences(username)
    if prefs:
        return {"success": True, "preferences": prefs}
    return {"success": True, "preferences": {}, "message": "No saved preferences found"}


# ──────────────────────────────────────────────────
# 1. CORE: Analyze eligibility
# ──────────────────────────────────────────────────
@app.post("/analyze")
def analyze(data: UserInput):
    user = build_profile(data.model_dump())
    matched = match_schemes(user, schemes)

    return {
        "user": user,
        "matched_schemes": matched,
    }


from function.gemini_service import (
    generate_ai_output,
    generate_scheme_guide,
    generate_comparison,
    parse_voice_to_profile,
)

# ...

class SchemeGuideRequest(BaseModel):
    user: dict = Field(..., description="User profile dict")
    scheme: dict = Field(..., description="Single scheme dict")


@app.post("/scheme-guide")
def get_scheme_guide(data: SchemeGuideRequest):
    """Generate AI Application Guide for a single scheme."""
    ai_output = generate_scheme_guide(data.user, data.scheme)
    return {"ai_output": ai_output, "success": True}


# ──────────────────────────────────────────────────
# 2. Document Upload + Auto Eligibility
# ──────────────────────────────────────────────────
@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    income: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    district: Optional[str] = Form(None),
):
    contents = await file.read()

    # Extract data via Sarvam Vision API
    vision_data = extract_from_sarvam(contents)
    extracted_data = parse_vision_output(vision_data)

    # Allow manual overrides from form fields
    overrides = {}
    if income and income.strip():
        overrides["income"] = int(income)
    if category and category.strip():
        overrides["category"] = category.strip()
    if district and district.strip():
        overrides["district"] = district.strip()

    # Merge: manual overrides take priority over scanned data
    merged = {**extracted_data, **overrides}

    # Determine which fields were extracted, which are missing
    extracted_fields = {}
    missing_fields = []
    for field in REQUIRED_FIELDS:
        val = merged.get(field)
        if val and str(val).strip() and str(val) != "0":
            extracted_fields[field] = val
        else:
            missing_fields.append(field)

    # Build profile and match
    user = build_profile(merged)
    matched = match_schemes(user, schemes)

    return {
        "user": user,
        "matched_schemes": matched,
        "scan_results": {
            "extracted_fields": extracted_fields,
            "missing_fields": missing_fields,
            "raw_vision_data": vision_data,
            "source": "sarvam_vision",
        },
    }


# ──────────────────────────────────────────────────
# 3. Voice STT + TTS
# ──────────────────────────────────────────────────
class TTSRequest(BaseModel):
    text: str = Field(..., description="Text to convert to speech")
    language: str = Field(default="ml-IN", description="Language code e.g. ml-IN, en-IN, hi-IN")
    speaker: str = Field(default="anila", description="Voice: anila(f), shubh(m), advika(f)")


@app.post("/voice/stt")
async def voice_stt(file: UploadFile = File(...), language: str = Form("ml-IN")):
    """Convert speech audio to text using Sarvam Saaras v3."""
    audio_bytes = await file.read()
    result = speech_to_text(audio_bytes, language=language)
    return result


@app.post("/voice/tts")
def voice_tts(data: TTSRequest):
    """Convert text to speech using Sarvam Bulbul v3."""
    result = text_to_speech(data.text, language=data.language, speaker=data.speaker)
    return result


# ──────────────────────────────────────────────────
# 4. Smart Voice Parse → auto-extract profile from transcript
# ──────────────────────────────────────────────────
class VoiceParseRequest(BaseModel):
    transcript: str = Field(..., description="Voice transcript to parse into profile data")


@app.post("/voice/parse")
def voice_parse(data: VoiceParseRequest):
    """Use AI to extract income/category/district from a voice transcript."""
    parsed = parse_voice_to_profile(data.transcript)
    return {"parsed_profile": parsed, "success": "error" not in parsed}


# ──────────────────────────────────────────────────
# 5. AI Chatbot
# ──────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str = Field(..., description="User's chat message")
    history: Optional[List[dict]] = Field(default=[], description="Chat history for context")
    income: Optional[int] = Field(default=None, description="User's income if known")
    category: Optional[str] = Field(default=None, description="User's category if known")
    district: Optional[str] = Field(default=None, description="User's district if known")


@app.post("/chat")
def chat(data: ChatRequest):
    """Conversational AI chat about government schemes."""
    user_profile = {}
    if data.income:
        user_profile["income"] = data.income
    if data.category:
        user_profile["category"] = data.category
    if data.district:
        user_profile["district"] = data.district

    response = generate_chat_response(
        message=data.message,
        history=data.history,
        user_profile=user_profile if user_profile else None,
        schemes=schemes,
    )
    return {"response": response, "success": True}


# ──────────────────────────────────────────────────
# 6. Scheme Comparison
# ──────────────────────────────────────────────────
class CompareRequest(BaseModel):
    scheme_a: str = Field(..., description="Name of first scheme")
    scheme_b: str = Field(..., description="Name of second scheme")
    income: Optional[int] = Field(default=None)
    category: Optional[str] = Field(default=None)
    district: Optional[str] = Field(default=None)


@app.post("/compare")
def compare_schemes(data: CompareRequest):
    """Compare two schemes side by side with AI analysis."""
    scheme_a = next((s for s in schemes if s["name"] == data.scheme_a), None)
    scheme_b = next((s for s in schemes if s["name"] == data.scheme_b), None)

    if not scheme_a or not scheme_b:
        return {"error": "One or both scheme names not found", "success": False}

    user_profile = {}
    if data.income:
        user_profile["income"] = data.income
    if data.category:
        user_profile["category"] = data.category
    if data.district:
        user_profile["district"] = data.district

    comparison = generate_comparison(scheme_a, scheme_b, user_profile if user_profile else None)

    return {
        "scheme_a": scheme_a,
        "scheme_b": scheme_b,
        "ai_comparison": comparison,
        "success": True,
    }


# ──────────────────────────────────────────────────
# 7. Translation (Sarvam Translate)
# ──────────────────────────────────────────────────
class TranslateRequest(BaseModel):
    text: str = Field(..., description="Text to translate")
    source_language: str = Field(default="en-IN", description="Source language code")
    target_language: str = Field(default="ml-IN", description="Target language code")


@app.post("/translate")
def translate(data: TranslateRequest):
    """Translate text between Indian languages using Sarvam."""
    result = translate_text(data.text, data.source_language, data.target_language)
    return result


# ──────────────────────────────────────────────────
# 8. Notifications — Upcoming deadlines, new schemes
# ──────────────────────────────────────────────────
@app.get("/notifications")
def get_notifications():
    """Get upcoming deadlines and recently added schemes."""
    today = datetime.now().date()
    notifications = []

    for scheme in schemes:
        # Check deadlines
        deadline_str = scheme.get("deadline", "")
        if deadline_str:
            try:
                deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date()
                days_left = (deadline - today).days
                if 0 <= days_left <= 60:
                    notifications.append({
                        "type": "deadline",
                        "scheme": scheme["name"],
                        "message": f"⏰ {scheme['name']} deadline in {days_left} days ({deadline_str})",
                        "urgency": "high" if days_left <= 14 else "medium" if days_left <= 30 else "low",
                        "days_left": days_left,
                        "deadline": deadline_str,
                        "scheme_category": scheme.get("scheme_category", "General"),
                    })
            except ValueError:
                pass

        # Check recently added (within 30 days)
        added_str = scheme.get("added_date", "")
        if added_str:
            try:
                added = datetime.strptime(added_str, "%Y-%m-%d").date()
                days_ago = (today - added).days
                if 0 <= days_ago <= 30:
                    notifications.append({
                        "type": "new_scheme",
                        "scheme": scheme["name"],
                        "message": f"🆕 {scheme['name']} added {days_ago} days ago",
                        "days_ago": days_ago,
                        "scheme_category": scheme.get("scheme_category", "General"),
                    })
            except ValueError:
                pass

    # Sort: urgent deadlines first, then new schemes
    notifications.sort(key=lambda x: (
        0 if x["type"] == "deadline" else 1,
        x.get("days_left", 999),
    ))

    return {"notifications": notifications, "count": len(notifications)}


@app.get("/notifications/personal/{username}")
def get_personal_notifications(username: str):
    """Get personalized notifications filtered by the user's saved profile."""
    profile = load_profile(username)
    if not profile or not any([
        profile.get("income", 0) > 0,
        profile.get("category", ""),
        profile.get("district", ""),
    ]):
        # No profile saved — fall back to generic notifications
        return get_notifications()

    today = datetime.now().date()
    notifications = []

    # Build a user dict for the matcher
    user_data = {
        "income": profile.get("income", 0),
        "category": profile.get("category", "").upper(),
        "district": profile.get("district", ""),
        "age": profile.get("age", 0),
        "gender": profile.get("gender", ""),
        "occupation": profile.get("occupation", ""),
        "education": profile.get("education", ""),
        "disability": profile.get("disability", False),
        "marital_status": profile.get("marital_status", ""),
    }

    for scheme in schemes:
        # Quick eligibility check — only notify for schemes user could be eligible for
        from function.matcher import check_eligibility
        eligible, _, _ = check_eligibility(user_data, scheme)
        if not eligible:
            continue

        # Check deadlines
        deadline_str = scheme.get("deadline", "")
        if deadline_str:
            try:
                deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date()
                days_left = (deadline - today).days
                if 0 <= days_left <= 60:
                    notifications.append({
                        "type": "deadline",
                        "scheme": scheme["name"],
                        "message": f"⏰ {scheme['name']} deadline in {days_left} days ({deadline_str})",
                        "urgency": "high" if days_left <= 14 else "medium" if days_left <= 30 else "low",
                        "days_left": days_left,
                        "deadline": deadline_str,
                        "scheme_category": scheme.get("scheme_category", "General"),
                        "personalized": True,
                    })
            except ValueError:
                pass

        # Check recently added (within 30 days)
        added_str = scheme.get("added_date", "")
        if added_str:
            try:
                added = datetime.strptime(added_str, "%Y-%m-%d").date()
                days_ago = (today - added).days
                if 0 <= days_ago <= 30:
                    notifications.append({
                        "type": "new_scheme",
                        "scheme": scheme["name"],
                        "message": f"🆕 {scheme['name']} added {days_ago} days ago — you may be eligible!",
                        "days_ago": days_ago,
                        "scheme_category": scheme.get("scheme_category", "General"),
                        "personalized": True,
                    })
            except ValueError:
                pass

    notifications.sort(key=lambda x: (
        0 if x["type"] == "deadline" else 1,
        x.get("days_left", 999),
    ))

    return {
        "notifications": notifications,
        "count": len(notifications),
        "personalized": True,
        "profile_summary": {
            "income": user_data["income"],
            "category": user_data["category"],
            "district": user_data["district"],
        },
    }


# ──────────────────────────────────────────────────
# 9. List all schemes (for comparison picker, etc.)
# ──────────────────────────────────────────────────
@app.get("/schemes")
def list_schemes():
    """Return all scheme names grouped by category."""
    categories = {}
    for s in schemes:
        cat = s.get("scheme_category", "General")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append({
            "name": s["name"],
            "type": s.get("type", "State"),
            "benefits": s["benefits"],
            "income_limit": s["income_limit"],
        })
    return {"categories": categories, "total": len(schemes)}