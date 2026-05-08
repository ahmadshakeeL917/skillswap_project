import streamlit as st
from pathlib import Path
import json, uuid, datetime, random
from typing import List, Dict, Any
import time
import csv
from io import StringIO

# ---------------- Config ----------------
DATA_FILE = Path("data.json")
st.set_page_config(
    page_title="SkillSwap", 
    page_icon="SS", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- Session State Init ----------------
if "theme" not in st.session_state:
    st.session_state.theme = "dark"
if "notifications" not in st.session_state:
    st.session_state.notifications = []
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "show_confetti" not in st.session_state:
    st.session_state.show_confetti = False

# ---------------- Data Management ----------------
def read_data() -> Dict[str, Any]:
    if not DATA_FILE.exists():
        default = {
            "users": [], 
            "requests": [], 
            "messages": [],
            "endorsements": [],
            "achievements": []
        }
        write_data(default)
        return default
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except Exception:
        default = {
            "users": [], 
            "requests": [], 
            "messages": [],
            "endorsements": [],
            "achievements": []
        }
        write_data(default)
        return default

def write_data(data: Dict[str, Any]):
    DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

def make_user(name: str, email: str, bio: str, offered: List[str], wanted: List[str], 
              proficiency: Dict[str, str], location: str = "", interests: List[str] = []) -> Dict[str, Any]:
    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "email": email,
        "bio": bio,
        "location": location,
        "interests": interests,
        "skills_offered": [s.strip().lower() for s in offered if s.strip()],
        "skills_wanted": [s.strip().lower() for s in wanted if s.strip()],
        "proficiency": proficiency,
        "rating": 5.0,
        "swaps_completed": 0,
        "endorsements_received": 0,
        "badges": [],
        "level": 1,
        "experience_points": 0,
        "availability": "Available",
        "response_rate": 100,
        "created_at": datetime.datetime.utcnow().isoformat(),
        "last_active": datetime.datetime.utcnow().isoformat()
    }

def make_request(sender_id: str, receiver_id: str, skill_offered: str, skill_wanted: str, 
                message: str = "", priority: str = "Medium") -> Dict[str, Any]:
    return {
        "id": str(uuid.uuid4()),
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "skill_offered": skill_offered,
        "skill_wanted": skill_wanted,
        "message": message,
        "priority": priority,
        "status": "Pending",
        "created_at": datetime.datetime.utcnow().isoformat(),
        "updated_at": datetime.datetime.utcnow().isoformat(),
        "viewed": False
    }

def add_achievement(user_id: str, achievement_type: str, data: Dict):
    achievements = data.get("achievements", [])
    achievements.append({
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "type": achievement_type,
        "timestamp": datetime.datetime.utcnow().isoformat()
    })
    data["achievements"] = achievements
    
    user = next((u for u in data["users"] if u["id"] == user_id), None)
    if user:
        badges = user.get("badges", [])
        if achievement_type == "first_swap" and "First Swap" not in badges:
            badges.append("First Swap")
        elif achievement_type == "5_swaps" and "Active Learner" not in badges:
            badges.append("Active Learner")
        elif achievement_type == "10_swaps" and "Expert Swapper" not in badges:
            badges.append("Expert Swapper")
        user["badges"] = badges

# ---------------- Enhanced Algorithm ----------------
def compatibility_score(a: Dict[str, Any], b: Dict[str, Any]) -> tuple[float, Dict[str, Any]]:
    offers_a = set(a["skills_offered"])
    wants_a = set(a["skills_wanted"])
    offers_b = set(b["skills_offered"])
    wants_b = set(b["skills_wanted"])
    
    a_to_b = offers_a.intersection(wants_b)
    b_to_a = offers_b.intersection(wants_a)
    
    reciprocity = 0
    if wants_b and a_to_b:
        reciprocity += (len(a_to_b) / len(wants_b)) * 40
    if wants_a and b_to_a:
        reciprocity += (len(b_to_a) / len(wants_a)) * 40
    
    proficiency = 0
    prof_a = a.get("proficiency", {})
    for skill in a_to_b:
        if skill in prof_a:
            if prof_a[skill] == "Expert":
                proficiency += 6
            elif prof_a[skill] == "Intermediate":
                proficiency += 3
    
    engagement = min(a.get("swaps_completed", 0) + b.get("swaps_completed", 0), 10)
    rating = ((a.get("rating", 0) + b.get("rating", 0)) / 2) * 0.5
    response = ((a.get("response_rate", 100) + b.get("response_rate", 100)) / 2) * 0.1
    
    location_bonus = 5 if a.get("location", "") == b.get("location", "") and a.get("location") else 0
    
    interests_a = set(a.get("interests", []))
    interests_b = set(b.get("interests", []))
    interest_overlap = len(interests_a.intersection(interests_b)) * 2
    
    total = min(reciprocity + proficiency + engagement + rating + response + location_bonus + interest_overlap, 100)
    
    details = {
        "reciprocity": round(reciprocity, 1),
        "proficiency": round(proficiency, 1),
        "engagement": round(engagement, 1),
        "rating": round(rating, 1),
        "response_rate": round(response, 1),
        "location_match": location_bonus > 0,
        "mutual_skills": list(a_to_b.union(b_to_a)),
        "common_interests": list(interests_a.intersection(interests_b))
    }
    
    return round(total, 1), details

# ---------------- ENHANCED CSS with Scrollable Quick Actions ----------------
ENHANCED_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;700&display=swap');

