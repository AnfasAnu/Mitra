import streamlit as st
import requests
import json
import base64

st.set_page_config(page_title="K-AI Scheme Mitra", page_icon="🏛️", layout="wide", initial_sidebar_state="expanded")

API = "http://127.0.0.1:8000"
LANGS = {"Malayalam": "ml-IN", "English (India)": "en-IN", "Hindi": "hi-IN", "Tamil": "ta-IN", "Telugu": "te-IN", "Kannada": "kn-IN"}
SPEAKERS = {"Anila (Female)": "anila", "Shubh (Male)": "shubh", "Advika (Female)": "advika", "Mansi (Female)": "mansi"}
DISTRICTS = ["Thiruvananthapuram", "Kollam", "Pathanamthitta", "Alappuzha", "Kottayam", "Idukki", "Ernakulam", "Thrissur", "Palakkad", "Malappuram", "Kozhikode", "Wayanad", "Kannur", "Kasaragod"]
CATEGORIES = ["General", "OBC", "SC", "ST", "EWS"]
GENDERS = ["Male", "Female", "Other"]
OCCUPATIONS = ["Employed", "Unemployed", "Farmer", "Self-Employed", "Retired", "Homemaker"]
EDUCATIONS = ["Student", "Below 10th", "10th Pass", "12th Pass", "Graduate", "Post Graduate", "Diploma", "None"]
MARITAL_STATUSES = ["Single", "Married", "Widow", "Divorced", "Separated"]
CAT_ICONS = {"Housing":"🏠","Education":"🎓","Healthcare":"🏥","Pension":"👴","Women Empowerment":"👩","Agriculture":"🌾","Employment":"💼","Financial":"💰","Infrastructure":"🏗️","General":"📋"}
CAT_COLORS = {"Housing":("#f97316","rgba(249,115,22,0.12)"),"Education":("#8b5cf6","rgba(139,92,246,0.12)"),"Healthcare":("#ef4444","rgba(239,68,68,0.12)"),"Pension":("#06b6d4","rgba(6,182,212,0.12)"),"Women Empowerment":("#ec4899","rgba(236,72,153,0.12)"),"Agriculture":("#22c55e","rgba(34,197,94,0.12)"),"Employment":("#f59e0b","rgba(245,158,11,0.12)"),"Financial":("#3b82f6","rgba(59,130,246,0.12)"),"Infrastructure":("#a855f7","rgba(168,85,247,0.12)"),"General":("#94a3b8","rgba(148,163,184,0.12)")}

for k,d in [("analysis_results",None),("scan_results",None),("uploaded_file_name",None),("voice_transcript",None),("tts_audio",None),("chat_history",[]),("notifications",None),("compare_result",None),("authenticated",False),("username",None),("current_page","home"),("search_open",False),("profile",{}),("preferences",{}),("scheme_guides",{})]:
    if k not in st.session_state: st.session_state[k] = d

