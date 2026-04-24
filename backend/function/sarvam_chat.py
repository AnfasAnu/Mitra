"""
Sarvam AI Chat Service — Uses Sarvam's OpenAI-compatible Chat Completions API.
Optimized for Indian languages (Malayalam, Hindi, Tamil, Telugu, Kannada).
Model: sarvam-m1 (multilingual, Indic-optimized)
"""
import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
SARVAM_CHAT_URL = "https://api.sarvam.ai/v1/chat/completions"


def generate_chat_response(message: str, history: list = None, user_profile: dict = None, schemes: list = None) -> str:
    """
    Conversational AI chatbot powered by Sarvam AI (sarvam-m1).
    Supports multilingual input/output with native Indic language understanding.
    """
    system_prompt = (
        "You are K-AI Scheme Mitra, a friendly and expert Kerala government welfare chatbot. "
        "You help citizens understand and apply for government schemes. "
        "You are fluent in Malayalam, Hindi, Tamil, Telugu, Kannada, and English. "
        "Always respond in the same language the user uses. "
        "Be warm, empathetic, and provide actionable advice."
    )

    if user_profile and any(user_profile.values()):
        system_prompt += (
            f"\n\nUser's Profile: "
            f"Income=₹{user_profile.get('income', 'unknown')}, "
            f"Category={user_profile.get('category', 'unknown')}, "
            f"District={user_profile.get('district', 'unknown')}"
        )

    if schemes:
        scheme_entries = []
        for s in schemes:
            scheme_entries.append(
                f"• {s['name']} (Limit: ₹{s.get('income_limit',0):,}, "
                f"Category: {', '.join(s.get('category', ['All']))}, "
                f"Benefits: {s.get('benefits','')}, "
                f"Docs: {', '.join(s.get('documents', []))}, "
                f"Deadline: {s.get('deadline','N/A')})"
            )
        system_prompt += "\n\n=== SCHEME DATABASE ===\n" + "\n".join(scheme_entries)

    system_prompt += (
        "\n\nRules:\n"
        "1. Use the Scheme Database above for accurate facts.\n"
        "2. If user asks about eligibility, CHECK income limits and categories.\n"
        "3. Always provide actionable advice — documents, where to apply, deadlines.\n"
        "4. Keep responses concise but complete (max 400 words).\n"
        "5. Always end with a helpful follow-up suggestion."
    )

    # Build messages array (OpenAI format)
    messages = [{"role": "system", "content": system_prompt}]

    # Add conversation history
    if history:
        for msg in history:
            role = msg["role"]
            content = msg["content"].replace("🎙️", "").strip()
            if role in ("user", "assistant"):
                messages.append({"role": role, "content": content})

    # Add current message
    messages.append({"role": "user", "content": message})

    headers = {
        "Content-Type": "application/json",
        "api-subscription-key": SARVAM_API_KEY,
    }

    payload = {
        "model": "sarvam-m1",
        "messages": messages,
        "max_tokens": 1024,
        "temperature": 0.7,
    }

    try:
        response = requests.post(SARVAM_CHAT_URL, json=payload, headers=headers, timeout=60)
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        else:
            return f"I'm sorry, I couldn't process your question. Sarvam API error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"I'm sorry, I couldn't process your question. Error: {str(e)}"


def run_sarvam_instruction(system_prompt: str, user_prompt: str) -> str:
    """General utility to run a task on Sarvam M1."""
    headers = {"Content-Type": "application/json", "api-subscription-key": SARVAM_API_KEY}
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    payload = {"model": "sarvam-m1", "messages": messages, "max_tokens": 1024, "temperature": 0.1}
    try:
        r = requests.post(SARVAM_CHAT_URL, json=payload, headers=headers, timeout=60)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
        return f"Error: {r.status_code}"
    except Exception as e: return str(e)


def generate_comparison(scheme_a: dict, scheme_b: dict, user_profile: dict = None) -> str:
    """Generate AI-powered comparison using Sarvam M1 (Offloaded from Gemini)."""
    user_ctx = f"User Profile: {user_profile}" if user_profile else "General user."
    system = "You are a government scheme expert. Compare the two schemes provided by the user accurately."
    user = f"""Compare these schemes for this user: {user_ctx}
    
    SCHEME A: {scheme_a['name']} - Benefits: {scheme_a['benefits']} - Limit: {scheme_a.get('income_limit')}
    SCHEME B: {scheme_b['name']} - Benefits: {scheme_b['benefits']} - Limit: {scheme_b.get('income_limit')}
    
    Output a comparison table and a recommendation on which is better for them. Response should be in Markdown."""
    return run_sarvam_instruction(system, user)


def parse_voice_to_profile(transcript: str) -> dict:
    """Extract profile data from voice using Sarvam M1 (Offloaded from Gemini)."""
    import json
    system = "Extract structured JSON from voice input. Fields: income (int), category (OBC/SC/ST/GENERAL), district (Kerala district name). Return ONLY JSON."
    user = f"Transcript: {transcript}"
    result = run_sarvam_instruction(system, user)
    try:
        # Clean potential markdown
        clean = result.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except:
        return {"error": "Could not parse voice data", "raw": result}