:root {
    --primary: #00d9ff;
    --primary-glow: rgba(0, 217, 255, 0.5);
    --secondary: #7c3aed;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
    --dark-bg: #0a0e27;
    --card-bg: rgba(255, 255, 255, 0.03);
    --border: rgba(255, 255, 255, 0.08);
    --transition-smooth: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

* {
    transition: var(--transition-smooth);
}

html {
    scroll-behavior: smooth;
}

[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 25%, #0f1729 50%, #1e2139 75%, #0a0e27 100%);
    background-size: 400% 400%;
    animation: gradientShift 15s ease infinite;
    color: #ffffff;
    font-family: 'Inter', sans-serif;
}

@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* ENHANCED SIDEBAR with Better Scrolling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(10, 14, 39, 0.98) 0%, rgba(15, 23, 41, 0.98) 100%);
    backdrop-filter: blur(25px) saturate(180%);
    border-right: 1px solid var(--border);
    box-shadow: 4px 0 50px rgba(0, 0, 0, 0.6);
}

[data-testid="stSidebar"]::-webkit-scrollbar {
    width: 8px;
}

[data-testid="stSidebar"]::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.02);
    border-radius: 10px;
}

[data-testid="stSidebar"]::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, var(--primary), var(--secondary));
    border-radius: 10px;
    box-shadow: 0 0 10px var(--primary-glow);
}

/* Quick Actions Container - FIXED SCROLLING */
.quick-actions-container {
    max-height: 400px;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 12px;
    margin: 16px 0;
    background: rgba(255, 255, 255, 0.02);
    border-radius: 16px;
    border: 1px solid var(--border);
}

.quick-actions-container::-webkit-scrollbar {
    width: 6px;
}

.quick-actions-container::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 10px;
}

.quick-actions-container::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, var(--primary), var(--secondary));
    border-radius: 10px;
}

.quick-actions-container::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, var(--secondary), var(--primary));
}

/* Quick Action Button */
.quick-action-btn {
    width: 100%;
    padding: 12px 16px;
    margin: 8px 0;
    background: linear-gradient(135deg, rgba(0, 217, 255, 0.15), rgba(124, 58, 237, 0.15));
    border: 1px solid var(--border);
    border-radius: 12px;
    color: white;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    text-align: left;
    display: flex;
    align-items: center;
    gap: 12px;
}

.quick-action-btn:hover {
    transform: translateX(4px);
    background: linear-gradient(135deg, rgba(0, 217, 255, 0.25), rgba(124, 58, 237, 0.25));
    border-color: var(--primary);
    box-shadow: 0 8px 24px rgba(0, 217, 255, 0.3);
}

.ultra-header {
    position: relative;
    background: rgba(255, 255, 255, 0.02);
    border-radius: 28px;
    padding: 50px;
    margin-bottom: 40px;
    backdrop-filter: blur(25px) saturate(180%);
    overflow: hidden;
    box-shadow: 0 12px 48px rgba(0, 0, 0, 0.5),
                inset 0 1px 0 rgba(255, 255, 255, 0.15);
}

.ultra-header::before {
    content: '';
    position: absolute;
    top: -3px;
    left: -3px;
    right: -3px;
    bottom: -3px;
    background: linear-gradient(45deg, var(--primary), var(--secondary), var(--success), var(--warning), var(--primary));
    background-size: 400% 400%;
    border-radius: 28px;
    z-index: -1;
    animation: borderGlowFlow 8s ease infinite;
    filter: blur(12px);
    opacity: 0.9;
}

@keyframes borderGlowFlow {
    0%, 100% { background-position: 0% 50%; }
    25% { background-position: 50% 100%; }
    50% { background-position: 100% 50%; }
    75% { background-position: 50% 0%; }
}

.title-ultra {
    font-size: 52px;
    font-weight: 900;
    background: linear-gradient(135deg, #00d9ff 0%, #7c3aed 50%, #10b981 100%);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: textShimmerFlow 4s ease-in-out infinite;
    letter-spacing: -2px;
    margin: 0;
    filter: drop-shadow(0 0 50px rgba(0, 217, 255, 0.6));
}

@keyframes textShimmerFlow {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}

.subtitle-ultra {
    color: rgba(255, 255, 255, 0.75);
    font-size: 19px;
    margin-top: 16px;
    font-weight: 400;
    letter-spacing: 0.5px;
}

.glass-card {
    position: relative;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.06), rgba(255, 255, 255, 0.02));
    border: 1px solid var(--border);
    border-radius: 24px;
    padding: 32px;
    margin-bottom: 28px;
    backdrop-filter: blur(25px) saturate(180%);
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4),
                inset 0 1px 0 rgba(255, 255, 255, 0.15);
    cursor: pointer;
    overflow: hidden;
}

.glass-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: -150%;
    width: 100%height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.15), transparent);
    transition: left 0.7s cubic-bezier(0.4, 0, 0.2, 1);
}

.glass-card:hover::before {
    left: 150%;
}

.glass-card:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 20px 60px rgba(0, 217, 255, 0.25),
                inset 0 1px 0 rgba(255, 255, 255, 0.25);
    border-color: rgba(0, 217, 255, 0.5);
}

.stat-card {
    background: linear-gradient(135deg, rgba(0, 217, 255, 0.12), rgba(124, 58, 237, 0.12));
    border: 1px solid var(--border);
    border-radius: 24px;
    padding: 32px;
    text-align: center;
    backdrop-filter: blur(25px);
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
}

