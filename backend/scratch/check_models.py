import os
try:
    import google.generativeai as genai
    from dotenv import load_dotenv
    load_dotenv()
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    for m in genai.list_models():
        print(m.name)
except Exception as e:
    print(f"FAILED: {e}")
