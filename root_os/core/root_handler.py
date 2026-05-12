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

# #=====
# [1] מנגנון ייבוא וקונפיגורציה ריבונית
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
            MANIFEST_PATH = "ROOT.md"


# #=====
# [2] ניהול משאבים ונעילה אטומית (atexit)
# #=====
LOCK_FILE = ".root_architect.lock"


def acquire_architect_lock():
    """
    נועל את המערכת למניעת Race Conditions.
    """
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE, "r") as f:
                old_pid = int(f.read().strip())
            os.kill(old_pid, 0)
            print(
                f"⏳ [Architect] System locked by PID {old_pid}. Aborting current sync."
            )
            return False
        except (OSError, ValueError):
            try:
                os.remove(LOCK_FILE)
            except:
                pass

    try:
        with open(LOCK_FILE, "w") as f:
            f.write(str(os.getpid()))
        return True
    except Exception as e:
        print(f"❌ [Architect] Lock error: {e}")
        return False


def release_architect_lock():
    """משחרר את הנעילה - מופעל תמיד בסיום דרך atexit."""
    if os.path.exists(LOCK_FILE):
        try:
            os.remove(LOCK_FILE)
        except:
            pass


atexit.register(release_architect_lock)


# #=====
# [3] מנוע האדריכלות האטומי (The Master Engine)
# #=====
def update_manifest(analysis_payload, critic_feedback=None):
    """
    הופך את כל ה-Payload למפרט הנדסי ברמת בורג.
    """
    if not acquire_architect_lock():
        return

    manifest_path = getattr(Config, "MANIFEST_PATH", "ROOT.md")
    blueprint_hash = hashlib.md5(
        (str(analysis_payload) + str(critic_feedback)).encode("utf-8")
    ).hexdigest()[:12]

    # בדיקת יציבות (Idempotency)
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            if f"BlueprintID: {blueprint_hash}" in f.read():
                print(
                    f"🔄 [Architect] Atomic state is stable (Hash: {blueprint_hash})."
                )
                release_architect_lock()
                return

    if not Config.API_KEY:
        print("⚠️ [Root Architect] No API Key.")
        release_architect_lock()
        return

    client = OpenAI(api_key=Config.API_KEY, base_url=Config.BASE_URL)

    # הזרקת דרישות רמת פירוט עילאית וצפיית פני עתיד
    system_prompt = f"""
    You are the 'Sovereign Atomic Architect'. Your output is the definitive HLD/LLD for Root OS.
    This document is the system's "Source of Truth".

    CRITICAL ENGINEERING STANDARDS (MASSIVE DETAIL REQUIRED):
    1. 100% INVENTORY: List EVERY single file provided. No generalizations.
       - For each: [Path | Logical Role | Micro-Logic Gates | Dependencies].
    2. ARCHITECTURAL RATIONALE: Explain the technical 'Why' behind every core module.
    3. THE CONTINUOUS LOOP: Detail the sub-second reaction flow: [FileSystem Event -> Watcher -> Ingestor -> Logic Handlers -> Manifest Update].
    4. DATA CONTRACTS: Map all schemas, from .env variables to the JSON structure of Core Dumps.
    5. OPERATIONAL BOUNDARIES: Document the 220,000 character context limit and the Industrial Locking mechanism (atexit).
    6. TECHNICAL HEBREW: Use surgical, high-level terms (חסינות לוגית, וקטור ביצוע, צימוד אטומי).
    """

    print(
        f"🏗️ [Root Architect] Synthesizing Digital Twin at {datetime.now().strftime('%H:%M:%S')}..."
    )

    try:
        response = client.chat.completions.create(
            model=Config.MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"PAYLOAD: {analysis_payload}\nCRITIC: {critic_feedback}",
                },
            ],
            temperature=0.1,
        )

        raw_blueprint = response.choices[0].message.content.strip()

        # ניקוי פורמט בטוח
        if raw_blueprint.startswith("```"):
            lines = raw_blueprint.split("\n")
            if lines[0].strip().startswith("```"):
                lines = lines[1:]
            if lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            raw_blueprint = "\n".join(lines).strip()

        # בניית המסמך הסופי - Tabula Rasa
        now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        header = f"# 🌳 Root OS: Sovereign Atomic Architecture\n\n> **הוראת מערכת:** זהו מניפסט ה-DNA המוחלט. כל בורג מתועד. אין פה היסטוריה.\n\n"
        footer = f"\n\n---\n*BlueprintID: {blueprint_hash}*\n*📐 אדריכלות מאומתת: {now_str} | מנוע: Root OS Master Architect V2*"

        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(header + raw_blueprint + footer)

        print(f"✅ [Root Architect] Master Blueprint locked (Hash: {blueprint_hash}).")

    except Exception as e:
        print(f"❌ [Root Architect Error]: {e}")
    finally:
        release_architect_lock()


# #=====

if __name__ == "__main__":
    mock_data = {"core": "active", "files": ["scanner.py", "architect.py"]}
    update_manifest(json.dumps(mock_data), "Initial scan nominal.")