.stat-card:hover {
    transform: translateY(-8px) scale(1.05);
    box-shadow: 0 24px 60px rgba(0, 217, 255, 0.35);
    border-color: rgba(0, 217, 255, 0.6);
}

.stat-number {
    font-size: 50px;
    font-weight: 900;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 0 30px rgba(0, 217, 255, 0.6));
}

.stat-label {
    color: rgba(255, 255, 255, 0.75);
    font-size: 14px;
    text-transform: uppercase;
    letter-spacing: 2.5px;
    margin-top: 16px;
    font-weight: 600;
}

.skill-badge {
    display: inline-block;
    background: linear-gradient(135deg, rgba(0, 217, 255, 0.25), rgba(0, 217, 255, 0.08));
    color: var(--primary);
    padding: 12px 22px;
    border-radius: 999px;
    margin: 6px;
    font-weight: 700;
    font-size: 14px;
    border: 1px solid rgba(0, 217, 255, 0.5);
    text-transform: uppercase;
    letter-spacing: 1px;
    box-shadow: 0 5px 20px rgba(0, 217, 255, 0.3);
}

.skill-badge:hover {
    transform: translateY(-4px) scale(1.08);
    box-shadow: 0 12px 32px rgba(0, 217, 255, 0.5);
}

.skill-want {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.25), rgba(16, 185, 129, 0.08));
    color: var(--success);
    border-color: rgba(16, 185, 129, 0.5);
    box-shadow: 0 5px 20px rgba(16, 185, 129, 0.3);
}

.proficiency {
    display: inline-block;
    padding: 7px 14px;
    border-radius: 10px;
    font-size: 12px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-left: 10px;
    box-shadow: 0 3px 12px rgba(0, 0, 0, 0.4);
}

.prof-expert {
    background: linear-gradient(135deg, #10b981, #059669);
    color: white;
}

.prof-intermediate {
    background: linear-gradient(135deg, #f59e0b, #d97706);
    color: white;
}

.prof-beginner {
    background: linear-gradient(135deg, #3b82f6, #2563eb);
    color: white;
}

.avatar-ultra {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 900;
    font-size: 36px;
    color: white;
    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
    box-shadow: 0 15px 40px rgba(0, 217, 255, 0.5);
}

.stButton > button {
    background: linear-gradient(135deg, var(--primary), var(--secondary)) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 16px !important;
    padding: 16px 36px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
    box-shadow: 0 8px 24px rgba(0, 217, 255, 0.5) !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    transform: translateY(-4px) scale(1.03) !important;
    box-shadow: 0 16px 40px rgba(0, 217, 255, 0.7) !important;
}

.muted {
    color: rgba(255, 255, 255, 0.55);
    font-size: 15px;
}

.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 10px 20px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    box-shadow: 0 5px 16px rgba(0, 0, 0, 0.4);
}

.status-pending {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.35), rgba(245, 158, 11, 0.15));
    color: #f59e0b;
    border: 1px solid rgba(245, 158, 11, 0.5);
}

.status-accepted {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.35), rgba(16, 185, 129, 0.15));
    color: #10b981;
    border: 1px solid rgba(16, 185, 129, 0.5);
}

.status-completed {
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.35), rgba(59, 130, 246, 0.15));
    color: #3b82f6;
    border: 1px solid rgba(59, 130, 246, 0.5);
}

.status-rejected {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.35), rgba(239, 68, 68, 0.15));
    color: #ef4444;
    border: 1px solid rgba(239, 68, 68, 0.5);
}

.compat-container {
    text-align: center;
    padding: 24px;
    background: rgba(255, 255, 255, 0.04);
    border-radius: 20px;
    backdrop-filter: blur(15px);
}

.compat-score {
    font-size: 48px;
    font-weight: 900;
    background: linear-gradient(135deg, var(--primary), var(--success));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 0 30px rgba(0, 217, 255, 0.6));
}

.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 32px;
    padding: 24px;
    background: linear-gradient(135deg, rgba(0, 217, 255, 0.15), rgba(124, 58, 237, 0.15));
    border-radius: 20px;
    border: 1px solid rgba(0, 217, 255, 0.4);
}

.brand-icon {
    width: 58px;
    height: 58px;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    box-shadow: 0 10px 30px rgba(0, 217, 255, 0.5);
}

.brand-text {
    font-weight: 900;
    font-size: 24px;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
}

.level-container {
    background: rgba(255, 255, 255, 0.06);
    border-radius: 999px;
    padding: 5px;
    margin: 20px 0;
}

.level-bar {
    height: 10px;
    background: linear-gradient(90deg, var(--primary), var(--success));
    border-radius: 999px;
    box-shadow: 0 0 25px rgba(0, 217, 255, 0.6);
}

.progress-bar {
    background: rgba(255, 255, 255, 0.06);
    border-radius: 999px;
    height: 14px;
    overflow: hidden;
    margin-top: 20px;
    box-shadow: inset 0 3px 6px rgba(0, 0, 0, 0.4);
}

.progress-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, var(--primary), var(--secondary), var(--success));
    background-size: 300% 100%;
    box-shadow: 0 0 30px rgba(0, 217, 255, 0.7);
    animation: progressWave 3s linear infinite;
}

@keyframes progressWave {
    0% { background-position: 0% 50%; }
    100% { background-position: 300% 50%; }
}

