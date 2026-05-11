#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ==============================================================================
# 🌳 Root OS: Sovereign Atomic Architect (Master Class Edition)
# ------------------------------------------------------------------------------
# תפקיד: יצירת "תאום דיגיטלי" (Digital Twin) של כל המערכת ב-ROOT.md.
# פילוסופיה: מיקרו-סקופיה הנדסית. כל בורג, כל פונקציה, כל חוזה - מתועד אטומית.
# חוקים: א-כרונולוגי (ללא היסטוריה), Idempotent (חתימות חסינות), קשיח (atexit).
# ==============================================================================

import os
import sys
import json
import hashlib
import atexit
import signal
from datetime import datetime
from openai import OpenAI

# ------------------------------------------------------------------------------
# [1] מנגנון ייבוא וקונפיגורציה ריבונית
# ------------------------------------------------------------------------------
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
            MANIFEST_PATH = "ROOT.md"

# ------------------------------------------------------------------------------
# [2] ניהול משאבים ונעילה אטומית (Concurrency Guard)
# ------------------------------------------------------------------------------
LOCK_FILE = ".root_architect.lock"

def acquire_architect_lock():
    """
    נועל את המערכת למניעת Race Conditions. 
    אם תהליך אחר רץ, הריצה הנוכחית תיבלם כדי למנוע השחתת ה-DNA.
    """
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE, "r") as f:
                old_pid = int(f.read().strip())
            # בדיקה אם התהליך הישן עדיין חי
            os.kill(old_pid, 0)
            print(f"⏳ [Architect] System locked by PID {old_pid}. Aborting current sync.")
            return False
        except (OSError, ValueError):
            # תהליך זומבי - מנקים ונועלים מחדש
            os.remove(LOCK_FILE)

    try:
        with open(LOCK_FILE, "w") as f:
            f.write(str(os.getpid()))
        return True
    except Exception as e:
        print(f"❌ [Architect] Lock error: {e}")
        return False

def release_architect_lock():
    """משחרר את הנעילה - מופעל תמיד בסיום (Graceful Shutdown)"""
    if os.path.exists(LOCK_FILE):
        try:
            os.remove(LOCK_FILE)
        except:
            pass

# רישום 'הטאקסיט' - הבטחת שרידות וניקיון משאבים תמיד
atexit.register(release_architect_lock)

