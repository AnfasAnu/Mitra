import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env from project root (parent of backend/)
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY not found. Ensure .env exists in the project root.")

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash")


def generate_ai_output(user: dict, matched_schemes: list) -> str:
    """
    Uses Gemini 2.0 Flash to generate a human-friendly summary
    of the user's eligibility results — ranked, explained, with
    step-by-step application guidance.
    """
    eligible = [s for s in matched_schemes if s["eligible"]]

    # Build detailed scheme info for the prompt
    scheme_details = []
    for s in eligible:
        detail = {
            "name": s["name"],
            "benefits": s["benefits"],
            "type": s.get("type", "State"),
            "category": s.get("scheme_category", "General"),
            "reasons": s.get("eligibility_reasons", []),
            "documents": s["documents"],
            "how_to_apply": s.get("how_to_apply", []),
            "office": s.get("office", ""),
            "deadline": s.get("deadline", ""),
            "application_url": s.get("application_url", ""),
            "income_limit": s.get("income_limit", 0),
            "relevance_score": s.get("relevance_score", 0)
        }
        scheme_details.append(detail)

    prompt = f"""
You are K-AI Scheme Mitra, an expert Kerala government welfare assistant.
Your role is to be a SMART ADVISOR — not just listing schemes, but explaining WHY the user qualifies and guiding them.

User Profile:
- Annual Income: ₹{user.get('income', 0):,}
- Category: {user.get('category', 'Not specified')}
- District: {user.get('district', 'Not specified')}

Total Eligible Schemes: {len(eligible)} out of {len(matched_schemes)}

Detailed Eligible Scheme Information:
{scheme_details}

Generate a response following this EXACT structure:

## 🎯 Personalized Recommendation Summary
Brief 2-line summary of their situation — e.g. "Based on your income of ₹X and category Y, you qualify for Z schemes..."

## 🏆 Top Recommended Schemes (Ranked)
Rank the TOP 5 schemes by relevance. For each:
1. **Scheme Name** — benefit amount
   - ✅ Why you qualify: [specific reason based on their income/category]
   - 📋 Key documents needed
   - ⏰ Deadline (if any)

## 📊 Category Breakdown
Group remaining schemes by category with brief descriptions.

## 📝 Next Steps — Start Here
Actionable 3-step plan to begin the application process, mentioning the most impactful scheme first.

## ⚠️ Important Deadlines
List any approaching deadlines with dates.

Keep response structured, warm, and actionable. Use emojis sparingly but effectively.
Speak directly to the user ("You qualify because...").
"""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI analysis could not be generated: {str(e)}"


def generate_scheme_guide(user: dict, scheme: dict) -> str:
    """
    Generates a ultra-personalized application guide for a SINGLE specific scheme.
    """
    prompt = f"""
You are K-AI Scheme Mitra, a Kerala government welfare guide.
Provide a laser-focused application guide for this specific user and this specific scheme.

USER PROFILE:
- Income: ₹{user.get('income', 0):,}
- Category: {user.get('category', 'General')}
- District: {user.get('district', 'Kerala')}
- Age: {user.get('age', 'N/A')}
- Occupation: {user.get('occupation', 'N/A')}

SCHEME DETAILS:
- Name: {scheme['name']}
- Benefits: {scheme['benefits']}
- Documents Required: {', '.join(scheme.get('documents', []))}
- How to Apply: {'; '.join(scheme.get('how_to_apply', []))}
- Office: {scheme.get('office', 'N/A')}
- Application URL: {scheme.get('application_url', 'N/A')}
- Deadline: {scheme.get('deadline', 'N/A')}

YOUR TASK:
Generate a clean, structured guide (4-5 bullet points) covering:
1. ❓ Why do I qualify? (Briefly match user profile with scheme rules)
2. 📄 Exactly what papers do I need? (Personalized checklist)
3. 🚶 Step 1: Where do I go first? (Actionable first step)
4. ⏰ Urgency: Any upcoming deadlines?
5. 💡 Pro-tip for successful application.

Tone: Professional, helpful, simple. Respond in user's preferred style.
Respond in markdown format.
"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Guide could not be generated: {str(e)}"


def generate_chat_response(message: str, history: list = None, user_profile: dict = None, schemes: list = None) -> str:
    """
    Handles conversational AI chat about government schemes with full history context.
    """
    system_ctx = "You are K-AI Scheme Mitra, a friendly and expert Kerala government welfare chatbot."
    
    if user_profile and any(user_profile.values()):
        system_ctx += f"\nUser's Profile: Income=₹{user_profile.get('income', 'unknown')}, Category={user_profile.get('category', 'unknown')}, District={user_profile.get('district', 'unknown')}"

    if schemes:
        scheme_db = []
        for s in schemes:
            scheme_db.append(f"• {s['name']} (Limit: ₹{s.get('income_limit',0):,}, Category: {', '.join(s.get('category', ['All']))})")
        system_ctx += "\n\n=== SCHEME DATABASE ===\n" + "\n".join(scheme_db)

    # Clean history for Gemini
    gemini_history = []
    if history:
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            content = msg["content"].replace("🎙️", "").strip()
            gemini_history.append({"role": role, "parts": [content]})

    prompt = f"""
{system_ctx}

User's current question: {message}

Rules:
1. Use the Scheme Database for facts. 
2. Be empathetic and clear.
3. Respond in the user's language.
4. Always end with a helpful next step.

Respond:
"""

    try:
        chat = model.start_chat(history=gemini_history)
        response = chat.send_message(prompt)
        return response.text
    except Exception as e:
        return f"I'm sorry, I couldn't process your question. Error: {str(e)}"


def generate_comparison(scheme_a: dict, scheme_b: dict, user_profile: dict = None) -> str:
    """Generate AI-powered comparison using Gemini 2.0 Flash (Optimized for Quota)."""
    user_brief = f"Profile: {user_profile.get('income')}, {user_profile.get('category')}" if user_profile else "General"
    
    prompt = f"""
    Compare Govt Schemes for {user_brief}. Respond in Markdown.
    A: {scheme_a['name']} | B: {scheme_b['name']}
    
    Structure:
    1. Table: Compare Benefits, Docs, apply process.
    2. Recommendation: Which is better for them & why?
    3. Can apply to both?
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Comparison unavailable: {str(e)}"


def parse_voice_to_profile(transcript: str) -> dict:
    """
    Use Gemini to intelligently extract income, category, and district
    from a voice transcript in any language.
    """
    prompt = f"""
Extract structured profile data from this voice input. The user may speak in English, Malayalam, Hindi, Tamil, or mixed languages.
 
Voice transcript: "{transcript}"
 
Extract these fields (return ONLY valid JSON, nothing else):
{{
  "income": <number or 0>,
  "category": "<General, OBC, SC, ST, EWS or empty>",
  "district": "<Kerala district or empty>",
  "age": <number or 0>,
  "gender": "<Male, Female, or Other>",
  "occupation": "<Farmer, Student, Unemployed, Employed, etc or empty>",
  "education": "<Below 10th, 10th, 12th, Graduate, Post Graduate or empty>",
  "disability": <true/false based on 40%+ disability mention>,
  "marital_status": "<Single, Married, Widow, Divorced or empty>"
}}
 
Rules:
- Intelligently map regional terms (e.g., "padikkunnu" = Student, "kalyanam kazhinju" = Married).
- "1.5 lakh" = 150000.
- ONLY return the JSON object.
"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Clean markdown code blocks if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()
        import json
        return json.loads(text)
    except Exception as e:
        return {"income": 0, "category": "", "district": "", "error": str(e)}