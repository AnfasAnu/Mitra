def check_eligibility(user, scheme):
    """Check if a user is eligible for a scheme and return detailed reasons."""
    reasons = []
    eligible = True

    # 1. Income check
    if user["income"] > scheme["income_limit"]:
        eligible = False
        reasons.append(f"❌ Income ₹{user['income']:,} exceeds scheme limit of ₹{scheme['income_limit']:,}")
    else:
        reasons.append(f"✅ Income ₹{user['income']:,} is within the ₹{scheme['income_limit']:,} limit")

    # 2. Category check
    if "All" not in scheme["category"] and user["category"] not in scheme["category"]:
        eligible = False
        reasons.append(f"❌ Category '{user['category']}' not in eligible categories: {', '.join(scheme['category'])}")
    else:
        if "All" in scheme["category"]:
            reasons.append("✅ Open to all categories")
        else:
            reasons.append(f"✅ Your category '{user['category']}' is eligible")

    # 3. District check
    districts = scheme.get("districts", ["All"])
    if "All" not in districts and user.get("district", "") not in districts:
        eligible = False
        reasons.append(f"❌ Not available in {user.get('district', 'your district')} — only in: {', '.join(districts)}")
    elif "All" not in districts:
        reasons.append(f"✅ Available in your district: {user.get('district', '')}")
    else:
        reasons.append("✅ Available across all Kerala districts")

    # 4. Age check
    user_age = user.get("age", 0)
    min_age = scheme.get("min_age", 0)
    max_age = scheme.get("max_age", 0)
    if user_age > 0:
        if min_age > 0 and user_age < min_age:
            eligible = False
            reasons.append(f"❌ Age {user_age} is below minimum required age of {min_age}")
        elif min_age > 0:
            reasons.append(f"✅ Age {user_age} meets minimum age requirement of {min_age}")

        if max_age > 0 and user_age > max_age:
            eligible = False
            reasons.append(f"❌ Age {user_age} exceeds maximum age limit of {max_age}")
        elif max_age > 0:
            reasons.append(f"✅ Age {user_age} is within maximum age limit of {max_age}")
    else:
        # Age not provided — skip age check but note if scheme has age requirement
        if min_age > 0 or max_age > 0:
            age_note = []
            if min_age > 0:
                age_note.append(f"min {min_age}")
            if max_age > 0:
                age_note.append(f"max {max_age}")
            reasons.append(f"ℹ️ Age requirement ({', '.join(age_note)}) — not checked (age not provided)")

    # 5. Gender check
    scheme_gender = scheme.get("gender", "All")
    user_gender = user.get("gender", "")
    if scheme_gender != "All" and user_gender:
        if user_gender.lower() != scheme_gender.lower():
            eligible = False
            reasons.append(f"❌ This scheme is for {scheme_gender} applicants only")
        else:
            reasons.append(f"✅ Gender '{user_gender}' matches scheme requirement")
    elif scheme_gender != "All" and not user_gender:
        reasons.append(f"ℹ️ This scheme is for {scheme_gender} only — not checked (gender not provided)")
    else:
        if scheme_gender == "All":
            reasons.append("✅ Open to all genders")

    # 6. Occupation check
    scheme_occupation = scheme.get("occupation", "All")
    user_occupation = user.get("occupation", "")
    if scheme_occupation != "All" and user_occupation:
        if user_occupation.lower() != scheme_occupation.lower():
            eligible = False
            reasons.append(f"❌ This scheme requires occupation: {scheme_occupation} (yours: {user_occupation})")
        else:
            reasons.append(f"✅ Occupation '{user_occupation}' matches scheme requirement")
    elif scheme_occupation != "All" and not user_occupation:
        reasons.append(f"ℹ️ Requires occupation: {scheme_occupation} — not checked (occupation not provided)")

    # 7. Education check
    scheme_education = scheme.get("education", "All")
    user_education = user.get("education", "")
    if scheme_education != "All" and user_education:
        if user_education.lower() != scheme_education.lower():
            eligible = False
            reasons.append(f"❌ This scheme requires: {scheme_education} (yours: {user_education})")
        else:
            reasons.append(f"✅ Education status '{user_education}' matches requirement")
    elif scheme_education != "All" and not user_education:
        reasons.append(f"ℹ️ Requires: {scheme_education} — not checked (education not provided)")

    # 8. Disability check
    disability_required = scheme.get("disability_required", False)
    user_disability = user.get("disability", False)
    if disability_required:
        if not user_disability:
            eligible = False
            reasons.append("❌ This scheme requires disability status (40%+ disability)")
        else:
            reasons.append("✅ Disability status verified — eligible")

    # 9. Marital status check
    scheme_marital = scheme.get("marital_status", "All")
    user_marital = user.get("marital_status", "")
    if scheme_marital != "All" and user_marital:
        if user_marital.lower() != scheme_marital.lower():
            eligible = False
            reasons.append(f"❌ This scheme is for {scheme_marital} applicants only (yours: {user_marital})")
        else:
            reasons.append(f"✅ Marital status '{user_marital}' matches requirement")
    elif scheme_marital != "All" and not user_marital:
        reasons.append(f"ℹ️ Requires marital status: {scheme_marital} — not checked (not provided)")

    summary = "Eligible" if eligible else "Not Eligible"
    return eligible, summary, reasons