# --- CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
.stApp{font-family:'Inter',sans-serif}
.hero-container{background:linear-gradient(135deg,#0a1628 0%,#1a3a5c 40%,#0d7377 70%,#14a085 100%);border-radius:20px;padding:2.2rem 2.5rem;margin-bottom:1.5rem;position:relative;overflow:hidden;box-shadow:0 20px 60px rgba(10,22,40,0.4)}
.hero-container::before{content:'';position:absolute;top:-50%;right:-20%;width:500px;height:500px;background:radial-gradient(circle,rgba(20,160,133,0.15) 0%,transparent 70%);border-radius:50%}
.hero-badge{display:inline-block;background:rgba(255,255,255,0.1);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,0.15);color:#7de8d4;padding:6px 16px;border-radius:50px;font-size:0.72rem;font-weight:600;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:0.6rem}
.hero-title{font-size:2.4rem;font-weight:800;color:#fff;line-height:1.15;margin-bottom:0.3rem;position:relative;z-index:1}
.hero-title span{background:linear-gradient(90deg,#7de8d4,#4ecdc4);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.hero-subtitle{font-size:0.95rem;color:rgba(255,255,255,0.6);line-height:1.6;max-width:600px;position:relative;z-index:1}
.stat-row{display:flex;gap:1rem;margin-top:1rem;position:relative;z-index:1}
.stat-card{background:rgba(255,255,255,0.08);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,0.1);border-radius:12px;padding:10px 18px;text-align:center}
.stat-number{font-size:1.3rem;font-weight:700;color:#7de8d4}
.stat-label{font-size:0.65rem;color:rgba(255,255,255,0.5);text-transform:uppercase;letter-spacing:1px}
.section-header{display:flex;align-items:center;gap:10px;margin-bottom:1rem;margin-top:0.5rem}
.section-icon{width:38px;height:38px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1.1rem}
.section-icon.green{background:rgba(20,160,133,0.15)}.section-icon.blue{background:rgba(59,130,246,0.15)}.section-icon.purple{background:rgba(139,92,246,0.15)}
.section-title{font-size:1.15rem;font-weight:700;color:#e2e8f0}
.section-subtitle{font-size:0.73rem;color:#94a3b8}
.custom-divider{height:1px;background:linear-gradient(90deg,transparent,rgba(78,205,196,0.3),transparent);margin:1.2rem 0;border:none}
.ai-output-box{background:linear-gradient(135deg,rgba(13,115,119,0.08),rgba(20,160,133,0.05));border:1px solid rgba(78,205,196,0.15);border-radius:16px;padding:1.5rem;line-height:1.7;color:#cbd5e1;font-size:0.88rem}
.ai-output-box strong,.ai-output-box b{color:#7de8d4}
.scan-card{background:linear-gradient(135deg,rgba(30,41,59,0.9),rgba(15,23,42,0.95));border:1px solid rgba(78,205,196,0.2);border-radius:20px;padding:1.8rem;margin-bottom:1.5rem;position:relative;overflow:hidden}
.scan-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,#0d7377,#4ecdc4,#7de8d4)}
.scan-card-title{font-size:1.05rem;font-weight:700;color:#e2e8f0;margin-bottom:1rem;display:flex;align-items:center;gap:10px}
.scan-field{display:flex;align-items:center;justify-content:space-between;padding:0.8rem 1rem;border-radius:12px;margin-bottom:0.5rem}
.scan-field.found{background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2)}
.scan-field.missing{background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2)}
.scan-field-label{font-size:0.82rem;font-weight:600}
.scan-field-value{font-size:0.85rem;font-weight:500}
.scan-field.found .scan-field-label{color:#6ee7b7}.scan-field.found .scan-field-value{color:#a7f3d0}
.scan-field.missing .scan-field-label{color:#fca5a5}.scan-field.missing .scan-field-value{color:#fca5a5;font-style:italic}
.detail-section{background:rgba(15,23,42,0.5);border:1px solid rgba(255,255,255,0.06);border-radius:12px;padding:1rem;margin-bottom:0.6rem}
.detail-title{font-size:0.75rem;font-weight:600;text-transform:uppercase;letter-spacing:1px;margin-bottom:0.6rem;display:flex;align-items:center;gap:6px}
.doc-item{display:flex;align-items:center;gap:8px;padding:6px 10px;border-radius:8px;margin-bottom:4px;font-size:0.82rem}
.doc-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.doc-dot.blue{background:#3b82f6}.doc-dot.red{background:#ef4444}.doc-dot.green{background:#10b981}
.type-badge{display:inline-flex;align-items:center;gap:4px;padding:4px 12px;border-radius:20px;font-size:0.7rem;font-weight:600}
.type-badge.central{background:rgba(59,130,246,0.12);color:#93c5fd}
.type-badge.state{background:rgba(34,197,94,0.12);color:#86efac}
.stButton>button{background:linear-gradient(135deg,#0d7377,#14a085)!important;color:white!important;border:none!important;border-radius:12px!important;padding:0.6rem 1.5rem!important;font-weight:600!important;font-size:0.92rem!important;transition:all 0.3s ease!important;box-shadow:0 4px 15px rgba(13,115,119,0.3)!important}
.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 8px 25px rgba(13,115,119,0.4)!important}
.streamlit-expanderHeader{background:linear-gradient(135deg,rgba(30,41,59,0.9),rgba(15,23,42,0.95))!important;border:1px solid rgba(255,255,255,0.08)!important;border-radius:14px!important;padding:0.9rem 1.2rem!important;font-weight:600!important;color:#e2e8f0!important}
.streamlit-expanderContent{background:linear-gradient(135deg,rgba(15,23,42,0.6),rgba(30,41,59,0.4))!important;border:1px solid rgba(255,255,255,0.05)!important;border-top:none!important;border-radius:0 0 14px 14px!important;padding:1.2rem!important}
.stTabs [data-baseweb="tab-list"]{gap:4px;justify-content:center}
.stTabs [data-baseweb="tab"]{background:rgba(30,41,59,0.5);border-radius:10px;padding:8px 16px;border:1px solid rgba(255,255,255,0.06)}
.stTabs [aria-selected="true"]{background:rgba(13,115,119,0.2)!important;border-color:rgba(78,205,196,0.3)!important}
.chat-msg{padding:1rem;border-radius:14px;margin-bottom:0.8rem;font-size:0.88rem;line-height:1.7}
.chat-user{background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.2);color:#93c5fd}
.chat-ai{background:rgba(13,115,119,0.08);border:1px solid rgba(78,205,196,0.15);color:#cbd5e1}
.notif-card{padding:0.8rem 1rem;border-radius:12px;margin-bottom:0.5rem;font-size:0.82rem}
.notif-high{background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);color:#fca5a5}
.notif-medium{background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.2);color:#fcd34d}
.notif-low{background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.2);color:#86efac}
.footer{text-align:center;padding:2rem 0 1rem;color:#475569;font-size:0.8rem}
.footer a{color:#4ecdc4;text-decoration:none}
#MainMenu{visibility:hidden}footer{visibility:hidden}
header[data-testid="stHeader"]{background:transparent!important}
header[data-testid="stHeader"] .stDeployButton,header[data-testid="stHeader"] .stToolbar{visibility:hidden}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#0a1628 0%,#111d32 100%);border-right:1px solid rgba(78,205,196,0.1)}
section[data-testid="stSidebar"] .stMarkdown p{color:#94a3b8}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════
# AUTH PAGE
# ══════════════════════════════════════════════════
if not st.session_state.authenticated:
    st.markdown("""
    <div style="max-width:520px;margin:2.5rem auto 1.5rem;text-align:center;">
        <div style="font-size:3.2rem;margin-bottom:0.5rem;">🏛️</div>
        <div class="hero-badge">🤖 AI-Powered Governance • Kerala IT Policy 2026</div>
        <div class="hero-title" style="font-size:2.2rem;margin:0.6rem 0 0.3rem;color:#fff;">K-AI <span>Scheme Mitra</span></div>
        <div class="hero-subtitle" style="margin:0 auto;max-width:420px;">Your intelligent navigator for Kerala government welfare schemes</div>
    </div>
    """, unsafe_allow_html=True)
    _, auth_col, _ = st.columns([1, 1.8, 1])
    with auth_col:
        st.markdown("""<div class="scan-card" style="padding:2rem;">""", unsafe_allow_html=True)
        login_tab, register_tab = st.tabs(["🔑 Sign In", "📝 Create Account"])
        with login_tab:
            login_user = st.text_input("Username", placeholder="Enter your username", key="login_user")
            login_pass = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pass")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔑 Sign In", use_container_width=True, key="login_btn"):
                if not login_user or not login_pass:
                    st.warning("Please enter both username and password")
                else:
                    with st.spinner("Signing in..."):
                        try:
                            r = requests.post(f"{API}/auth/login", json={"username":login_user,"password":login_pass}, timeout=10)
                            if r.status_code==200 and r.json().get("success"):
                                st.session_state.authenticated = True
                                st.session_state.username = login_user
                                st.session_state.profile = r.json().get("saved_profile", {})
                                st.rerun()
                            else:
                                st.error(r.json().get("error","Invalid credentials") if r.status_code==200 else f"Server error: {r.status_code}")
                        except Exception as e: st.error(f"Backend not reachable: {e}")
        with register_tab:
            reg_user = st.text_input("Choose a username", placeholder="e.g. rahul_kerala", key="reg_user")
            reg_pass = st.text_input("Create password", type="password", placeholder="Min 4 characters", key="reg_pass")
            reg_pass2 = st.text_input("Confirm password", type="password", placeholder="Re-enter password", key="reg_pass2")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📝 Create Account", use_container_width=True, key="reg_btn"):
                if not reg_user or not reg_pass: st.warning("Please fill all fields")
                elif reg_pass != reg_pass2: st.error("Passwords do not match")
                elif len(reg_pass) < 4: st.warning("Password must be at least 4 characters")
                else:
                    with st.spinner("Creating account..."):
                        try:
                            r = requests.post(f"{API}/auth/register", json={"username":reg_user,"password":reg_pass}, timeout=10)
                            if r.status_code==200 and r.json().get("success"):
                                st.success("✅ Account created! Switch to **Sign In** tab to login.")
                            else:
                                st.error(r.json().get("error","Registration failed") if r.status_code==200 else f"Server error: {r.status_code}")
                        except Exception as e: st.error(f"Backend not reachable: {e}")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div style="text-align:center;font-size:0.8rem;color:#64748b;margin-bottom:0.6rem;">Don\'t want to create an account?</div>', unsafe_allow_html=True)
        if st.button("👤 Continue as Guest", use_container_width=True, key="guest_btn"):
            st.session_state.authenticated = True; st.session_state.username = "Guest"; st.rerun()
        st.markdown('<div style="text-align:center;font-size:0.68rem;color:#475569;margin-top:0.4rem;">⚠️ Guest mode — your session data will not be saved</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    feat_cols = st.columns(4)
    for col,(icon,title,desc) in zip(feat_cols, [("🧠","AI Recommendations","Smart scheme ranking"),("🎙️","Voice & Multilingual","Speak in Malayalam, Hindi..."),("📸","Document Scan","Auto-extract from Aadhaar"),("🤖","AI Chatbot","Ask anything about schemes")]):
        with col:
            st.markdown(f"""<div style="text-align:center;padding:1.2rem 0.8rem;background:rgba(30,41,59,0.5);border-radius:16px;border:1px solid rgba(255,255,255,0.05);"><div style="font-size:1.6rem;margin-bottom:0.3rem;">{icon}</div><div style="font-size:0.82rem;font-weight:600;color:#e2e8f0;">{title}</div><div style="font-size:0.68rem;color:#64748b;margin-top:2px;">{desc}</div></div>""", unsafe_allow_html=True)
    st.stop()


# ══════════════════════════════════════════════════
# SIDEBAR — Navigation
# ══════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""<div style="text-align:center;padding:1rem 0 0.5rem;">
        <div style="font-size:1.8rem;">🏛️</div>
        <div style="font-size:1.1rem;font-weight:800;color:#fff;margin-top:0.3rem;">K-AI <span style="color:#4ecdc4;">Mitra</span></div>
        <div style="font-size:0.7rem;color:#64748b;margin-top:2px;">{'Guest' if st.session_state.username=='Guest' else st.session_state.username}</div>
    </div>""", unsafe_allow_html=True)
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    if st.button("🏠 Home", use_container_width=True, key="nav_home"):
        st.session_state.current_page = "home"; st.session_state.search_open = False; st.rerun()
    if st.button("🔍 Search Schemes", use_container_width=True, key="nav_search"):
        st.session_state.current_page = "search"; st.session_state.search_open = True; st.rerun()
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    if st.button("📊 Compare Schemes", use_container_width=True, key="nav_compare"):
        st.session_state.current_page = "compare"; st.rerun()
    if st.button("🤖 AI Chatbot", use_container_width=True, key="nav_chat"):
        st.session_state.current_page = "chatbot"; st.rerun()
    if st.button("🔔 Notifications", use_container_width=True, key="nav_notif"):
        st.session_state.current_page = "notifications"; st.rerun()

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    if st.button("⚙️ Settings", use_container_width=True, key="nav_settings"):
        st.session_state.current_page = "settings"; st.rerun()

    st.markdown("<br>" * 3, unsafe_allow_html=True)

    if st.button("🚪 End Session", use_container_width=True, key="nav_logout"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

    st.markdown(f'<div style="text-align:center;font-size:0.6rem;color:#475569;margin-top:1rem;">v2.0 • Kerala IT Policy 2026</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════
def render_scheme_cards(scheme_list, show_category_tag=True):
    for scheme in scheme_list:
        p_label = "⚡ High" if scheme["priority"]==1 else "📌 Med"
        cat = scheme.get("scheme_category","General")
        ci = CAT_ICONS.get(cat,"📋")
        cat_label = f" │ {ci} {cat}" if show_category_tag else ""
        dc = len(scheme.get('documents',[])); mc = len(scheme.get('missing_documents',[]))
        ds = f"📄 {dc-mc}/{dc}" if mc<dc else f"⚠️ 0/{dc}"
        score = scheme.get("relevance_score", 0)
        score_badge = f" │ 🎯 {score}pts" if score > 0 else ""
        with st.expander(f"✅ {scheme['name']}  │  {p_label}{cat_label}{score_badge}  │  {ds} docs", expanded=False):
            st_type = scheme.get('type','State')
            tc = 'central' if st_type=='Central' else 'state'
            cc,cb = CAT_COLORS.get(cat, CAT_COLORS['General'])
            st.markdown(f"""<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:1rem;">
                <div style="font-size:0.9rem;color:#94a3b8;line-height:1.6;flex:1;">{scheme['benefits']}</div>
                <div style="display:flex;gap:6px;flex-shrink:0;margin-left:1rem;">
                    <span class="type-badge {tc}">🏛️ {st_type}</span>
                    <span class="type-badge" style="background:{cb};color:{cc};">{ci} {cat}</span>
                </div></div>""", unsafe_allow_html=True)
            reasons = scheme.get("eligibility_reasons", [])
            if reasons:
                r_html = "".join(f'<div style="padding:4px 0;font-size:0.82rem;color:#7de8d4;">✅ {r}</div>' for r in reasons)
                st.markdown(f'<div class="detail-section" style="border-color:rgba(78,205,196,0.15);"><div class="detail-title" style="color:#7de8d4;">🧠 Why You\'re Eligible</div>{r_html}</div>', unsafe_allow_html=True)
            c1,c2 = st.columns(2)
            with c1:
                docs_html = "".join(f'<div class="doc-item"><div class="doc-dot blue"></div>{doc}</div>' for doc in scheme['documents'])
                st.markdown(f'<div class="detail-section"><div class="detail-title" style="color:#7de8d4;">📄 Required Documents</div>{docs_html}</div>', unsafe_allow_html=True)
            with c2:
                steps = scheme.get('how_to_apply', [])
                if steps:
                    s_html = "".join(f'<div style="padding:3px 0;font-size:0.8rem;color:#94a3b8;">{i+1}. {s}</div>' for i,s in enumerate(steps))
                    st.markdown(f'<div class="detail-section"><div class="detail-title" style="color:#f9a8d4;">🧾 How to Apply</div>{s_html}</div>', unsafe_allow_html=True)
            info_parts = []
            if scheme.get('office'): info_parts.append(f"🏢 <b>{scheme['office']}</b>")
            if scheme.get('deadline'): info_parts.append(f"⏰ Deadline: <b>{scheme['deadline']}</b>")
            if scheme.get('application_url'):
                info_parts.append(f"🔗 <a href='{scheme['application_url']}' style='color:#4ecdc4;'>{scheme['application_url']}</a>")
                info_parts.append(f"<a href='{scheme['application_url']}' target='_blank' style='display:inline-block;margin-top:6px;padding:6px 18px;background:linear-gradient(135deg,#0d7377,#14a085);color:white;border-radius:8px;font-size:0.78rem;font-weight:600;text-decoration:none;'>🚀 Apply Now →</a>")
            if info_parts:
                st.markdown(f'<div style="padding:0.6rem;background:rgba(15,23,42,0.5);border-radius:10px;font-size:0.78rem;color:#94a3b8;line-height:1.8;">{"<br>".join(info_parts)}</div>', unsafe_allow_html=True)
            
            # --- AI Guidance Toggle ---
            st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)
            guide_key = f"guide_{scheme['name']}"
            if guide_key not in st.session_state.scheme_guides:
                if st.button(f"🪄 Generate AI Application Guide", key=f"btn_{scheme['name']}", use_container_width=True):
                    with st.spinner("🧠 Gemini is analyzing..."):
                        try:
                            r = requests.post(f"{API}/scheme-guide", json={"user":st.session_state.profile, "scheme":scheme}, timeout=45)
                            if r.status_code==200 and r.json().get("success"):
                                st.session_state.scheme_guides[guide_key] = r.json()["ai_output"]
                                st.rerun()
                            else: st.error("AI service busy")
                        except: st.error("Connection failed")
            else:
                st.markdown(f"""<div style="padding:1rem;background:rgba(139,92,246,0.06);border:1px solid rgba(139,92,246,0.15);border-radius:12px;margin-top:0.5rem;">
                    <div style="font-size:0.85rem;font-weight:700;color:#c4b5fd;margin-bottom:0.6rem;display:flex;align-items:center;gap:8px;"><span>🪄</span> AI Personalized Roadmap</div>
                    <div style="font-size:0.82rem;color:#d1d5db;line-height:1.6;white-space:pre-wrap;">{st.session_state.scheme_guides[guide_key]}</div>
                </div>""", unsafe_allow_html=True)
                if st.button("🗑️ Clear Guide", key=f"clr_{scheme['name']}", use_container_width=True):
                    del st.session_state.scheme_guides[guide_key]; st.rerun()

def do_tts(text, key_prefix):
    tc1,tc2 = st.columns(2)
    with tc1: lang = st.selectbox("🌐 Language", list(LANGS.keys()), index=0, key=f"{key_prefix}_l")
    with tc2: spk = st.selectbox("🗣️ Voice", list(SPEAKERS.keys()), index=0, key=f"{key_prefix}_s")
    if st.button("🔊 Listen", key=f"{key_prefix}_btn", use_container_width=True):
        with st.spinner("🔊 Generating voice..."):
            try:
                clean = text.replace("**","").replace("*","").replace("#","")[:2500]
                r = requests.post(f"{API}/voice/tts", json={"text":clean,"language":LANGS[lang],"speaker":SPEAKERS[spk]}, timeout=30)
                if r.status_code==200 and r.json().get("success"):
                    st.audio(base64.b64decode(r.json()["audio_base64"]), format="audio/wav")
                else: st.warning(f"TTS: {r.json().get('error','Failed')}")
            except Exception as e: st.error(f"Voice error: {e}")

def do_translate(text, key_prefix):
    tr1, tr2 = st.columns(2)
    with tr1: sl = st.selectbox("📥 Source", list(LANGS.keys()), index=1, key=f"{key_prefix}_sl")
    with tr2: tl = st.selectbox("📤 Translate to", list(LANGS.keys()), index=0, key=f"{key_prefix}_tl")
    if st.button("🌐 Translate", key=f"{key_prefix}_tr", use_container_width=True):
        with st.spinner("Translating..."):
            try:
                r = requests.post(f"{API}/translate", json={"text":text[:5000],"source_language":LANGS[sl],"target_language":LANGS[tl]}, timeout=30)
                if r.status_code==200 and r.json().get("success"):
                    st.markdown(f'<div class="ai-output-box">{r.json()["translated_text"]}</div>', unsafe_allow_html=True)
                else: st.warning(f"Translation: {r.json().get('error','Failed')}")
            except Exception as e: st.error(f"Error: {e}")


# ══════════════════════════════════════════════════
# PAGE: HOME
# ══════════════════════════════════════════════════
if st.session_state.current_page == "home":
    st.markdown(f"""
    <div class="hero-container">
        <div class="hero-badge">🤖 AI-Powered Governance • Kerala IT Policy 2026</div>
        <div class="hero-title">K-AI <span>Scheme Mitra</span></div>
        <div class="hero-subtitle">{'Guest session' if st.session_state.username=='Guest' else f'Welcome back, <b>{st.session_state.username}</b>!'} — Find, compare & apply for Kerala government welfare schemes with AI assistance.</div>
        <div class="stat-row">
            <div class="stat-card"><div class="stat-number">45</div><div class="stat-label">Schemes</div></div>
            <div class="stat-card"><div class="stat-number">9</div><div class="stat-label">Categories</div></div>
            <div class="stat-card"><div class="stat-number">AI</div><div class="stat-label">Gemini 2.0</div></div>
            <div class="stat-card"><div class="stat-number">6+</div><div class="stat-label">Languages</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Big search button
    st.markdown("<br>", unsafe_allow_html=True)
    _, btn_col, _ = st.columns([1, 2, 1])
    with btn_col:
        if st.button("🔍  Search for Eligible Schemes", use_container_width=True, key="home_search"):
            st.session_state.current_page = "search"; st.session_state.search_open = True; st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Quick action cards
    q1, q2, q3, q4 = st.columns(4)
    with q1:
        st.markdown("""<div style="text-align:center;padding:1.5rem 1rem;background:rgba(30,41,59,0.5);border-radius:16px;border:1px solid rgba(78,205,196,0.1);">
            <div style="font-size:2rem;margin-bottom:0.4rem;">🏛️</div>
            <div style="font-size:0.88rem;font-weight:700;color:#e2e8f0;">Navigator</div>
            <div style="font-size:0.7rem;color:#64748b;margin-top:4px;">Enter profile & get AI-ranked schemes</div>
        </div>""", unsafe_allow_html=True)
    with q2:
        st.markdown("""<div style="text-align:center;padding:1.5rem 1rem;background:rgba(30,41,59,0.5);border-radius:16px;border:1px solid rgba(139,92,246,0.1);">
            <div style="font-size:2rem;margin-bottom:0.4rem;">📸</div>
            <div style="font-size:0.88rem;font-weight:700;color:#e2e8f0;">Scanner</div>
            <div style="font-size:0.7rem;color:#64748b;margin-top:4px;">Upload docs, auto-extract details</div>
        </div>""", unsafe_allow_html=True)
    with q3:
        st.markdown("""<div style="text-align:center;padding:1.5rem 1rem;background:rgba(30,41,59,0.5);border-radius:16px;border:1px solid rgba(236,72,153,0.1);">
            <div style="font-size:2rem;margin-bottom:0.4rem;">🎙️</div>
            <div style="font-size:0.88rem;font-weight:700;color:#e2e8f0;">Voice</div>
            <div style="font-size:0.7rem;color:#64748b;margin-top:4px;">Speak and auto-fill your profile</div>
        </div>""", unsafe_allow_html=True)
    with q4:
        st.markdown("""<div style="text-align:center;padding:1.5rem 1rem;background:rgba(30,41,59,0.5);border-radius:16px;border:1px solid rgba(245,158,11,0.1);">
            <div style="font-size:2rem;margin-bottom:0.4rem;">🔔</div>
            <div style="font-size:0.88rem;font-weight:700;color:#e2e8f0;">Notifications</div>
            <div style="font-size:0.7rem;color:#64748b;margin-top:4px;">Deadline alerts & new schemes</div>
        </div>""", unsafe_allow_html=True)

    # About this app
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown("""<div class="scan-card">
        <div class="scan-card-title">🏛️ About K-AI Scheme Mitra</div>
        <div style="font-size:0.88rem;color:#94a3b8;line-height:1.9;">
            <b style="color:#7de8d4;">K-AI Scheme Mitra</b> is an AI-powered citizen welfare navigator built for Kerala, aligned with the <b style="color:#7de8d4;">Kerala IT Policy 2026</b>. It helps citizens discover government schemes they are eligible for — without manually searching through hundreds of policies.<br><br>
            <b style="color:#e2e8f0;">🧠 How it works:</b> Enter your profile (income, category, district, age, etc.) or simply <b style="color:#f9a8d4;">speak</b> or <b style="color:#f9a8d4;">upload a document</b> — the AI automatically finds, ranks, and explains every scheme you qualify for, with step-by-step application guidance.<br><br>
            <b style="color:#e2e8f0;">✨ Key Features:</b><br>
            &nbsp;&nbsp;• <b style="color:#7de8d4;">AI Recommendations</b> — Schemes ranked by relevance with eligibility explanations<br>
            &nbsp;&nbsp;• <b style="color:#7de8d4;">Voice & Multilingual</b> — Speak in Malayalam, Hindi, Tamil & more<br>
            &nbsp;&nbsp;• <b style="color:#7de8d4;">Document Scan</b> — Upload Aadhaar/Ration Card, AI extracts your data<br>
            &nbsp;&nbsp;• <b style="color:#7de8d4;">AI Chatbot</b> — Ask anything about schemes in natural language<br>
            &nbsp;&nbsp;• <b style="color:#7de8d4;">Scheme Comparison</b> — Compare benefits side-by-side<br>
            &nbsp;&nbsp;• <b style="color:#7de8d4;">Deadline Alerts</b> — Never miss an application deadline<br><br>
            <b style="color:#e2e8f0;">🔒 Privacy First:</b> No user data is stored. Your profile is processed in-memory and discarded after each session.<br>
        </div>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════
# PAGE: SEARCH (Navigator + Scanner + Voice)
# ══════════════════════════════════════════════════
elif st.session_state.current_page == "search":
    st.markdown("""<div class="section-header"><div class="section-icon green">🔍</div><div><div class="section-title">Search for Eligible Schemes</div><div class="section-subtitle">Choose your input method below</div></div></div>""", unsafe_allow_html=True)

    search_tab1, search_tab2, search_tab3 = st.tabs(["🏛️ Navigator", "📸 Scanner", "🎙️ Voice"])

    # ── NAVIGATOR TAB ──
    with search_tab1:
        st.markdown("""<div class="section-header"><div class="section-icon green">📋</div><div><div class="section-title">Enter Your Profile</div><div class="section-subtitle">AI will rank schemes by relevance and explain why you qualify</div></div></div>""", unsafe_allow_html=True)
        
        p = st.session_state.profile
        c1,c2 = st.columns(2)
        with c1: email = st.text_input("📧 Email Address", value=p.get("email",""), placeholder="To receive deadline alerts")
        with c2: phone = st.text_input("📱 Phone Number", value=p.get("phone",""), placeholder="For SMS notifications")
        
        c1,c2,c3 = st.columns(3)
        with c1: income = st.number_input("💰 Annual Income (₹)", min_value=0, max_value=10000000, value=p.get("income", 150000), step=10000)
        with c2: category = st.selectbox("🏷️ Category", CATEGORIES, index=CATEGORIES.index(p.get("category").capitalize()) if p.get("category") and p.get("category").capitalize() in CATEGORIES else 0)
        with c3: district = st.selectbox("📍 District", DISTRICTS, index=DISTRICTS.index(p.get("district")) if p.get("district") in DISTRICTS else 0)
        c4,c5,c6 = st.columns(3)
        with c4: age = st.number_input("🎂 Age", min_value=0, max_value=120, value=p.get("age", 25), step=1)
        with c5: gender = st.selectbox("👤 Gender", GENDERS, index=GENDERS.index(p.get("gender")) if p.get("gender") in GENDERS else 0)
        with c6: occupation = st.selectbox("💼 Occupation", OCCUPATIONS, index=OCCUPATIONS.index(p.get("occupation")) if p.get("occupation") in OCCUPATIONS else 0)
        c7,c8,c9 = st.columns(3)
        with c7: education = st.selectbox("🎓 Education", EDUCATIONS, index=EDUCATIONS.index(p.get("education")) if p.get("education") in EDUCATIONS else 0)
        with c8: marital_status = st.selectbox("💍 Marital Status", MARITAL_STATUSES, index=MARITAL_STATUSES.index(p.get("marital_status")) if p.get("marital_status") in MARITAL_STATUSES else 0)
        with c9: disability = st.checkbox("♿ Person with Disability (40%+)", value=p.get("disability", False))

        st.markdown('<div style="margin-top:10px;"></div>', unsafe_allow_html=True)
        allow_store = st.checkbox("🔔 Save this information to my profile for personalized alerts and proactive notifications", 
                                  value=True if p else False, key="allow_store")

        if st.button("🔍 Find Schemes", use_container_width=True, key="analyze_btn"):
            with st.spinner("🧠 AI is analyzing your eligibility and ranking schemes..."):
                try:
                    payload = {"email":email,"phone":phone,"income":income,"category":category.upper(),"district":district,"age":age,"gender":gender,"occupation":occupation,"education":education,"disability":disability,"marital_status":marital_status}
                    r = requests.post(f"{API}/analyze", json=payload, timeout=60)
                    if r.status_code==200:
                        st.session_state.analysis_results = r.json(); st.session_state.scan_results = None; st.session_state.ai_roadmap = None
                        
                        # Optionally save to database if requested and not Guest
                        if allow_store and st.session_state.username != "Guest":
                            save_payload = {"username":st.session_state.username, **payload}
                            rs = requests.post(f"{API}/profile/save", json=save_payload, timeout=10)
                            if rs.status_code==200: 
                                st.session_state.profile = save_payload
                        
                        st.rerun()
                    else: st.error(f"Backend error: {r.status_code}")
                except Exception as e: st.error(f"Error: {e}")
        
        if st.session_state.username == "Guest":
            st.markdown('<div style="font-size:0.75rem;color:#64748b;font-style:italic;">⚠️ Guest mode: Data is only used for this search and will not be stored.</div>', unsafe_allow_html=True)

    # ── SCANNER TAB ──
    with search_tab2:
        sc,rc = st.columns([1,1], gap="large")
        with sc:
            st.markdown("""<div class="section-header"><div class="section-icon blue">📤</div><div><div class="section-title">Upload Document</div><div class="section-subtitle">Ration Card, Income Certificate, Aadhar (PNG, JPG, PDF)</div></div></div>""", unsafe_allow_html=True)
            uploaded_file = st.file_uploader("Upload document", type=["png","jpg","jpeg","pdf"], label_visibility="collapsed")
            if uploaded_file:
                st.session_state.uploaded_file_name = uploaded_file.name
                st.image(uploaded_file, caption=f"📎 {uploaded_file.name}", use_container_width=True)
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
            ov_inc = st.number_input("💰 Income (0=use scanned)", min_value=0, max_value=10000000, value=0, step=10000, key="s_inc")
            ov_cat = st.selectbox("🏷️ Category", ["-- Use Scanned --"]+CATEGORIES, key="s_cat")
            ov_dist = st.selectbox("📍 District", ["-- Use Scanned --"]+DISTRICTS, key="s_dist")
            if st.button("🔍 Scan & Analyze", use_container_width=True, disabled=not uploaded_file, key="scan_btn"):
                if uploaded_file:
                    with st.spinner("📸 Scanning document with AI Vision..."):
                        try:
                            files = {"file":(uploaded_file.name,uploaded_file.getvalue(),uploaded_file.type)}
                            fd = {}
                            if ov_inc>0: fd["income"]=str(ov_inc)
                            if ov_cat!="-- Use Scanned --": fd["category"]=ov_cat
                            if ov_dist!="-- Use Scanned --": fd["district"]=ov_dist
                            r = requests.post(f"{API}/upload", files=files, data=fd, timeout=60)
                            if r.status_code==200:
                                st.session_state.analysis_results = r.json()
                                st.session_state.scan_results = r.json().get("scan_results",{})
                                # Update session profile with extracted fields
                                user_data = r.json().get("user", {})
                                for k, v in user_data.items():
                                    st.session_state.profile[k] = v
                                st.success("✅ Scanned!"); st.rerun()
                            else: st.error(f"Error: {r.status_code}")
                        except Exception as e: st.error(f"Error: {e}")
        with rc:
            if st.session_state.scan_results:
                sd = st.session_state.scan_results
                ext = sd.get("extracted_fields",{}); mis = sd.get("missing_fields",[])
                st.markdown(f'<div class="scan-card"><div class="scan-card-title">📋 Scan Results — {len(ext)} fields extracted</div>', unsafe_allow_html=True)
                
                # All possible fields with labels and formatters
                all_fields = [
                    ("income", "💰 Income", lambda v: f"₹{v:,}"),
                    ("category", "🏷️ Category", str),
                    ("district", "📍 District", str),
                    ("age", "🎂 Age", lambda v: f"{v} years"),
                    ("gender", "👤 Gender", str),
                ]
                
                for field_key, label, fmt in all_fields:
                    if field_key in ext:
                        val = fmt(ext[field_key])
                        st.markdown(f'<div class="scan-field found"><div class="scan-field-label">{label}</div><div class="scan-field-value">✅ {val}</div></div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="scan-field missing"><div class="scan-field-label">{label}</div><div class="scan-field-value">❌ Not found</div></div>', unsafe_allow_html=True)
                
                if ext:
                    st.markdown('<div style="margin-top:12px;font-size:0.75rem;color:#4ecdc4;">💡 Extracted data has been auto-filled in the Navigator tab. Review and click "Find Schemes" to search.</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown("""<div style="text-align:center;padding:4rem 2rem;"><div style="font-size:3.5rem;margin-bottom:1rem;">📸</div><div style="font-size:1.2rem;font-weight:700;color:#e2e8f0;">Upload a Document</div><div style="font-size:0.8rem;color:#64748b;margin-top:0.4rem;">AI will extract your details automatically</div></div>""", unsafe_allow_html=True)

    # ── VOICE TAB ──
    with search_tab3:
        vl,vr = st.columns([1,1], gap="large")
        with vl:
            st.markdown("""<div class="section-header"><div class="section-icon" style="background:rgba(236,72,153,0.15);">🎙️</div><div><div class="section-title">Voice Input</div><div class="section-subtitle">Speak your profile — AI auto-extracts income, category & district</div></div></div>""", unsafe_allow_html=True)
            stt_lang = st.selectbox("🌐 Speaking Language", list(LANGS.keys()), index=0, key="stt_lang")
            audio_input = st.audio_input("🎙️ Click to record", key="voice_rec")
            if audio_input:
                st.audio(audio_input, format="audio/wav")
                vc1,vc2 = st.columns(2)
                with vc1:
                    if st.button("📝 Transcribe", key="stt_btn", use_container_width=True):
                        with st.spinner("🎙️ Transcribing..."):
                            try:
                                r = requests.post(f"{API}/voice/stt", files={"file":("audio.wav",audio_input.getvalue(),"audio/wav")}, data={"language":LANGS[stt_lang]}, timeout=30)
                                if r.status_code==200 and r.json().get("success"):
                                    st.session_state.voice_transcript = r.json()["transcript"]; st.rerun()
                                else: st.error(f"STT: {r.json().get('error','Failed')}")
                            except Exception as e: st.error(f"Error: {e}")
                with vc2:
                    if st.button("🧠 Speak & Auto-Fill", key="autofill_btn", use_container_width=True):
                        with st.spinner("🎙️ Transcribing & extracting profile..."):
                            try:
                                r = requests.post(f"{API}/voice/stt", files={"file":("audio.wav",audio_input.getvalue(),"audio/wav")}, data={"language":LANGS[stt_lang]}, timeout=30)
                                if r.status_code==200 and r.json().get("success"):
                                    transcript = r.json()["transcript"]; st.session_state.voice_transcript = transcript
                                    r2 = requests.post(f"{API}/voice/parse", json={"transcript":transcript}, timeout=30)
                                    if r2.status_code==200:
                                        parsed = r2.json().get("parsed_profile",{})
                                        st.success(f"✅ Extracted: Income=₹{parsed.get('income',0):,}, Category={parsed.get('category','')}, District={parsed.get('district','')}")
                                        # Update session profile
                                        for k, v in parsed.items():
                                            st.session_state.profile[k] = v
                                        
                                        if parsed.get("income",0)>0 or parsed.get("category","") or parsed.get("district",""):
                                            r3 = requests.post(f"{API}/analyze", json={"income":parsed.get("income",0),"category":parsed.get("category","").upper(),"district":parsed.get("district","")}, timeout=60)
                                            if r3.status_code==200:
                                                st.session_state.analysis_results = r3.json(); st.session_state.scan_results = None
                                else: st.error(f"STT: {r.json().get('error','Failed')}")
                            except Exception as e: st.error(f"Error: {e}")
            if st.session_state.voice_transcript:
                st.markdown(f'<div class="scan-card"><div class="scan-card-title">📝 Transcript</div><div style="font-size:0.95rem;color:#e2e8f0;font-style:italic;">"{st.session_state.voice_transcript}"</div></div>', unsafe_allow_html=True)
        with vr:
            st.markdown("""<div class="scan-card"><div class="scan-card-title">🎯 How it Works</div>
                <div style="padding:4px 0;font-size:0.85rem;color:#94a3b8;">1️⃣ Record your voice in any language</div>
                <div style="padding:4px 0;font-size:0.85rem;color:#94a3b8;">2️⃣ AI transcribes using Sarvam Saaras v3</div>
                <div style="padding:4px 0;font-size:0.85rem;color:#94a3b8;">3️⃣ Gemini extracts profile features</div>
                <div style="padding:4px 0;font-size:0.85rem;color:#94a3b8;">4️⃣ Finds your eligible schemes instantly</div>
            </div>""", unsafe_allow_html=True)
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
            st.markdown("""<div class="section-header"><div class="section-icon blue">🔊</div><div><div class="section-title">Text to Speech</div><div class="section-subtitle">Convert any text to natural voice</div></div></div>""", unsafe_allow_html=True)
            tts_text = st.text_area("✍️ Text to read aloud", height=80, placeholder="Paste text...", key="tts_input")
            do_tts(tts_text or "", "voice_tts")

    # ── RESULTS SECTION (shown below tabs if results exist) ──
    if st.session_state.analysis_results:
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        data = st.session_state.analysis_results
        schemes_data = data["matched_schemes"]
        eligible = [s for s in schemes_data if s["eligible"]]
        ineligible = [s for s in schemes_data if not s["eligible"]]

        # Statistics
        c1,c2,c3 = st.columns(3)
        with c1: st.metric("✅ Eligible", f"{len(eligible)} schemes")
        with c2: st.metric("❌ Not Eligible", f"{len(ineligible)} schemes")
        with c3: st.metric("📂 Categories", f"{len(set(s['scheme_category'] for s in eligible))} matched")
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

        # Full-width card view
        st.markdown("""<div class="section-header"><div class="section-icon green">✅</div><div><div class="section-title">Eligible Schemes (AI-Ranked)</div><div class="section-subtitle">Ranked by relevance score • Expand a card to generate a personalized AI guide</div></div></div>""", unsafe_allow_html=True)
        
        if inelastic_schemes := [s for s in schemes_data if not s["eligible"]]:
            st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)
            with st.expander("📁 View schemes you don't qualify for", expanded=False):
                render_scheme_cards(inelastic_schemes, show_category_tag=True)

        all_cats = sorted(set(s["scheme_category"] for s in eligible))
        if all_cats:
            sc1, sc2 = st.columns([1,2])
            with sc1: sel_cat = st.selectbox("Filter by Category", ["All"] + all_cats, key="cat_filter")
            filtered = eligible if sel_cat=="All" else [s for s in eligible if s["scheme_category"]==sel_cat]
            render_scheme_cards(filtered)
        else:
            render_scheme_cards(eligible)





# ══════════════════════════════════════════════════
# PAGE: COMPARE
# ══════════════════════════════════════════════════
elif st.session_state.current_page == "compare":
    st.markdown("""<div class="section-header"><div class="section-icon" style="background:rgba(245,158,11,0.15);">📊</div><div><div class="section-title">Compare Schemes</div><div class="section-subtitle">Side-by-side comparison with AI analysis</div></div></div>""", unsafe_allow_html=True)
    try:
        sr = requests.get(f"{API}/schemes", timeout=5)
        if sr.status_code==200:
            all_scheme_names = []
            for cat,items in sr.json()["categories"].items():
                for s in items: all_scheme_names.append(s["name"])
            all_scheme_names.sort()
            cc1,cc2 = st.columns(2)
            with cc1: sa = st.selectbox("🅰️ Scheme A", all_scheme_names, index=0, key="cmp_a")
            with cc2: sb = st.selectbox("🅱️ Scheme B", all_scheme_names, index=min(1,len(all_scheme_names)-1), key="cmp_b")
            cp1,cp2,cp3 = st.columns(3)
            with cp1: cmp_inc = st.number_input("💰 Your Income", min_value=0, value=150000, step=10000, key="cmp_inc")
            with cp2: cmp_cat = st.selectbox("🏷️ Category", CATEGORIES, key="cmp_cat")
            with cp3: cmp_dist = st.selectbox("📍 District", DISTRICTS, key="cmp_dist")
            if st.button("📊 Compare Now", use_container_width=True, key="cmp_btn"):
                if sa == sb: st.warning("Select two different schemes.")
                else:
                    with st.spinner("🤖 AI is comparing schemes..."):
                        try:
                            # Direct request to avoid silent failures
                            r = requests.post(f"{API}/compare", json={"scheme_a":sa,"scheme_b":sb,"income":cmp_inc,"category":cmp_cat,"district":cmp_dist}, timeout=60)
                            if r.status_code == 200 and r.json().get("success"):
                                st.session_state.compare_result = r.json()
                                st.rerun()
                            else: 
                                st.error(f"Failed: {r.status_code}")
                        except Exception as e: 
                            st.error(f"Connection Error: {e}")
            if st.session_state.compare_result:
                cr = st.session_state.compare_result; a,b = cr["scheme_a"], cr["scheme_b"]
                st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
                ca1,ca2 = st.columns(2)
                with ca1:
                    st.markdown(f"""<div class="scan-card"><div class="scan-card-title">🅰️ {a['name']}</div>
                    <div style="font-size:0.85rem;color:#94a3b8;margin-bottom:1rem;">{a['benefits']}</div>
                    <div class="scan-field found"><div class="scan-field-label">Income Limit</div><div class="scan-field-value">₹{a['income_limit']:,}</div></div>
                    <div class="scan-field found"><div class="scan-field-label">Type</div><div class="scan-field-value">{a.get('type','State')}</div></div>
                    <div class="scan-field found"><div class="scan-field-label">Deadline</div><div class="scan-field-value">{a.get('deadline','N/A')}</div></div>
                    </div>""", unsafe_allow_html=True)
                with ca2:
                    st.markdown(f"""<div class="scan-card"><div class="scan-card-title">🅱️ {b['name']}</div>
                    <div style="font-size:0.85rem;color:#94a3b8;margin-bottom:1rem;">{b['benefits']}</div>
                    <div class="scan-field found"><div class="scan-field-label">Income Limit</div><div class="scan-field-value">₹{b['income_limit']:,}</div></div>
                    <div class="scan-field found"><div class="scan-field-label">Type</div><div class="scan-field-value">{b.get('type','State')}</div></div>
                    <div class="scan-field found"><div class="scan-field-label">Deadline</div><div class="scan-field-value">{b.get('deadline','N/A')}</div></div>
                    </div>""", unsafe_allow_html=True)
                st.markdown("""<div class="section-header"><div class="section-icon purple">🤖</div><div><div class="section-title">AI Comparison Analysis</div><div class="section-subtitle">Personalized pros/cons by Gemini AI</div></div></div>""", unsafe_allow_html=True)
                st.markdown(cr["ai_comparison"])
                st.markdown('<div style="height:1rem;"></div>', unsafe_allow_html=True)
                do_tts(cr["ai_comparison"], "cmp_tts")
    except requests.exceptions.ConnectionError: st.error("❌ Backend not reachable")
    except Exception as e: st.error(f"Error: {e}")


# ══════════════════════════════════════════════════
# PAGE: CHATBOT
# ══════════════════════════════════════════════════
elif st.session_state.current_page == "chatbot":
    st.markdown("""<div class="section-header"><div class="section-icon" style="background:rgba(236,72,153,0.15);">🤖</div><div><div class="section-title">AI Scheme Assistant</div><div class="section-subtitle">Ask anything about government schemes — type or speak</div></div></div>""", unsafe_allow_html=True)

    st.markdown("""<div style="padding:0.8rem 1rem;background:rgba(236,72,153,0.06);border:1px solid rgba(236,72,153,0.15);border-radius:14px;margin-bottom:1rem;font-size:0.78rem;color:#94a3b8;line-height:1.7;">
    💡 <b style="color:#f9a8d4;">Try:</b> "How to apply for PM Kisan?" • "I earn ₹1L, what schemes?" • "Compare PMAY vs Life Mission" • "എനിക്ക് ലഭ്യമായ സ്കീമുകൾ?"
    </div>""", unsafe_allow_html=True)

    with st.expander("📋 Set your profile (optional)", expanded=False):
        ch1,ch2,ch3 = st.columns(3)
        with ch1: chat_income = st.number_input("Income", min_value=0, value=0, step=10000, key="chat_inc")
        with ch2: chat_cat = st.selectbox("Category", [""]+CATEGORIES, key="chat_cat")
        with ch3: chat_dist = st.selectbox("District", [""]+DISTRICTS, key="chat_dist")

    with st.expander("🎙️ Speak your question", expanded=False):
        chat_stt_lang = st.selectbox("Language", list(LANGS.keys()), index=0, key="chat_stt_lang")
        chat_audio = st.audio_input("🎙️ Record", key="chat_voice")
        if chat_audio and st.button("📝 Send Voice Question", key="chat_voice_send", use_container_width=True):
            with st.spinner("🎙️ Transcribing & asking AI..."):
                try:
                    r = requests.post(f"{API}/voice/stt", files={"file":("audio.wav",chat_audio.getvalue(),"audio/wav")}, data={"language":LANGS[chat_stt_lang]}, timeout=30)
                    if r.status_code==200 and r.json().get("success"):
                        voice_q = r.json()["transcript"]
                        st.session_state.chat_history.append({"role":"user","content":f"🎙️ {voice_q}"})
                        payload = {"message":voice_q, "history":st.session_state.chat_history[:-1]}
                        if chat_income>0: payload["income"] = chat_income
                        if chat_cat: payload["category"] = chat_cat
                        if chat_dist: payload["district"] = chat_dist
                        r2 = requests.post(f"{API}/chat", json=payload, timeout=60)
                        if r2.status_code==200:
                            st.session_state.chat_history.append({"role":"ai","content":r2.json().get("response","Sorry, couldn't process.")})
                        st.rerun()
                except Exception as e: st.error(f"Error: {e}")

    for idx, msg in enumerate(st.session_state.chat_history):
        cls = "chat-user" if msg["role"]=="user" else "chat-ai"
        icon = "👤" if msg["role"]=="user" else "🤖"
        st.markdown(f'<div class="chat-msg {cls}"><b>{icon}</b> {msg["content"].replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)
        if msg["role"] == "ai":
            if st.button(f"🔊 Listen", key=f"chat_tts_{idx}"):
                with st.spinner("🔊 Generating voice..."):
                    try:
                        clean = msg["content"].replace("**","").replace("*","").replace("#","")[:2500]
                        r = requests.post(f"{API}/voice/tts", json={"text":clean,"language":"ml-IN","speaker":"anila"}, timeout=30)
                        if r.status_code==200 and r.json().get("success"):
                            st.audio(base64.b64decode(r.json()["audio_base64"]), format="audio/wav")
                    except: pass

    chat_msg = st.chat_input("Ask about any scheme...")
    if chat_msg:
        st.session_state.chat_history.append({"role":"user","content":chat_msg})
        with st.spinner("🤖 Thinking..."):
            try:
                payload = {"message":chat_msg, "history":st.session_state.chat_history[:-1]}
                if chat_income>0: payload["income"] = chat_income
                if chat_cat: payload["category"] = chat_cat
                if chat_dist: payload["district"] = chat_dist
                r = requests.post(f"{API}/chat", json=payload, timeout=60)
                if r.status_code==200:
                    st.session_state.chat_history.append({"role":"ai","content":r.json().get("response","Sorry, something went wrong.")})
                else:
                    st.session_state.chat_history.append({"role":"ai","content":"Sorry, something went wrong."})
            except Exception as e:
                st.session_state.chat_history.append({"role":"ai","content":f"Connection error: {e}"})
        st.rerun()

    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat", key="clear_chat"):
            st.session_state.chat_history = []; st.rerun()


# ══════════════════════════════════════════════════
# PAGE: NOTIFICATIONS
# ══════════════════════════════════════════════════
elif st.session_state.current_page == "notifications":
    st.markdown("""<div class="section-header"><div class="section-icon" style="background:rgba(245,158,11,0.15);">🔔</div><div><div class="section-title">Notifications</div><div class="section-subtitle">Upcoming deadlines & recently added schemes</div></div></div>""", unsafe_allow_html=True)

    try:
        nr = requests.get(f"{API}/notifications", timeout=5)
        if nr.status_code==200:
            notifs = nr.json().get("notifications",[])
            if notifs:
                deadlines = [n for n in notifs if n["type"]=="deadline"]
                new_schemes = [n for n in notifs if n["type"]=="new_scheme"]

                mc1,mc2 = st.columns(2)
                with mc1: st.metric("⏰ Upcoming Deadlines", f"{len(deadlines)}")
                with mc2: st.metric("🆕 New Schemes", f"{len(new_schemes)}")
                st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

                if deadlines:
                    st.markdown("""<div class="section-header"><div class="section-icon" style="background:rgba(239,68,68,0.15);">⏰</div><div><div class="section-title">Deadline Alerts</div><div class="section-subtitle">Apply before these dates</div></div></div>""", unsafe_allow_html=True)
                    for n in deadlines:
                        uc = "notif-high" if n.get("urgency")=="high" else "notif-medium" if n.get("urgency")=="medium" else "notif-low"
                        cat_icon = CAT_ICONS.get(n.get("scheme_category","General"), "📋")
                        st.markdown(f'<div class="notif-card {uc}">{cat_icon} {n["message"]}  <span style="font-size:0.7rem;opacity:0.7;">({n.get("scheme_category","General")})</span></div>', unsafe_allow_html=True)

                if new_schemes:
                    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
                    st.markdown("""<div class="section-header"><div class="section-icon" style="background:rgba(34,197,94,0.15);">🆕</div><div><div class="section-title">Recently Added Schemes</div><div class="section-subtitle">New opportunities in the last 30 days</div></div></div>""", unsafe_allow_html=True)
                    for n in new_schemes:
                        cat_icon = CAT_ICONS.get(n.get("scheme_category","General"), "📋")
                        st.markdown(f'<div class="notif-card notif-low">{cat_icon} {n["message"]}  <span style="font-size:0.7rem;opacity:0.7;">({n.get("scheme_category","General")})</span></div>', unsafe_allow_html=True)
            else:
                st.markdown("""<div style="text-align:center;padding:4rem 2rem;"><div style="font-size:3.5rem;margin-bottom:1rem;">✅</div><div style="font-size:1.2rem;font-weight:700;color:#e2e8f0;">All caught up!</div><div style="font-size:0.85rem;color:#64748b;margin-top:0.4rem;">No upcoming deadlines or new schemes right now.</div></div>""", unsafe_allow_html=True)
        else:
            st.error("Could not load notifications")
    except requests.exceptions.ConnectionError:
        st.error("❌ Backend not reachable")
    except Exception as e:
        st.error(f"Error: {e}")


# ══════════════════════════════════════════════════
# PAGE: SETTINGS
# ══════════════════════════════════════════════════
elif st.session_state.current_page == "settings":
    st.markdown("""<div class="section-header"><div class="section-icon" style="background:rgba(139,92,246,0.15);">⚙️</div><div><div class="section-title">Settings</div><div class="section-subtitle">Configure your preferences</div></div></div>""", unsafe_allow_html=True)

    st.markdown("""<div class="scan-card"><div class="scan-card-title">👤 Account</div>""", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="scan-field found"><div class="scan-field-label">Username</div><div class="scan-field-value">{st.session_state.username}</div></div>
    <div class="scan-field found"><div class="scan-field-label">Account Type</div><div class="scan-field-value">{'Guest' if st.session_state.username=='Guest' else 'Registered'}</div></div>
    </div>""", unsafe_allow_html=True)

    if st.session_state.username != "Guest" and st.session_state.profile:
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        st.markdown("""<div class="scan-card"><div class="scan-card-title">📋 Saved Profile Info</div>""", unsafe_allow_html=True)
        prof = st.session_state.profile
        cols = st.columns(2)
        with cols[0]:
            st.markdown(f"**Email:** {prof.get('email','N/A')}")
            st.markdown(f"**Phone:** {prof.get('phone','N/A')}")
            st.markdown(f"**Income:** ₹{prof.get('income',0):,}")
            st.markdown(f"**District:** {prof.get('district','N/A')}")
        with cols[1]:
            st.markdown(f"**Category:** {prof.get('category','N/A')}")
            st.markdown(f"**Age:** {prof.get('age','N/A')}")
            st.markdown(f"**Occupation:** {prof.get('occupation','N/A')}")
            st.markdown(f"**Education:** {prof.get('education','N/A')}")
        if st.button("🗑️ Delete Stored Data", use_container_width=True, key="del_data_btn"):
            with st.spinner("Deleting stored data..."):
                try:
                    r = requests.delete(f"{API}/profile/delete/{st.session_state.username}", timeout=30)
                    if r.status_code==200:
                        st.session_state.profile = {}
                        st.success("✅ All personal data deleted from our servers.")
                        st.rerun()
                    else: st.error("Failed to delete stored data")
                except Exception as e: st.error(f"Error: {e}")
        st.markdown('<div style="font-size:0.7rem;color:#64748b;margin-top:10px;">This data is used to filter schemes and send you personalized alerts.</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    st.markdown("""<div class="scan-card"><div class="scan-card-title">🌐 Language & Voice</div>""", unsafe_allow_html=True)
    pref_lang = st.selectbox("Preferred Language", list(LANGS.keys()), index=0, key="pref_lang")
    pref_speaker = st.selectbox("Preferred Voice", list(SPEAKERS.keys()), index=0, key="pref_speaker")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    st.markdown("""<div class="scan-card"><div class="scan-card-title">ℹ️ About</div>""", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.82rem;color:#94a3b8;line-height:1.8;">
    <b style="color:#7de8d4;">K-AI Scheme Mitra</b> — AI-powered Kerala Government Scheme Navigator<br>
    📡 Powered by <b>Google Gemini 2.0 Flash</b> + <b>Sarvam AI</b><br>
    🏛️ Aligned with <b>Kerala IT Policy 2026</b><br>
    🔒 Privacy First — No user data is stored permanently<br>
    📊 Database: 45 schemes across 9 categories<br>
    🌐 Supports: Malayalam, English, Hindi, Tamil, Telugu, Kannada
    </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ── FOOTER ──
st.markdown("""<div class="footer"><div class="custom-divider"></div>
🔒 Data Privacy: Encrypted storage used for personalized alerts | Powered by <a href="#">Gemini 2.0 Flash</a> + <a href="#">Sarvam AI</a> | <a href="#">Kerala IT Policy 2026</a>
</div>""", unsafe_allow_html=True)