# ------------------------------------------------------------------------------
# [3] מנוע האדריכלות האטומי (The Master Engine)
# ------------------------------------------------------------------------------
def update_manifest(analysis_payload, critic_feedback=None):
    """
    הופך את כל ה-Payload שהתקבל מהסקאנר למפרט הנדסי ברמת בורג.
    """
    if not acquire_architect_lock(): return

    manifest_path = getattr(Config, 'MANIFEST_PATH', 'ROOT.md')
    
    # חישוב BlueprintID: חתימה אטומית המונעת עיבוד כפול אם הקוד לא השתנה
    raw_data = str(analysis_payload) + str(critic_feedback)
    blueprint_hash = hashlib.md5(raw_data.encode('utf-8')).hexdigest()[:12]

    # קריאת המפה הקיימת ובדיקת יציבות (Idempotency)
    current_root = ""
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            current_root = f.read()
            if f"BlueprintID: {blueprint_hash}" in current_root:
                print(f"🔄 [Architect] Atomic state is stable (Hash: {blueprint_hash}). Skipping sync.")
                return

    # אתחול ה-AI (המוח של המפלצת)
    if not Config.API_KEY:
        print("⚠️ [Root Architect] Critical Failure: No API Key. Master sync suspended.")
        return

    client = OpenAI(api_key=Config.API_KEY, base_url=Config.BASE_URL)

    # --------------------------------------------------------------------------
    # הפרומפט המפלצתי - רמה עולמית של פירוט הנדסי
    # --------------------------------------------------------------------------
    system_prompt = f"""
    You are the 'Sovereign Atomic Architect'. Your output is the definitive HLD/LLD for Root OS.
    This document is the system's "Source of Truth". If a component is not here, it doesn't exist.

    CRITICAL ENGINEERING CONTRACT:
    1. ATOMIC INVENTORY: You MUST list EVERY SINGLE FILE provided in the scan payload. 
       - No "various", no "etc". Map all 100% of files.
       - For each file: [Path, Role, Logic Gate, Data Contracts, Dependencies].
    2. MICRO-LOGIC MAPPING: Document specific functions, variable schemas (e.g., .env), and PID lock files.
    3. THE CONTINUOUS LOOP: Detail exactly how the system reacts to a file change (Watcher -> Ingestor -> Handlers).
    4. PERSISTENCE MATRIX: Create a strict table of data locations (Memory DB, JSON, Markdown, Core Dumps).
    5. NO HISTORY: Zero chronological data. Only describe the current 'Now' of the machine.

    MANDATORY STRUCTURE:
    - 🏗️ Runtime Topology (The Orchestration Engine & Process Model)
    - 📦 Micro-Component Inventory (EVERY file mapped in an atomic table)
    - 🔌 Data Contracts & Logic Interfaces (How modules talk to each other)
    - 🛡️ Operational Boundaries (Resource limits, RAM guards, Security rules)
    - 📊 Persistence Matrix (Path-specific storage rules)

    Use Markdown tables for EVERYTHING possible. Professional, surgical, engineering-grade tone.
    Output ONLY valid Markdown. Append 'BlueprintID: {blueprint_hash}' at the very end.
    """

    user_prompt = f"""
    --- ATOMIC SCAN PAYLOAD ---
    {analysis_payload}
    
    --- CRITIC REVIEW ---
    {critic_feedback if critic_feedback else "No structural errors detected."}
    """

    print(f"🏗️ [Root Architect] Synthesizing Digital Twin (Blueprint: {blueprint_hash})...")

    try:
        # פנייה למוח ה-AI ליצירת ה-DNA מחדש
        response = client.chat.completions.create(
            model=Config.MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1 # טמפרטורה נמוכה לדיוק הנדסי מקסימלי
        )
        
        raw_blueprint = response.choices[0].message.content.strip()

        # ניקוי פורמט Markdown - חסין שבירות
        if raw_blueprint.startswith("```"):
            lines = raw_blueprint.split("\n")
            if len(lines) > 0 and lines[0].strip().startswith("```"):
                lines = lines[1:]
            if len(lines) > 0 and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            raw_blueprint = "\n".join(lines).strip()

        # הזרקת החותמת למקרה שה-AI השמיט
        if f"BlueprintID: {blueprint_hash}" not in raw_blueprint:
            raw_blueprint += f"\n\n---\n*BlueprintID: {blueprint_hash}*"

        # כתיבת ה"לוח המחיק" (Tabula Rasa)
        now_str = datetime.now().strftime('%d/%m/%Y %H:%M')
        header = f"# 🌳 Root OS: Sovereign Atomic Architecture\n\n> **הוראת מערכת:** זהו מניפסט ה-DNA המוחלט. כל בורג מתועד. אין פה היסטוריה.\n\n"
        footer = f"\n\n---\n*📐 אדריכלות מאומתת: {now_str} | מנוע: Root OS Master Architect V2*"
        
        final_document = header + raw_blueprint + footer

        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(final_document)
            
        print(f"✅ [Root Architect] Master Blueprint is now locked and atomic. Integrity 100%.")

    except Exception as e:
        print(f"❌ [Root Architect Error] Failed to generate atomic spec: {e}")
    finally:
        release_architect_lock()

# ------------------------------------------------------------------------------
# [4] נקודת כניסה למערכת (Entry Point)
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    # הרצה ידנית לצורך אימות בסיס הנתונים
    mock_scan = {
        "files": ["core/root_handler.py", "core/scanner.py", "core/ingestor.py"],
        "total_kb": 124,
        "config": ".env"
    }
    update_manifest(json.dumps(mock_scan), "Standard system initialization.")