def match_schemes(user, schemes):
    results = []

    for scheme in schemes:
        eligible, summary, reasons = check_eligibility(user, scheme)

        missing_docs = []
        for doc in scheme["documents"]:
            missing_docs.append(doc)

        # Calculate a relevance score for ranking
        score = 0
        if eligible:
            score += 100
            # Priority bonus (lower priority number = more important)
            score += (5 - scheme["priority"]) * 10
            # Income proximity bonus (closer to limit = more relevant)
            if scheme["income_limit"] > 0:
                income_ratio = user["income"] / scheme["income_limit"]
                score += int((1 - income_ratio) * 20)
            # District-specific bonus
            districts = scheme.get("districts", ["All"])
            if "All" not in districts and user.get("district", "") in districts:
                score += 15
            # Exact occupation match bonus
            if scheme.get("occupation", "All") != "All" and user.get("occupation", ""):
                if user["occupation"].lower() == scheme["occupation"].lower():
                    score += 10
            # Gender-specific scheme bonus
            if scheme.get("gender", "All") != "All" and user.get("gender", ""):
                if user["gender"].lower() == scheme["gender"].lower():
                    score += 10

        results.append({
            "name": scheme["name"],
            "eligible": eligible,
            "reason": summary,
            "eligibility_reasons": reasons,
            "priority": scheme["priority"],
            "documents": scheme["documents"],
            "missing_documents": missing_docs,
            "benefits": scheme["benefits"],
            "scheme_category": scheme.get("scheme_category", "General"),
            "type": scheme.get("type", "State"),
            "districts": scheme.get("districts", ["All"]),
            "deadline": scheme.get("deadline", ""),
            "added_date": scheme.get("added_date", ""),
            "application_url": scheme.get("application_url", ""),
            "how_to_apply": scheme.get("how_to_apply", []),
            "office": scheme.get("office", ""),
            "income_limit": scheme.get("income_limit", 0),
            "category": scheme.get("category", []),
            "gender": scheme.get("gender", "All"),
            "min_age": scheme.get("min_age", 0),
            "max_age": scheme.get("max_age", 0),
            "occupation": scheme.get("occupation", "All"),
            "education": scheme.get("education", "All"),
            "disability_required": scheme.get("disability_required", False),
            "marital_status": scheme.get("marital_status", "All"),
            "relevance_score": score
        })

    # Sort by relevance score (highest first)
    results = sorted(results, key=lambda x: (-x["relevance_score"], x["priority"]))
    return results