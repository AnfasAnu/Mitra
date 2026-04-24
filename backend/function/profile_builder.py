def build_profile(data):
    return {
        "email": data.get("email", ""),
        "phone": data.get("phone", ""),
        "income": int(data.get("income", 0)),
        "category": data.get("category", "").upper(),
        "district": data.get("district", ""),
        "age": int(data.get("age", 0)),
        "gender": data.get("gender", ""),
        "occupation": data.get("occupation", ""),
        "education": data.get("education", ""),
        "disability": bool(data.get("disability", False)),
        "marital_status": data.get("marital_status", ""),
    }