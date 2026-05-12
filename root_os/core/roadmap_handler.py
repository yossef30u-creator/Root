#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ==============================================================================
# 🗺️ Root OS: Sovereign Tactical Strategist (Master Class Edition)
# ------------------------------------------------------------------------------
# תפקיד: ניהול הנתיב הקריטי (Critical Path), חוב טכני (Tech Debt), ומיקרו-משימות.
# פילוסופיה: ניהול מוצר אגרסיבי. אין משימות עמומות. כל משימה משויכת לקובץ מדויק.
# חוקים: השמדת משימות שבוצעו, חסינות לזומבים, סנכרון GitHub, ו-Idempotency אטומי.
# ==============================================================================

import os
import sys
import json
import hashlib
import atexit
import subprocess
import requests
from datetime import datetime
from openai import OpenAI

# #=====
# [1] מנגנון ייבוא מבוצר - עמידות בפני סביבה קורסת (Zero-Dependency)
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
            GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")


# #=====
# [2] מערכת נעילה טקטית עם קוטל זומבים (Zombie-Proof Lock)
# #=====
LOCK_FILE = ".root_roadmap.lock"


def acquire_roadmap_lock():
    """מנגנון Concurrency קשיח. משמיד מנעולים שנשארו מתהליכים שקרסו."""
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE, "r") as f:
                old_pid = int(f.read().strip())
            os.kill(old_pid, 0)  # וידוא חיות מול ה-OS
            print(
                f"⏳ [Strategist] Roadmap locked by live process (PID: {old_pid}). Postponing."
            )
            return False
        except (OSError, ValueError):
            print(
                f"🔨 [Strategist] Crushing zombie lock (PID: {old_pid}). Proceeding..."
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
        print(f"❌ [Strategist] Lock failure: {e}")
        return False


def release_roadmap_lock():
    """שחרור אלגנטי המובטח תמיד להתרחש דרך atexit."""
    if os.path.exists(LOCK_FILE):
        try:
            os.remove(LOCK_FILE)
            print("🔒 [Strategist Lock] Released.")
        except:
            pass


atexit.register(release_roadmap_lock)


# #=====
# [3] אינטגרציה חיצונית (GitHub Tactical Ops)
# #=====
def get_current_repo():
    """זיהוי דינאמי של סביבת הגיטהאב לצורך סנכרון"""
    try:
        url = (
            subprocess.check_output(
                ["git", "remote", "get-url", "origin"], stderr=subprocess.DEVNULL
            )
            .decode()
            .strip()
        )
        if "github.com/" in url:
            return url.split("github.com/")[-1].replace(".git", "")
    except:
        return None
    return None


def create_github_issue(title, body, labels=None):
    """נשק יום הדין: האסטרטג פותח תקלות לעצמו אם המצב קריטי"""
    repo = get_current_repo()
    if not Config.GITHUB_TOKEN or not repo:
        return

    labels = labels or ["root-task", "P1-Urgent"]
    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {
        "Authorization": f"token {Config.GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    try:
        requests.post(
            url,
            json={"title": title, "body": body, "labels": labels},
            headers=headers,
            timeout=5,
        )
    except:
        pass


# #=====
# [4] מנוע האסטרטגיה הריבוני (The Tactical Engine)
# #=====
def generate_strategy_hash(payload, critic):
    """חתימה מתמטית של מצב הקוד למניעת ניתוח סרק."""
    raw_data = f"{payload}::_{critic}_::TACTICAL"
    return hashlib.md5(raw_data.encode("utf-8")).hexdigest()[:10]


def agentic_roadmap_sync(analysis, critic_feedback):
    """מנתח את המצב, משמיד משימות שבוצעו, וגוזר מיקרו-משימות לביצוע מיידי."""
    if not acquire_roadmap_lock():
        return

    roadmap_file = "ROADMAP.md"
    strategy_hash = generate_strategy_hash(analysis, critic_feedback)
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    current_roadmap = ""
    if os.path.exists(roadmap_file):
        with open(roadmap_file, "r", encoding="utf-8") as f:
            current_roadmap = f.read()
            if f"StrategyID: {strategy_hash}" in current_roadmap:
                print(
                    f"🔄 [Strategist] Path is already optimized (Hash: {strategy_hash})."
                )
                release_roadmap_lock()
                return

    if not Config.API_KEY:
        print("⚠️ [Strategist] API Key missing.")
        release_roadmap_lock()
        return

    client = OpenAI(base_url=Config.BASE_URL, api_key=Config.API_KEY)

    # הזרקת דרישות רמה גבוהה, זמן ותאריך לתוך הפרומפט
    system_prompt = f"""
    You are the 'Sovereign Technical Architect' for Root OS.
    Your output is an Engineering Blueprint, not a simple list.
    
    MANDATORY: You MUST start the document with the current timestamp: {now}.

    TACTICAL ARCHITECTURE RULES:
    1. EXTREME DETAIL: Every task must be broken down. Never write "Fix UI". Write "Refactor class X in file Y to include Z validation".
    2. THE CRITIC IS LAW: Convert every 'Critic Feedback' into a P1-Urgent Fix.
    3. NO VAGUENESS: Each task needs a TARGET FILE and a clear 'Definition of Done'.
    4. RUTHLESS PRUNING: Delete any task that 'Latest Analysis' shows as already completed.
    5. HEBREW PRECISION: Use technical, professional Hebrew.
    """

    print(f"🗺️  [Strategist] Mapping critical path at {now} (Hash: {strategy_hash})...")

    try:
        response = client.chat.completions.create(
            model=Config.MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"TIME: {now}\nPlan:\n{current_roadmap}\n\nState:\n{analysis}\n\nCritic:\n{critic_feedback}",
                },
            ],
            temperature=0.1,
        )

        new_content = response.choices[0].message.content.strip()

        # ניקוי פורמט Markdown
        if new_content.startswith("```"):
            lines = new_content.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            new_content = "\n".join(lines).strip()

        # הבטחת חתימת Hash וזמן במידה והסוכן שכח
        header = f"> **Last Tactical Update:** {now}\n\n"
        if now not in new_content:
            new_content = header + new_content
        if f"StrategyID: {strategy_hash}" not in new_content:
            new_content += f"\n\n---\n*StrategyID: {strategy_hash}*"

        with open(roadmap_file, "w", encoding="utf-8") as f:
            f.write(new_content)

        print("✅ [Strategist] High-fidelity roadmap deployed.")

    except Exception as e:
        print(f"❌ [Strategist Error]: {e}")
    finally:
        release_roadmap_lock()


# #=====
# [5] ממשק ה-Handler לסורק הגלובלי
# #=====
class RoadmapHandler:
    def update(self, analysis="Update", critic="None"):
        agentic_roadmap_sync(analysis, critic)


if __name__ == "__main__":
    agentic_roadmap_sync("Scanner initialized", "Incomplete architecture file")