.badge-item {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    background: linear-gradient(135deg, rgba(124, 58, 237, 0.25), rgba(124, 58, 237, 0.08));
    padding: 12px 20px;
    border-radius: 999px;
    border: 1px solid rgba(124, 58, 237, 0.5);
    margin: 6px;
    font-weight: 600;
    font-size: 14px;
    color: #a78bfa;
    box-shadow: 0 5px 20px rgba(124, 58, 237, 0.4);
}

.badge-item:hover {
    transform: translateY(-4px) scale(1.08);
    box-shadow: 0 12px 32px rgba(124, 58, 237, 0.6);
}

input, textarea, select {
    background: rgba(255, 255, 255, 0.06) !important;
    color: #ffffff !important;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    padding: 18px !important;
    font-size: 16px !important;
    backdrop-filter: blur(15px) !important;
    box-shadow: inset 0 3px 6px rgba(0, 0, 0, 0.3) !important;
    transition: all 0.4s ease !important;
}

input:focus, textarea:focus, select:focus {
    background: rgba(255, 255, 255, 0.1) !important;
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 5px rgba(0, 217, 255, 0.2),
                inset 0 3px 6px rgba(0, 0, 0, 0.3) !important;
    transform: translateY(-2px) !important;
}

::-webkit-scrollbar {
    width: 12px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.02);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    border-radius: 10px;
    box-shadow: 0 0 15px var(--primary-glow);
}

