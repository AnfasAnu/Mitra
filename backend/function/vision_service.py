import requests
import base64
import os
import re
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
VISION_URL = "https://api.sarvam.ai/parse/image"


def extract_from_sarvam(file_bytes):
    """
    Extract text from a document image using Sarvam Vision API.
    Supports Ration Card, Income Certificate, Aadhar Card.
    Returns raw extracted text/data from the API.
    """
    encoded_image = base64.b64encode(file_bytes).decode("utf-8")

    headers = {
        "api-subscription-key": SARVAM_API_KEY,
        "Content-Type": "application/json",
    }

    payload = {
        "image": f"data:image/png;base64,{encoded_image}",
        "prompt": (
            "Extract ALL text from this Indian government document. "
            "Look for these specific fields: "
            "1. Name of person "
            "2. Date of Birth or Age "
            "3. Gender (Male, Female, Other) "
            "4. Annual Income or Monthly Income (in rupees) "
            "5. Category/Caste (SC, ST, OBC, General, EWS) "
            "6. District or Address location "
            "7. Occupation or Profession (if mentioned) "
            "8. Aadhaar number "
            "9. Ration card number "
            "Return the extracted information in a structured way."
        ),
    }

    try:
        response = requests.post(VISION_URL, json=payload, headers=headers, timeout=60)
        if response.status_code == 200:
            result = response.json()
            return {
                "extracted_text": result.get("text", result.get("response", "")),
                "raw_response": result,
                "success": True,
            }
        else:
            return {
                "extracted_text": "",
                "error": f"Vision API error: {response.status_code} - {response.text}",
                "success": False,
            }
    except Exception as e:
        return {
            "extracted_text": "",
            "error": f"Vision request failed: {str(e)}",
            "success": False,
        }


def parse_vision_output(data):
    """
    Parse the raw Vision API output to extract structured profile fields.
    Uses regex and keyword matching to find income, category, and district
    from the OCR text — works even if the API returns partial or messy data.
    """
    extracted_text = data.get("extracted_text", "")
    if not extracted_text:
        extracted_text = str(data.get("raw_response", ""))

    text_lower = extracted_text.lower()
    result = {}

    # ── Extract Income ──
    income = _extract_income(extracted_text, text_lower)
    if income > 0:
        result["income"] = income

    # ── Extract Category ──
    category = _extract_category(text_lower)
    if category:
        result["category"] = category

    # ── Extract District ──
    district = _extract_district(text_lower)
    if district:
        result["district"] = district
        
    # ── Extract Age ──
    age = _extract_age(extracted_text, text_lower)
    if age > 0:
        result["age"] = age
        
    # ── Extract Gender ──
    gender = _extract_gender(text_lower)
    if gender:
        result["gender"] = gender

    return result


def _extract_income(text, text_lower):
    """Extract income from document text using multiple patterns."""
    # Pattern: "Annual Income: ₹1,50,000" or "Income: Rs. 150000"
    income_patterns = [
        r"(?:annual\s*income|yearly\s*income|income)[:\s]*(?:₹|rs\.?|inr)?\s*([\d,]+)",
        r"(?:₹|rs\.?|inr)\s*([\d,]+)\s*(?:per\s*(?:annum|year))",
        r"(?:monthly\s*income)[:\s]*(?:₹|rs\.?|inr)?\s*([\d,]+)",
        r"(?:വാർഷിക\s*വരുമാനം|വരുമാനം)[:\s]*([\d,]+)",  # Malayalam
        r"(?:वार्षिक\s*आय|आय)[:\s]*([\d,]+)",  # Hindi
    ]

    for pattern in income_patterns:
        match = re.search(pattern, text_lower)
        if match:
            amount_str = match.group(1).replace(",", "")
            try:
                amount = int(amount_str)
                # If it's monthly, multiply by 12
                if "month" in pattern or "monthly" in text_lower[:match.start() + 50]:
                    amount *= 12
                # Sanity check: income should be reasonable (1K to 1Cr)
                if 1000 <= amount <= 10000000:
                    return amount
            except ValueError:
                continue

    # Fallback: look for any large number near income-related words
    if "income" in text_lower or "वरुमानम" in text_lower or "आय" in text_lower:
        numbers = re.findall(r"(\d{4,8})", text)
        for num_str in numbers:
            num = int(num_str)
            if 10000 <= num <= 10000000:
                return num

    return 0


