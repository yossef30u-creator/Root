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

# ------------------------------------------------------------------------------
# [1] מנגנון ייבוא מבוצר - עמידות בפני היעדר קבצים (Zero-Dependency Fallback)
# ------------------------------------------------------------------------------
try:
    from root_os.core.config_manager import Config
except ImportError:
    try:
        from config_manager import Config
    except ImportError:
        # Fallback מפלצתי: יצירת Config דינאמי מתוך סביבת הריצה
        class Config:
            API_KEY = os.environ.get("OPENAI_API_KEY")
            BASE_URL = os.environ.get("BASE_URL", "https://api.openai.com/v1")
            MODEL = os.environ.get("MODEL", "gpt-4o")

# ------------------------------------------------------------------------------
# [2] מערכת נעילה חכמה עם קוטל זומבים (Zombie-Proof Concurrency Guard)
# ------------------------------------------------------------------------------
LOCK_FILE = ".root_history.lock"

def acquire_history_lock():
    """מונע התנגשויות כתיבה. כולל מנגנון אקטיבי לפריצת מנעולי רפאים (Dead PIDs)."""
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE, "r") as f:
                old_pid = int(f.read().strip())
            # שליחת סיגנל 0 כדי לבדוק אם התהליך באמת חי ב-OS
            os.kill(old_pid, 0)
            print(f"⏳ [Archivist] History locked by live process (PID: {old_pid}). Postponing.")
            return False
        except (OSError, ValueError):
            # התהליך מת אך המנעול נשאר (Zombie Lock) - שוברים אותו!
            print(f"🔨 [Archivist] Detected zombie lock (PID: {old_pid}). Breaking lock...")
            try: os.remove(LOCK_FILE)
            except: pass

    # יצירת מנעול חדש בבטחה
    try:
        with open(LOCK_FILE, "w") as f:
            f.write(str(os.getpid()))
        return True
    except Exception as e:
        print(f"❌ [Archivist] Failed to acquire lock: {e}")
        return False

def release_history_lock():
    """שחרור נעילה אלגנטי. מופעל תמיד בסיום או בקריסה (Graceful Shutdown)."""
    if os.path.exists(LOCK_FILE):
        try: os.remove(LOCK_FILE)
        except: pass

# הטאקסיט (atexit): הברזל של המערכת - מבטיח שחרור תמיד!
atexit.register(release_history_lock)

# ------------------------------------------------------------------------------
# [3] מנוע ההיסטוריה הריבוני (The Episodic Engine)
# ------------------------------------------------------------------------------
def generate_entry_hash(payload, critic):
    """מייצר טביעת אצבע אטומית למניעת כפילויות בהיסטוריה (Idempotency)"""
    raw_data = f"{payload}::_{critic}_::"
    return hashlib.md5(raw_data.encode('utf-8')).hexdigest()[:10]

