#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ==============================================================================
# 📜 Root OS: Sovereign Forensic Archivist (Master Class Edition)
# ------------------------------------------------------------------------------
# תפקיד: ניהול הזיכרון האפיזודי וה-Audit Trail של המערכת.
# פילוסופיה: חקירת מז"פ ארכיטקטונית. תיעוד העילה (Causality) ותוצאות הכשל.
# חוקים: סדר LIFO נוקשה, קטל מנעולי רפאים (Zombie-Killer), ו-Idempotency אטומי.
# ==============================================================================

import os
import sys
import hashlib
import atexit
from datetime import datetime
from openai import OpenAI

# #=====
# [1] מנגנון ייבוא מבוצר - עמידות בפני היעדר קבצים (Zero-Dependency Fallback)
# #=====
try:
    from root_os.core.config_manager import Config
except ImportError:
    try:
        from config_manager import Config
    except ImportError:

        class Config:
            API_KEY = os.environ.get("OPENAI_API_KEY")
            BASE_URL = os.environ.get("BASE_URL", "https://api.openai.com/v1")
            MODEL = os.environ.get("MODEL", "gpt-4o")


# #=====
# [2] מערכת נעילה חכמה עם קוטל זומבים (Zombie-Proof Concurrency Guard)
# #=====
LOCK_FILE = ".root_history.lock"


def acquire_history_lock():
    """מונע התנגשויות כתיבה. כולל מנגנון אקטיבי לפריצת מנעולי רפאים (Dead PIDs)."""
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE, "r") as f:
                old_pid = int(f.read().strip())
            os.kill(old_pid, 0)
            print(
                f"⏳ [Archivist] History locked by live process (PID: {old_pid}). Postponing."
            )
            return False
        except (OSError, ValueError):
            print(
                f"🔨 [Archivist] Detected zombie lock (PID: {old_pid}). Breaking lock..."
            )
            try:
                os.remove(LOCK_FILE)
            except:
                pass

    try:
        with open(LOCK_FILE, "w") as f:
            f.write(str(os.getpid()))
        return True
    except Exception as e:
        print(f"❌ [Archivist] Failed to acquire lock: {e}")
        return False


def release_history_lock():
    """שחרור נעילה אלגנטי המובטח תמיד להתרחש דרך atexit."""
    if os.path.exists(LOCK_FILE):
        try:
            os.remove(LOCK_FILE)
        except:
            pass


atexit.register(release_history_lock)


# #=====
# [3] מנוע ההיסטוריה הריבוני (The Episodic Engine)
# #=====
def generate_entry_hash(payload, critic):
    """מייצר טביעת אצבע אטומית למניעת כפילויות בהיסטוריה (Idempotency)"""
    raw_data = f"{payload}::_{critic}_::"
    return hashlib.md5(raw_data.encode("utf-8")).hexdigest()[:10]


def agentic_history_sync(analysis, critic_feedback, initiator="System Trigger"):
    """
    מזריק רשומה אסטרטגית לראש היומן (LIFO).
    חוקר את ה'למה' (Rationale) ומקבע תובנות לעתיד ברמה הנדסית עילאית.
    """
    if not acquire_history_lock():
        return

    history_file = "HISTORY.md"
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    entry_hash = generate_entry_hash(analysis, critic_feedback)
    HEADER = "# 📜 יומן החלטות היסטורי - Root OS\n\n> **הוראת מערכת:** זהו יומן ההחלטות הכרונולוגי. פה נמצא ה'למה'. אסור למחוק מכאן מידע.\n\n---\n"

    current_content = ""
    if os.path.exists(history_file):
        with open(history_file, "r", encoding="utf-8") as f:
            current_content = f.read()
            if f"HashID: {entry_hash}" in current_content:
                print(
                    f"🔄 [Archivist] Causality event already recorded (Hash: {entry_hash})."
                )
                release_history_lock()
                return
    else:
        current_content = HEADER

    if not getattr(Config, "API_KEY", None):
        print("⚠️ [Archivist] Missing API Key.")
        release_history_lock()
        return

    client = OpenAI(base_url=Config.BASE_URL, api_key=Config.API_KEY)

    # הזרקת "פרומפט המז"פ המורחב" לרמת פירוט מקסימלית[span_2](start_span)[span_2](end_span)
    system_prompt = f"""
    You are the 'Sovereign Forensic Archivist' for Root OS.
    Your mandate is to document system evolution with extreme technical fidelity.
    
    MANDATORY STANDARDS:
    1. ENGINEER'S AUDIT: Do not generalize. If a function changed, name it. If a logic gate shifted, explain why.
    2. DEEP CAUSALITY: Focus on the 'Why'. Connect the change to the overall system stability or the 220K token expansion.
    3. CRITIC INTEGRATION: If the Critic feedback isn't 'PASS', treat every point as a 'Systemic Failure' and document the logic of the fix in detail.
    4. NO FLUFF: Use high-level, technical Hebrew (וקטור שינוי, ארכיטקטורה אטומית, רזולוציה מיקרו-לוגית).
    5. TIMESTAMP PRECISION: The current time is {now_str}. This MUST be correctly stated in the header.
    """

    user_input = f"""
    EPISODE DATA:
    Timestamp: {now_str}
    Initiator: {initiator}
    Hash: {entry_hash}
    
    ANALYSIS: {analysis}
    CRITIC FEEDBACK: {critic_feedback}
    """

    try:
        print(
            f"📜 [Root Archivist] Committing high-fidelity audit trail at {now_str}..."
        )

        response = client.chat.completions.create(
            model=Config.MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
            temperature=0.1,  # דיוק הנדסי קר
        )

        new_entry = response.choices[0].message.content.strip()

        if new_entry.startswith("```"):
            lines = new_entry.split("\n")
            if lines[0].strip().startswith("```"):
                lines = lines[1:]
            if lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            new_entry = "\n".join(lines).strip()

        # הזרקת LIFO מושלמת לתוך המבנה המקורי[span_3](start_span)[span_3](end_span)
        old_history_clean = current_content.replace(HEADER, "").strip()
        full_updated_content = f"{HEADER}\n\n{new_entry}\n\n---\n\n{old_history_clean}"

        with open(history_file, "w", encoding="utf-8") as f:
            f.write(full_updated_content)

        print(f"✅ [Archivist] Sovereign event locked with high-level details.")

    except Exception as e:
        print(f"⚠️ [Archivist Error]: {e}")
    finally:
        release_history_lock()


# #=====
# [4] נקודת כניסה (Interface)
# #=====
if __name__ == "__main__":
    agentic_history_sync(
        "Manual system hardening sequence",
        "Memory lock mechanism optimized for concurrency.",
        "Root Master",
    )