def _extract_category(text_lower):
    """Extract caste/category from document text."""
    category_map = {
        "scheduled caste": "SC",
        "scheduled tribe": "ST",
        "other backward class": "OBC",
        "other backward": "OBC",
        "backward class": "OBC",
        "economically weaker": "EWS",
        "general": "GENERAL",
        "sc/st": "SC",
        "obc": "OBC",
        " sc ": "SC",
        " st ": "ST",
        " ews ": "EWS",
        "पिछड़ा वर्ग": "OBC",       # Hindi
        "अनुसूचित जाति": "SC",       # Hindi
        "अनुसूचित जनजाति": "ST",     # Hindi
        "പട്ടിക ജാതി": "SC",         # Malayalam
        "പട്ടിക വർഗ്ഗം": "ST",       # Malayalam
        "ഒ.ബി.സി": "OBC",           # Malayalam
    }

    for keyword, cat in category_map.items():
        if keyword in text_lower:
            return cat

    return ""


def _extract_district(text_lower):
    """Extract Kerala district from document text."""
    kerala_districts = [
        "Thiruvananthapuram", "Kollam", "Pathanamthitta", "Alappuzha",
        "Kottayam", "Idukki", "Ernakulam", "Thrissur", "Palakkad",
        "Malappuram", "Kozhikode", "Wayanad", "Kannur", "Kasaragod",
    ]

    # Also include common alternate spellings
    district_aliases = {
        "trivandrum": "Thiruvananthapuram",
        "tvm": "Thiruvananthapuram",
        "cochin": "Ernakulam",
        "kochi": "Ernakulam",
        "calicut": "Kozhikode",
        "trichur": "Thrissur",
        "palghat": "Palakkad",
        "cannanore": "Kannur",
        "quilon": "Kollam",
        "alleppey": "Alappuzha",
        "തിരുവനന്തപുരം": "Thiruvananthapuram",
        "കൊല്ലം": "Kollam",
        "എറണാകുളം": "Ernakulam",
        "കോഴിക്കോട്": "Kozhikode",
        "മലപ്പുറം": "Malappuram",
        "തൃശ്ശൂർ": "Thrissur",
        "പാലക്കാട്": "Palakkad",
        "കണ്ണൂർ": "Kannur",
        "കാസർഗോഡ്": "Kasaragod",
        "വയനാട്": "Wayanad",
        "ഇടുക്കി": "Idukki",
        "കോട്ടയം": "Kottayam",
        "ആലപ്പുഴ": "Alappuzha",
        "പത്തനംതിട്ട": "Pathanamthitta",
    }

    # Check exact district names first
    for district in kerala_districts:
        if district.lower() in text_lower:
            return district

    # Check aliases
    for alias, district in district_aliases.items():
        if alias.lower() in text_lower:
            return district

    return ""
 
def _extract_age(text, text_lower):
    """Extract age or DOB from text."""
    # Look for DOB patterns: 12/05/1995, 1995-05-12
    dob_match = re.search(r"(?:dob|birth|date of birth)[:\s]*(\d{2}[/-]\d{2}[/-]\d{4})", text_lower)
    if dob_match:
        dob_str = dob_match.group(1)
        year = int(re.search(r"(\d{4})", dob_str).group(1))
        return 2026 - year # Assuming current year 2026
    
    # Look for "Age: 25"
    age_match = re.search(r"age[:\s]*(\d{1,3})", text_lower)
    if age_match:
        return int(age_match.group(1))
        
    # Just look for years like 19xx or 20xx and calculate age
    years = re.findall(r"(19\d{2}|20[012]\d)", text)
    if years:
        # Take the earliest year found (likely DOB)
        age = 2026 - int(min(years))
        if 5 <= age <= 100: return age
        
    return 0

def _extract_gender(text_lower):
    """Extract gender from text."""
    if "female" in text_lower or "സ്ത്രീ" in text_lower: return "Female"
    if "male" in text_lower or "പുരുഷൻ" in text_lower: return "Male"
    if "transgender" in text_lower or "മറ്റുള്ളവർ" in text_lower: return "Other"
    return ""