def agentic_history_sync(analysis, critic_feedback, initiator="System Trigger"):
    """
    מזריק רשומה אסטרטגית לראש היומן (LIFO).
    חוקר את ה'למה' (Rationale) ומקבע תובנות לעתיד.
    """
    if not acquire_history_lock(): return

    history_file = "HISTORY.md"
    now_str = datetime.now().strftime('%d/%m/%Y %H:%M')
    
    # 1. יצירת חותמת זהות (Idempotency Guard)
    entry_hash = generate_entry_hash(analysis, critic_feedback)
    
    # 2. ה-Header הקבוע (The Eternal Contract)
    HEADER = "# 📜 יומן החלטות היסטורי - Root OS\n\n> **הוראת מערכת:** זהו יומן ההחלטות הכרונולוגי. פה נמצא ה'למה'. אסור למחוק מכאן מידע.\n\n---\n"

    # 3. קריאה וסינון כפילויות אקטיבי
    current_content = ""
    if os.path.exists(history_file):
        with open(history_file, "r", encoding="utf-8") as f:
            current_content = f.read()
            # הגנה מפלצתית: בלימת שווא אם האירוע כבר תועד
            if f"HashID: {entry_hash}" in current_content:
                print(f"🔄 [Archivist] Causality event already recorded (Hash: {entry_hash}). Silently skipping.")
                return
    else:
        current_content = HEADER

    # 4. אתחול מוח ה-AI
    if not getattr(Config, 'API_KEY', None):
        print("⚠️ [Archivist] Missing API Key in config. Ephemeral mode active (No log written).")
        return

    client = OpenAI(
        base_url=Config.BASE_URL,
        api_key=Config.API_KEY,
        default_headers={"X-Title": "Root Sovereign Archivist"}
    )

    # --------------------------------------------------------------------------
    # הפרומפט המז"פי (Forensic Engineering Prompt)
    # --------------------------------------------------------------------------
    system_prompt = f"""
    You are the 'Sovereign Forensic Archivist' for Root OS.
    Your mandate is to maintain the 'Episodic Memory' and 'Audit Trail' of the system.
    
    CRITICAL FORENSIC RULES:
    1. STRICT CAUSALITY: Do not merely summarize the diff. Explain the STRATEGIC REASON for the change.
    2. FAILURE ANALYSIS: If the Critic (TestSentry) reported warnings, document them explicitly as 'Systemic Failures' and state the corrective logic applied.
    3. NO FLUFF: Brutally objective, analytical, and professional Hebrew tone.
    4. IMMUTABLE FORMAT: You MUST follow the exact markdown structure below. Do not deviate.
    
    MANDATORY STRUCTURE:
    ## 📅 {now_str} | Initiator: {initiator} | HashID: {entry_hash}
    - 🎯 **עילה אסטרטגית ושורש הבעיה:** (Root cause analysis - Why this execution occurred)
    - 🏗️ **וקטור השינוי הלוגי:** (Atomic level description of what mechanisms shifted)
    - 🛡️ **חוסן ומסקנות לעתיד:** (Self-Healing insights derived from the Critic feedback)
    """

    # קיצוץ ההקשר הישן כדי לשמור על טוקנים, אבל השארת דוגמה לסגנון
    context_snippet = current_content.replace(HEADER, "").strip()[:3000]

    try:
        print(f"📜 [Root Archivist] Committing forensic audit trail (Hash: {entry_hash})...")
        
        # שימוש ב-temperature נמוך לטובת כתיבה אנליטית קרה ומדויקת
        response = client.chat.completions.create(
            model=Config.MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context Memory:\n{context_snippet}\n\nLive Analysis:\n{analysis}\n\nCritic Feedback:\n{critic_feedback}"}
            ],
            temperature=0.15 
        )
        
        new_entry = response.choices[0].message.content.strip()
        
        # ניקוי בטוח מתגיות Markdown (התיקון של השבירה)
        if new_entry.startswith("```"):
            lines = new_entry.split("\n")
            if len(lines) > 0 and lines[0].strip().startswith("```"):
                lines = lines[1:]
            if len(lines) > 0 and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            new_entry = "\n".join(lines).strip()

        # 5. הזרקת LIFO מושלמת: כותרת -> רשומה חדשה -> היסטוריה ישנה
        old_history_clean = current_content.replace(HEADER, "").strip()
        full_updated_content = f"{HEADER}\n\n{new_entry}\n\n---\n\n{old_history_clean}"

        with open(history_file, "w", encoding="utf-8") as f:
            f.write(full_updated_content)
            
        print(f"✅ [Archivist] Sovereign event locked into Episodic Memory.")

    except Exception as e:
        print(f"⚠️ [Archivist Error] Core memory sync failed: {e}")
    finally:
        # אבטחת שחרור נעילה בכל תרחיש (הגנת ברזל)
        release_history_lock()

# ------------------------------------------------------------------------------
# [4] נקודת כניסה (Interface)
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    # בדיקת חיות (Heartbeat Test) ללא שבירת המערכת
    agentic_history_sync("System bootstrap verification", "All core services nominal. Watcher active.", "Architect Daemon")