@media (max-width: 768px) {
    .ultra-header { padding: 28px; }
    .title-ultra { font-size: 40px; }
    .glass-card { padding: 24px; }
}
</style>
"""

st.markdown(ENHANCED_CSS, unsafe_allow_html=True)

# ---------------- Helper Functions ----------------
def initials(name: str) -> str:
    parts = [p for p in name.split() if p]
    return (parts[0][0] + (parts[1][0] if len(parts) > 1 else "")).upper()

def avatar_html(name: str) -> str:
    return f"<div class='avatar-ultra'>{initials(name)}</div>"

def skill_badge_html(skill: str, proficiency: str = "", want: bool = False) -> str:
    badge_class = "skill-want" if want else "skill-badge"
    prof_html = ""
    if proficiency and not want:
        prof_class = f"prof-{proficiency.lower()}"
        prof_html = f"<span class='proficiency {prof_class}'>{proficiency}</span>"
    return f"<span class='{badge_class}'>{skill}{prof_html}</span>"

def status_badge_html(status: str) -> str:
    icons = {
        "Pending": "",
        "Accepted": "",
        "Completed": "",
        "Rejected": ""
    }
    icon = icons.get(status, "")
    return f"<span class='status-badge status-{status.lower()}'>{icon} {status}</span>"

def level_progress_html(user: Dict) -> str:
    xp = user.get("experience_points", 0)
    level = user.get("level", 1)
    next_level_xp = level * 100
    progress = (xp % next_level_xp) / next_level_xp * 100
    
    return f"""
    <div style='margin:16px 0'>
        <div style='display:flex;justify-content:space-between;margin-bottom:8px'>
            <span style='font-weight:700;color:var(--primary)'>Level {level}</span>
            <span class='muted'>{xp % next_level_xp}/{next_level_xp} XP</span>
        </div>
        <div class='level-container'>
            <div class='level-bar' style='width:{progress}%'></div>
        </div>
    </div>
    """

def compat_display_html(score: float, details: Dict[str, Any]) -> str:
    return f"""
    <div class='compat-container'>
        <div class='compat-score'>{score}</div>
        <div class='muted' style='margin-top:12px;font-size:11px'>
            Match Score<br>
            Reciprocity: {details['reciprocity']}%<br>
            Proficiency: {details['proficiency']}%
        </div>
        <div class='progress-bar'>
            <div class='progress-fill' style='width:{score}%'></div>
        </div>
    </div>
    """

def export_users_csv(users: List[Dict]) -> str:
    output = StringIO()
    if users:
        keys = ["name", "email", "location", "rating", "swaps_completed", "level", "experience_points"]
        writer = csv.DictWriter(output, fieldnames=keys, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(users)
    return output.getvalue()

def export_requests_csv(requests: List[Dict], users: List[Dict]) -> str:
    output = StringIO()
    if requests:
        rows = []
        for req in requests:
            sender = next((u for u in users if u["id"] == req["sender_id"]), {})
            receiver = next((u for u in users if u["id"] == req["receiver_id"]), {})
            rows.append({
                "sender": sender.get("name", "Unknown"),
                "receiver": receiver.get("name", "Unknown"),
                "skill_offered": req.get("skill_offered", ""),
                "skill_wanted": req.get("skill_wanted", ""),
                "status": req.get("status", ""),
                "priority": req.get("priority", ""),
                "created_at": req.get("created_at", "")
            })
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return output.getvalue()

# ---------------- Load Data ----------------
data = read_data()
users = data.get("users", [])
requests = data.get("requests", [])

# ---------------- Sidebar with SCROLLABLE Quick Actions ----------------
with st.sidebar:
    st.markdown("""
        <div class='sidebar-brand'>
            <div class='brand-icon'>SS</div>
            <div class='brand-text'>SkillSwap</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='text-align:center;color:rgba(255,255,255,0.6);font-size:12px;margin-bottom:20px'>Built by CSE Engineering Student</div>", unsafe_allow_html=True)
    
    if users:
        st.markdown("### Active Profile")
        selected_user = st.selectbox(
            "Select Profile",
            ["None"] + [u["name"] for u in users],
            label_visibility="collapsed"
        )
        if selected_user != "None":
            user = next(u for u in users if u["name"] == selected_user)
            st.session_state.current_user = user
            
            st.markdown(level_progress_html(user), unsafe_allow_html=True)
            
            if user.get("badges"):
                st.markdown("**Badges**")
                badges_html = " ".join([f"<span class='badge-item'>{b}</span>" for b in user["badges"]])
                st.markdown(badges_html, unsafe_allow_html=True)
    
    st.markdown("---")
    
    mode = st.radio(
        "Navigation",
        ["Dashboard", "Create Profile", "My Profile", "Discover", 
         "Requests", "Analytics", "Leaderboard"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### Quick Actions")
    
    # SCROLLABLE CONTAINER FOR QUICK ACTIONS
    st.markdown("<div class='quick-actions-container'>", unsafe_allow_html=True)
    
    # Demo Data
    if st.button("Load Demo Data", use_container_width=True, key="demo"):
        demo_users = [
            {
                "name": "Aman Verma", "email": "aman@skillswap.com",
                "bio": "Full-stack dev | Python & React enthusiast",
                "location": "Mumbai", "interests": ["web dev", "AI", "gaming"],
                "skills_offered": ["python", "django", "postgresql", "docker"],
                "skills_wanted": ["react", "typescript", "aws"],
                "proficiency": {"python": "Expert", "django": "Expert", "postgresql": "Intermediate", "docker": "Intermediate"},
                "swaps_completed": 8, "rating": 4.9, "level": 3, "experience_points": 250
            },
            {
                "name": "Riya Kapoor", "email": "riya@skillswap.com",
                "bio": "Frontend wizard | React & Figma",
                "location": "Bangalore", "interests": ["design", "frontend", "UX"],
                "skills_offered": ["react", "typescript", "figma", "css", "tailwind"],
                "skills_wanted": ["python", "django", "postgresql"],
                "proficiency": {"react": "Expert", "typescript": "Expert", "figma": "Intermediate"},
                "swaps_completed": 6, "rating": 4.7, "level": 2, "experience_points": 180
            },
            {
                "name": "Sameer Desai", "email": "sameer@skillswap.com",
                "bio": "Data scientist | ML & Analytics",
                "location": "Pune", "interests": ["data science", "ML", "analytics"],
                "skills_offered": ["pandas", "numpy", "matplotlib", "scikit-learn", "sql"],
                "skills_wanted": ["docker", "kubernetes", "aws", "react"],
                "proficiency": {"pandas": "Expert", "matplotlib": "Expert", "scikit-learn": "Intermediate"},
                "swaps_completed": 12, "rating": 5.0, "level": 4, "experience_points": 380
            },
            {
                "name": "Priya Sharma", "email": "priya@skillswap.com",
                "bio": "DevOps Engineer | Cloud & Containers",
                "location": "Delhi", "interests": ["cloud", "devops", "automation"],
                "skills_offered": ["aws", "docker", "kubernetes", "terraform"],
                "skills_wanted": ["python", "golang", "rust"],
                "proficiency": {"aws": "Expert", "docker": "Expert", "kubernetes": "Intermediate"},
                "swaps_completed": 5, "rating": 4.6, "level": 2, "experience_points": 150
            }
        ]
        
        added = 0
        for d in demo_users:
            if not any(u["name"] == d["name"] for u in users):
                new_user = {
                    "id": str(uuid.uuid4()),
                    **d,
                    "endorsements_received": random.randint(5, 20),
                    "badges": random.sample(["First Swap", "Active Learner", "Expert Swapper"], k=random.randint(1, 3)),
                    "availability": random.choice(["Available", "Busy", "Away"]),
                    "response_rate": random.randint(85, 100),
                    "created_at": datetime.datetime.utcnow().isoformat(),
                    "last_active": datetime.datetime.utcnow().isoformat()
                }
                users.append(new_user)
                added += 1
        
        data["users"] = users
        write_data(data)
        st.success(f"Added {added} demo profiles!")
        time.sleep(1)
        st.rerun()
    
    # Export Users CSV
    if st.button("Export Users CSV", use_container_width=True, key="export_users"):
        if users:
            csv_data = export_users_csv(users)
            st.download_button(
                "Download Users.csv",
                csv_data,
                file_name=f"users_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.warning("No users to export")
    
    # Export Requests CSV
    if st.button("Export Requests CSV", use_container_width=True, key="export_requests"):
        if requests:
            csv_data = export_requests_csv(requests, users)
            st.download_button(
                "Download Requests.csv",
                csv_data,
                file_name=f"requests_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.warning("No requests to export")
    
    # Generate Platform Report
    if st.button("Generate Report", use_container_width=True, key="report"):
        report = f"""
SkillSwap Platform Report
Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
===========================================

Platform Statistics:
- Total Users: {len(users)}
- Total Skills Offered: {sum(len(u.get('skills_offered', [])) for u in users)}
- Total Requests: {len(requests)}
- Pending Requests: {len([r for r in requests if r['status'] == 'Pending'])}
- Completed Swaps: {len([r for r in requests if r['status'] == 'Completed'])}
- Average Rating: {sum(u.get('rating', 0) for u in users) / len(users) if users else 0:.2f}

Top Skills:
{chr(10).join([f'- {skill}' for skill in sorted(set(s for u in users for s in u.get('skills_offered', [])))[:10]])}

Top Users (by swaps):
{chr(10).join([f'- {u["name"]}: {u.get("swaps_completed", 0)} swaps' for u in sorted(users, key=lambda x: x.get('swaps_completed', 0), reverse=True)[:5]])}
        """
        st.download_button(
            "Download Report.txt",
            report,
            file_name=f"report_{datetime.datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    # Batch Accept Requests
    if st.button("Accept All Pending", use_container_width=True, key="accept_all"):
        count = 0
        for req in requests:
            if req["status"] == "Pending":
                req["status"] = "Accepted"
                req["updated_at"] = datetime.datetime.utcnow().isoformat()
                count += 1
        if count > 0:
            data["requests"] = requests
            write_data(data)
            st.success(f"Accepted {count} requests!")
            time.sleep(1)
            st.rerun()
        else:
            st.info("No pending requests")
    
    # Batch Complete Requests
    if st.button("Complete All Accepted", use_container_width=True, key="complete_all"):
        count = 0
        for req in requests:
            if req["status"] == "Accepted":
                req["status"] = "Completed"
                req["updated_at"] = datetime.datetime.utcnow().isoformat()
                # Award XP
                sender = next((u for u in users if u["id"] == req["sender_id"]), None)
                receiver = next((u for u in users if u["id"] == req["receiver_id"]), None)
                if sender:
                    sender["swaps_completed"] = sender.get("swaps_completed", 0) + 1
                    sender["experience_points"] = sender.get("experience_points", 0) + 50
                if receiver:
                    receiver["swaps_completed"] = receiver.get("swaps_completed", 0) + 1
                    receiver["experience_points"] = receiver.get("experience_points", 0) + 50
                count += 1
        if count > 0:
            data["requests"] = requests
            data["users"] = users
            write_data(data)
            st.success(f"Completed {count} swaps!")
            time.sleep(1)
            st.rerun()
        else:
            st.info("No accepted requests")
    
    # Calculate All Matches
    if st.button("Calculate Matches", use_container_width=True, key="calc_matches"):
        if len(users) >= 2:
            st.info(f"Analyzing {len(users)} users...")
            # This would trigger match calculation in Discover mode
            st.success("Ready to discover!")
        else:
            st.warning("Need at least 2 users")
    
    # Export Full JSON
    if st.button("Export Full Data", use_container_width=True, key="export_json"):
        st.download_button(
            "Download data.json",
            DATA_FILE.read_bytes() if DATA_FILE.exists() else b"{}",
            file_name=f"skillswap_{datetime.datetime.now().strftime('%Y%m%d')}.json",
            use_container_width=True
        )
    
    # Clear Completed
    if st.button("Clear Completed", use_container_width=True, key="clear_completed"):
        count = len([r for r in requests if r["status"] == "Completed"])
        data["requests"] = [r for r in requests if r["status"] != "Completed"]
        write_data(data)
        st.success(f"Cleared {count} completed requests")
        time.sleep(1)
        st.rerun()
    
    # Reset All Data
    if st.button("Reset All Data", use_container_width=True, key="reset"):
        write_data({"users": [], "requests": [], "messages": [], "endorsements": [], "achievements": []})
        st.session_state.current_user = None
        st.success("Reset complete!")
        time.sleep(1)
        st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)  # Close scrollable container
    
    st.markdown("---")
    st.markdown(f"""
        <div class='muted' style='text-align:center'>
            <div>{len(users)} Users</div>
            <div>{len(requests)} Requests</div>
            <div>{len([r for r in requests if r['status'] == 'Completed'])} Completed</div>
            <div style='margin-top:12px;font-size:11px'>v2.0 Engineering Edition</div>
        </div>
    """, unsafe_allow_html=True)

# ---------------- Header ----------------
st.markdown("""
    <div class='ultra-header'>
        <div class='header-content'>
            <h1 class='title-ultra'>SkillSwap </h1>
            <p class='subtitle-ultra'>Peer-to-Peer Skill Exchange Platform - Connect - Learn - Grow</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# ---------------- Pages (Same as before, but now with working Quick Actions) ----------------
if mode == "Dashboard":
    st.markdown("## Platform Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-number'>{len(users)}</div>
                <div class='stat-label'>Total Users</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_skills = sum(len(u["skills_offered"]) for u in users)
        st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-number'>{total_skills}</div>
                <div class='stat-label'>Skills Offered</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        pending = len([r for r in requests if r["status"] == "Pending"])
        st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-number'>{pending}</div>
                <div class='stat-label'>Pending</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        completed = len([r for r in requests if r["status"] == "Completed"])
        st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-number'>{completed}</div>
                <div class='stat-label'>Completed</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Top Contributors")
        top = sorted(users, key=lambda u: u.get("swaps_completed", 0), reverse=True)[:5]
        for idx, user in enumerate(top, 1):
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            cols = st.columns([1, 5, 2])
            with cols[0]:
                st.markdown(f"<div style='font-size:32px;font-weight:900;color:var(--primary)'>#{idx}</div>", unsafe_allow_html=True)
            with cols[1]:
                st.markdown(f"### {user['name']}")
                st.markdown(f"<div class='muted'>{user.get('swaps_completed', 0)} swaps - {user.get('rating', 0):.1f} - Level {user.get('level', 1)}</div>", unsafe_allow_html=True)
            with cols[2]:
                st.markdown(avatar_html(user['name']), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Recent Activity")
        recent = sorted(requests, key=lambda r: r["created_at"], reverse=True)[:5]
        if recent:
            for req in recent:
                sender = next((u for u in users if u["id"] == req["sender_id"]), None)
                receiver = next((u for u in users if u["id"] == req["receiver_id"]), None)
                if sender and receiver:
                    st.markdown(f"""
                        <div class='glass-card'>
                            <div style='display:flex;justify-content:space-between;align-items:center'>
                                <div>
                                    <strong>{sender['name']}</strong> → <strong>{receiver['name']}</strong>
                                    <div class='muted'>{req.get('skill_offered', '')} / {req.get('skill_wanted', '')}</div>
                                </div>
                                {status_badge_html(req['status'])}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No recent activity")

elif mode == "Create Profile":
    st.markdown("## Create Your Profile")
    
    with st.form("create_profile", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name *", placeholder="John Doe")
            email = st.text_input("Email *", placeholder="john@example.com")
            location = st.text_input("Location", placeholder="City, Country")
            bio = st.text_area("Bio", placeholder="Tell us about yourself...", height=120)
        
        with col2:
            offered = st.text_input("Skills Offered *", placeholder="python, react, docker")
            wanted = st.text_input("Skills Wanted *", placeholder="aws, kubernetes, golang")
            interests = st.text_input("Interests", placeholder="web dev, AI, cloud")
            availability = st.selectbox("Availability", ["Available", "Busy", "Away"])
        
        st.markdown("### Proficiency Levels")
        offered_list = [s.strip().lower() for s in offered.split(",") if s.strip()]
        proficiency = {}
        
        if offered_list:
            cols = st.columns(min(len(offered_list), 4))
            for idx, skill in enumerate(offered_list):
                with cols[idx % 4]:
                    proficiency[skill] = st.selectbox(
                        skill.capitalize(),
                        ["Beginner", "Intermediate", "Expert"],
                        key=f"prof_{skill}"
                    )
        
        if st.form_submit_button("Create Profile", use_container_width=True):
            if not name.strip() or not email.strip():
                st.error("Name and email required!")
            elif not offered_list:
                st.error("Add at least one skill!")
            else:
                wanted_list = [s.strip().lower() for s in wanted.split(",") if s.strip()]
                interest_list = [s.strip() for s in interests.split(",") if s.strip()]
                
                new_user = make_user(name, email, bio, offered_list, wanted_list, proficiency, location, interest_list)
                new_user["availability"] = availability
                users.append(new_user)
                data["users"] = users
                write_data(data)
                
                st.success("Profile created successfully!")
                time.sleep(2)
                st.rerun()

elif mode == "My Profile":
    st.markdown("## Your Profile")
    
    if not users:
        st.info("No profiles yet. Create one first!")
    else:
        profile_name = st.selectbox("Select Profile", ["Select..."] + [u["name"] for u in users])
        
        if profile_name != "Select...":
            user = next(u for u in users if u["name"] == profile_name)
            
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.markdown(avatar_html(user["name"]), unsafe_allow_html=True)
                st.markdown(f"<div style='text-align:center;margin-top:16px'><h3>{user['name']}</h3></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='muted' style='text-align:center'>{user.get('email', '')}</div>", unsafe_allow_html=True)
                
                st.markdown(f"""
                    <div style='text-align:center;margin-top:20px'>
                        <div style='font-size:28px;font-weight:900;color:var(--primary)'>{user.get('rating', 0):.1f}</div>
                        <div class='muted'>Rating</div>
                        <div style='margin-top:12px'>
                            <strong>{user.get('swaps_completed', 0)}</strong> swaps<br>
                            <strong>{user.get('endorsements_received', 0)}</strong> endorsements
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if user.get("location"):
                    st.markdown(f"**{user['location']}**")
                st.markdown(f"<div class='muted' style='margin:12px 0'>{user.get('bio', 'No bio')}</div>", unsafe_allow_html=True)
                
                st.markdown(level_progress_html(user), unsafe_allow_html=True)
                
                if user.get("badges"):
                    st.markdown("### Achievements")
                    badges_html = " ".join([f"<span class='badge-item'>{b}</span>" for b in user["badges"]])
                    st.markdown(badges_html, unsafe_allow_html=True)
                
                st.markdown("### Skills Offered")
                prof = user.get("proficiency", {})
                skills_html = " ".join([skill_badge_html(s, prof.get(s, ""), False) for s in user["skills_offered"]])
                st.markdown(skills_html or "<span class='muted'>None</span>", unsafe_allow_html=True)
                
                st.markdown("### Skills Wanted")
                wants_html = " ".join([skill_badge_html(s, "", True) for s in user["skills_wanted"]])
                st.markdown(wants_html or "<span class='muted'>None</span>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Delete Profile", key="del_profile"):
                data["users"] = [u for u in users if u["id"] != user["id"]]
                data["requests"] = [r for r in requests if r["sender_id"] != user["id"] and r["receiver_id"] != user["id"]]
                write_data(data)
                st.success("Deleted!")
                time.sleep(1)
                st.rerun()

elif mode == "Discover":
    st.markdown("## Discover Perfect Matches")
    
    if len(users) < 2:
        st.info("Need at least 2 users to discover matches!")
    else:
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            my_profile = st.selectbox("Your Profile", ["Select..."] + [u["name"] for u in users])
        with col2:
            search = st.text_input("Search skills", placeholder="python, react...")
        with col3:
            min_score = st.slider("Min Score", 0, 100, 40)
        
        if my_profile != "Select...":
            me = next(u for u in users if u["name"] == my_profile)
            candidates = []
            
            for other in users:
                if other["id"] == me["id"]:
                    continue
                
                if search:
                    combined = " ".join(other["skills_offered"] + other["skills_wanted"])
                    if search.lower() not in combined:
                        continue
                
                score, details = compatibility_score(me, other)
                if score >= min_score:
                    candidates.append((other, score, details))
            
            candidates.sort(key=lambda x: x[1], reverse=True)
            
            if not candidates:
                st.info("No matches found. Try adjusting filters!")
            else:
                st.markdown(f"<div class='muted'>Found {len(candidates)} matches</div>", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                
                for other, score, details in candidates:
                    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns([1, 4, 2])
                    
                    with col1:
                        st.markdown(avatar_html(other["name"]), unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"### {other['name']}")
                        st.markdown(f"<div class='muted'>{other.get('bio', '')[:150]}</div>", unsafe_allow_html=True)
                        prof = other.get("proficiency", {})
                        st.markdown("**Offers:** " + " ".join([skill_badge_html(s, prof.get(s, ""), False) for s in other["skills_offered"][:5]]), unsafe_allow_html=True)
                        st.markdown("**Wants:** " + " ".join([skill_badge_html(s, "", True) for s in other["skills_wanted"][:5]]), unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(compat_display_html(score, details), unsafe_allow_html=True)
                        if st.button("Request Swap", key=f"req_{other['id']}"):
                            skill_offered = (me.get("skills_offered") or [""])[0]
                            skill_wanted = (other.get("skills_offered") or [""])[0]
                            new_req = make_request(me["id"], other["id"], skill_offered, skill_wanted, f"Hi, let's swap!", "High")
                            requests.append(new_req)
                            data["requests"] = requests
                            write_data(data)
                            st.success("Request sent!")
                            time.sleep(1)
                            st.rerun()
                    
                    st.markdown("</div>", unsafe_allow_html=True)

elif mode == "Requests":
    st.markdown("## Swap Requests")
    
    if not requests:
        st.info("No requests yet!")
    else:
        tabs = st.tabs(["Received", "Sent", "Completed"])
        
        with tabs[0]:
            received = [r for r in requests if st.session_state.current_user and r["receiver_id"] == st.session_state.current_user["id"]]
            if received:
                for req in received:
                    sender = next((u for u in users if u["id"] == req["sender_id"]), None)
                    if sender:
                        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"### From: {sender['name']}")
                            st.markdown(f"**Offers:** {req.get('skill_offered', '')} | **Wants:** {req.get('skill_wanted', '')}")
                            st.markdown(f"{status_badge_html(req['status'])}", unsafe_allow_html=True)
                        with col2:
                            if req["status"] == "Pending":
                                if st.button("Accept", key=f"acc_{req['id']}"):
                                    req["status"] = "Accepted"
                                    data["requests"] = requests
                                    write_data(data)
                                    st.rerun()
                                if st.button("Reject", key=f"rej_{req['id']}"):
                                    req["status"] = "Rejected"
                                    data["requests"] = requests
                                    write_data(data)
                                    st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("No received requests")
        
        with tabs[1]:
            sent = [r for r in requests if st.session_state.current_user and r["sender_id"] == st.session_state.current_user["id"]]
            if sent:
                for req in sent:
                    receiver = next((u for u in users if u["id"] == req["receiver_id"]), None)
                    if receiver:
                        st.markdown(f"**To:** {receiver['name']} | {status_badge_html(req['status'])}", unsafe_allow_html=True)
            else:
                st.info("No sent requests")
        
        with tabs[2]:
            completed = [r for r in requests if r["status"] == "Completed"]
            if completed:
                for req in completed:
                    sender = next((u for u in users if u["id"] == req["sender_id"]), None)
                    receiver = next((u for u in users if u["id"] == req["receiver_id"]), None)
                    if sender and receiver:
                        st.markdown(f"**{sender['name']}** / **{receiver['name']}** | {req.get('skill_offered', '')} / {req.get('skill_wanted', '')}", unsafe_allow_html=True)
            else:
                st.info("No completed swaps")

elif mode == "Analytics":
    st.markdown("## Platform Analytics")
    
    if users:
        # Skills distribution
        all_skills = {}
        for u in users:
            for s in u.get("skills_offered", []):
                all_skills[s] = all_skills.get(s, 0) + 1
        
        if all_skills:
            st.markdown("### Most Offered Skills")
            top_skills = sorted(all_skills.items(), key=lambda x: x[1], reverse=True)[:10]
            for skill, count in top_skills:
                st.markdown(f"**{skill.capitalize()}**: {count} users")
        
        # Location distribution
        locations = {}
        for u in users:
            loc = u.get("location", "Unknown")
            locations[loc] = locations.get(loc, 0) + 1
        
        if locations:
            st.markdown("### User Locations")
            for loc, count in sorted(locations.items(), key=lambda x: x[1], reverse=True):
                st.markdown(f"**{loc}**: {count} users")
    else:
        st.info("No data yet!")

elif mode == "Leaderboard":
    st.markdown("## Top Performers")
    
    if users:
        sorted_users = sorted(users, key=lambda u: (u.get("swaps_completed", 0), u.get("rating", 0)), reverse=True)
        
        for idx, user in enumerate(sorted_users[:10], 1):
            medal = "#1" if idx == 1 else "#2" if idx == 2 else "#3" if idx == 3 else f"#{idx}"
            st.markdown(f"""
                <div class='glass-card'>
                    <h2>{medal} {user['name']}</h2>
                    <div class='muted'>
                        {user.get('rating', 0):.1f} | 
                        {user.get('swaps_completed', 0)} swaps | 
                        Level {user.get('level', 1)} | 
                        {user.get('experience_points', 0)} XP
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No users yet!")
