import requests
import base64
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
STT_URL = "https://api.sarvam.ai/speech-to-text"
TTS_URL = "https://api.sarvam.ai/text-to-speech"
TRANSLATE_URL = "https://api.sarvam.ai/translate"


def speech_to_text(audio_bytes: bytes, language: str = "ml-IN") -> dict:
    """
    Convert speech audio to text using Sarvam Saaras v3.
    Supports Malayalam (ml-IN), English (en-IN), Hindi (hi-IN), etc.
    Returns: {"transcript": "...", "language": "..."}
    """
    headers = {
        "api-subscription-key": SARVAM_API_KEY,
    }
    files = {
        "file": ("audio.wav", audio_bytes, "audio/wav"),
    }
    data = {
        "model": "saaras:v3",
        "mode": "transcribe",
    }

    try:
        response = requests.post(STT_URL, headers=headers, files=files, data=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return {
                "transcript": result.get("transcript", ""),
                "language": result.get("language_code", language),
                "success": True
            }
        else:
            return {
                "transcript": "",
                "error": f"STT API error: {response.status_code} - {response.text}",
                "success": False
            }
    except Exception as e:
        return {
            "transcript": "",
            "error": f"STT request failed: {str(e)}",
            "success": False
        }


def text_to_speech(text: str, language: str = "ml-IN", speaker: str = "anila") -> dict:
    """
    Convert text to speech using Sarvam Bulbul v3.
    Speakers: anila(f), shubh(m), advika(f), mansi(f), etc.
    Languages: ml-IN, en-IN, hi-IN, ta-IN, te-IN, kn-IN, etc.
    Returns: {"audio_base64": "...", "success": True}
    """
    headers = {
        "api-subscription-key": SARVAM_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "text": text[:2500],  # Bulbul v3 max 2500 chars
        "target_language_code": language,
        "speaker": speaker,
        "model": "bulbul:v3",
        "pace": 1.0,
        "sample_rate": 22050,
    }

    try:
        response = requests.post(TTS_URL, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            audios = result.get("audios", [])
            if audios:
                return {
                    "audio_base64": audios[0],
                    "success": True
                }
            return {"audio_base64": "", "error": "No audio in response", "success": False}
        else:
            return {
                "audio_base64": "",
                "error": f"TTS API error: {response.status_code} - {response.text}",
                "success": False
            }
    except Exception as e:
        return {
            "audio_base64": "",
            "error": f"TTS request failed: {str(e)}",
            "success": False
        }


def translate_text(text: str, source_language: str = "en-IN", target_language: str = "ml-IN") -> dict:
    """
    Translate text between Indian languages using Sarvam Translate API.
    Languages: en-IN, ml-IN, hi-IN, ta-IN, te-IN, kn-IN, etc.
    Returns: {"translated_text": "...", "success": True}
    """
    headers = {
        "api-subscription-key": SARVAM_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "input": text[:5000],
        "source_language_code": source_language,
        "target_language_code": target_language,
        "model": "mayura:v1",
        "enable_preprocessing": True,
    }

    try:
        response = requests.post(TRANSLATE_URL, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return {
                "translated_text": result.get("translated_text", ""),
                "source_language": source_language,
                "target_language": target_language,
                "success": True
            }
        else:
            return {
                "translated_text": "",
                "error": f"Translate API error: {response.status_code} - {response.text}",
                "success": False
            }
    except Exception as e:
        return {
            "translated_text": "",
            "error": f"Translation failed: {str(e)}",
            "success": False
        }
