#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#=====
# 🧠 Root OS: Sovereign Monster Ingestor (Main Orchestrator)
# תפקיד: ניהול משאבים (Locking), ניתוח AI מורחב, והזנת הזיכרון הארכיטקטוני.
#=====

import os
import sys
import json
import atexit
from datetime import datetime

try:
    from dotenv import load_dotenv
except ImportError:
    print("⚠️ [Warning] 'python-dotenv' missing. Environment variables might not load. Run: pip install python-dotenv")
    load_dotenv = lambda **kwargs: None

#=====
# 🛠️ הוספת שורש הפרויקט, תיקיית ההרצה (CWD), ותיקיות הליבה ל-sys.path
# תיקון אגרסיבי למניעת שגיאות ייבוא בסביבות Termux/Mobile
current_core_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_core_dir, "../../"))
parent_os_dir = os.path.dirname(current_core_dir) # root_os
cwd = os.getcwd()

# טעינת קובץ ה-.env ישירות משורש הפרויקט בצורה בטוחה
env_path = os.path.join(project_root, ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv() # Fallback חיפוש סטנדרטי

# דחיפת כל הנתיבים האפשריים לתחילת רשימת החיפוש של פייתון
for path in [cwd, project_root, parent_os_dir, current_core_dir]:
    if path not in sys.path:
        sys.path.insert(0, path)
#=====

#=====
# ייבוא רכיב הזיכרון עם טיפול שגיאות שמדפיס את נתיבי החיפוש במקרה של כשל
try:
    from root_os.core.memory import RootMemory
except ImportError:
    try:
        from memory import RootMemory
    except ImportError as e:
        print(f"❌ [Critical] Could not find 'memory' module. Error: {e}")
        print(f"🔍 System paths currently loaded:\n" + "\n".join(sys.path))
        sys.exit(1)
#=====

#=====
# 1. ניהול נעילה תעשייתית (Concurrency Guard)
class RootLock:
    def __init__(self, project_path):
        self.lock_file = os.path.join(project_path, ".root.lock")

    def acquire(self):
        if os.path.exists(self.lock_file):
            try:
                with open(self.lock_file, "r") as f:
                    old_pid = int(f.read().strip())
                if self._is_pid_running(old_pid):
                    print(
                        f"⏳ [Root Ingestor] System locked by PID {old_pid}. Postponing."
                    )
                    return False
            except Exception:
                pass

        with open(self.lock_file, "w") as f:
            f.write(str(os.getpid()))
        return True

    def release(self):
        if os.path.exists(self.lock_file):
            try:
                os.remove(self.lock_file)
                print("🔒 [Root Lock] Lock released successfully.")
            except OSError:
                pass

    def _is_pid_running(self, pid):
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False
#=====

#=====
# 2. אתחול סביבה וטעינת Config
if len(sys.argv) < 2:
    print("❌ [Ingestor] Project path missing! Run via boot system.")
    sys.exit(1)

PROJECT_DIR = sys.argv[1]
LOCK = RootLock(PROJECT_DIR)

if not LOCK.acquire():
    sys.exit(0)

# הבטחת שחרור נעילה תמיד בסיום הריצה
atexit.register(LOCK.release)

try:
    from config_manager import Config
except ImportError:
    # Fallback להגדרות ברירת מחדל אם ה-Config חסר
    class Config:
        MODEL = "gpt-4o"
        BASE_URL = "https://openrouter.ai/api/v1"
        TOKEN_GUARD_LIMIT = 220000
        AGENT_TEMPERATURE = 0.2
        RAG_TOP_K = 5


RAW_DATA_FILE = os.path.join(PROJECT_DIR, ".root_core_dump.json")
#=====

#=====
# 3. מנועי ה-AI המשופרים
from openai import OpenAI
try:
    from git_engine import get_git_info
except ImportError:
    from root_os.core.git_engine import get_git_info

# הנדלרים של המפלצת
try:
    from root_handler import update_manifest
    from git_handler import autonomous_push
    from history_handler import agentic_history_sync
    from roadmap_handler import agentic_roadmap_sync, create_github_issue
except ImportError:
    # תמיכה בייבוא מתוך root_os אם ההנדלרים יושבים שם
    from root_os.core.root_handler import update_manifest
    from root_os.core.git_handler import autonomous_push
    from root_os.core.history_handler import agentic_history_sync
    from root_os.core.roadmap_handler import agentic_roadmap_sync, create_github_issue


client = OpenAI(
    base_url=getattr(Config, "BASE_URL", "https://openrouter.ai/api/v1"),
    api_key=os.environ.get("OPENAI_API_KEY"),
)


def analyze_diff(diff_text):
    # שימוש במגבלה המורחבת של 220,000 תווים
    limit = getattr(Config, "TOKEN_GUARD_LIMIT", 220000)
    if len(diff_text) > limit:
        diff_text = (
            diff_text[:limit] + "\n\n[... Diff truncated for context safety ...]"
        )

    print(
        f"🧠 [Ingestor Brain] High-Level Analysis (Context: {len(diff_text)} chars)..."
    )

    # פרומפט משופר לניתוח ארכיטקטוני עמוק
    prompt = (
        "You are the Root Architect. Analyze this code diff and provide a high-level summary in Hebrew. "
        "Focus on architectural shifts, logic flow, and structural impact. Use bullet points.\n\n"
        f"Diff:\n{diff_text}"
    )

    try:
        res = client.chat.completions.create(
            model=getattr(Config, "MODEL", "gpt-4o"),
            messages=[{"role": "user", "content": prompt}],
            temperature=getattr(Config, "AGENT_TEMPERATURE", 0.2),
        )
        return res.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ [API Error]: {e}")
        return None


def run_critic(diff_text, past_context=""):
    limit = getattr(Config, "TOKEN_GUARD_LIMIT", 220000)
    if len(diff_text) > limit:
        diff_text = diff_text[:limit] + "\n\n[... Diff truncated ...]"

    print(f"🛡️  [TestSentry Critic] Reviewing quality with systemic context...")
    context_str = f"\nSystem Context:\n{past_context}" if past_context else ""
    prompt = f"As the Root Critic, review this diff. If perfect, output ONLY 'PASS'. Otherwise, list actionable systemic risks in Hebrew.{context_str}\n\nDiff:\n{diff_text}"

    try:
        res = client.chat.completions.create(
            model=getattr(Config, "MODEL", "gpt-4o"),
            messages=[
                {
                    "role": "system",
                    "content": "You are the Root Critic. Brutally honest, objective, atomic.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
        )
        return res.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ [API Error]: {e}")
        return None
#=====

#=====
# 4. הזרם המרכזי (The Orchestration Loop)
if __name__ == "__main__":
    os.chdir(PROJECT_DIR)

    # הבטחת קובץ היסטוריה קיים
    if not os.path.exists("HISTORY.md"):
        with open("HISTORY.md", "w", encoding="utf-8") as f:
            f.write("# 📜 יומן החלטות היסטורי - Root OS\n\n---\n")

    # שליפת המידע מה-Git
    diff, metadata, run_mode = get_git_info(PROJECT_DIR)

    if diff and run_mode in ["LIVE", "FINAL"]:
        root_memory = RootMemory()

        # חיפוש מורחב בזיכרון RAG לפי ההגדרות החדשות
        past_context = ""
        try:
            top_k = getattr(Config, "RAG_TOP_K", 5)
            results = root_memory.search_memory(query=diff, top_k=top_k)
            if results:
                past_context = "\n".join(
                    [r[1]["text"] for r in results if isinstance(r, tuple)]
                )
        except:
            pass

        analysis = analyze_diff(diff)
        critic = run_critic(diff, past_context)

        if analysis:
            print(f"⚙️  [Ingestor] Updating manifests and memory...")
            update_manifest(analysis, critic)  # עדכון ROOT.md

            if run_mode == "FINAL":
                agentic_roadmap_sync(analysis, critic)
                agentic_history_sync(analysis, critic, "Monster Ingestor")
                root_memory.add_memory(
                    text=f"Analysis: {analysis}\nCritic: {critic}", metadata=metadata
                )

                print("🌐 [Ingestor] Syncing to cloud...")
                autonomous_push(PROJECT_DIR)

            # יצירת Dump מעודכן לדשבורד
            try:
                payload = {
                    "timestamp": datetime.now().isoformat(),
                    "mode": run_mode,
                    "analysis": analysis,
                    "critic": critic,
                }
                with open(RAW_DATA_FILE, "w", encoding="utf-8") as f:
                    json.dump(payload, f, ensure_ascii=False, indent=4)
            except:
                pass

            print(f"✨ [Ingestor] Sequence complete ({run_mode}).")
    else:
        print("ℹ️ [Ingestor] No critical mass shifts detected.")
#=====
