#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ==============================================================================
# 🧠 Root OS: Sovereign Monster Ingestor (Main Orchestrator)
# ------------------------------------------------------------------------------
# תפקיד: ניהול משאבים (Locking), הפעלת מנוע הראייה, ניתוח AI, והזנת ההנדלרים.
# ==============================================================================

import os
import sys
import json
import atexit
from datetime import datetime

# ==========================================
# 1. ניהול נעילה תעשייתית (Concurrency Guard)
# ==========================================
class RootLock:
    def __init__(self, project_path):
        self.lock_file = os.path.join(project_path, ".root.lock")

    def acquire(self):
        if os.path.exists(self.lock_file):
            try:
                with open(self.lock_file, "r") as f:
                    old_pid = int(f.read().strip())
                if self._is_pid_running(old_pid):
                    print(f"⏳ [Root Ingestor] System locked by PID {old_pid}. Postponing.")
                    return False
            except Exception: pass
            
        with open(self.lock_file, "w") as f:
            f.write(str(os.getpid()))
        return True

    def release(self):
        if os.path.exists(self.lock_file):
            try: os.remove(self.lock_file)
            except OSError: pass

    def _is_pid_running(self, pid):
        try:
            os.kill(pid, 0)
            return True
        except OSError: return False

# ==========================================
# 2. אתחול סביבה קשיח
# ==========================================
if len(sys.argv) < 2:
    print("❌ [Ingestor] Project path missing! Run via boot system.")
    sys.exit(1)

PROJECT_DIR = sys.argv[1]
LOCK = RootLock(PROJECT_DIR)

if not LOCK.acquire(): sys.exit(0)
atexit.register(LOCK.release) # הבטחת שחרור תמיד

CORE_DIR = os.path.dirname(os.path.abspath(__file__))
if CORE_DIR not in sys.path: sys.path.append(CORE_DIR)

RAW_DATA_FILE = os.path.join(PROJECT_DIR, ".root_core_dump.json")

# ==========================================
# 3. טעינת Config והזרקת משתני סביבה
# ==========================================
try:
    from config_manager import Config
    os.environ["OPENAI_API_KEY"] = Config.API_KEY or ""
    os.environ["BASE_URL"] = getattr(Config, 'BASE_URL', "https://api.openai.com/v1")
    os.environ["MODEL"] = getattr(Config, 'MODEL', "gpt-4o")
except ImportError:
    print("⚠️ [Ingestor] Config module missing. Relying on environment variables.")

if not os.environ.get("OPENAI_API_KEY"):
    print("❌ [Ingestor] API Key missing. Halting execution.")
    sys.exit(1)

# ==========================================
# 4. ייבוא איברים פנימיים
# ==========================================
from openai import OpenAI
from git_engine import get_git_info # המודול המפוצל שלנו
from memory import RootMemory

# הנדלרים של המפלצת
from root_handler import update_manifest
from git_handler import autonomous_push
from history_handler import agentic_history_sync
from roadmap_handler import agentic_roadmap_sync, create_github_issue

client = OpenAI(
    base_url=os.environ["BASE_URL"],
    api_key=os.environ["OPENAI_API_KEY"],
    default_headers={"X-Title": "Root Agentic OS"}
)

# ==========================================
# 5. מנועי ה-AI
# ==========================================
def analyze_diff(diff_text):
    if len(diff_text) > 40000:
        diff_text = diff_text[:40000] + "\n\n[... Diff truncated ...]"

    print(f"🧠 [Ingestor Brain] Analyzing semantic impact...")
    prompt = f"Analyze this code diff. Provide a surgical summary in Hebrew using bullet points. Focus on architectural shifts:\n\n{diff_text}"
    
    try:
        res = client.chat.completions.create(model=os.environ["MODEL"], messages=[{"role": "user", "content": prompt}], temperature=0.2)
        return res.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ [API Error]: {e}")
        return None

def run_critic(diff_text, past_context=""):
    if len(diff_text) > 40000:
        diff_text = diff_text[:40000] + "\n\n[... Diff truncated ...]"

    print(f"🛡️  [TestSentry Critic] Reviewing code quality...")
    context_str = f"\nSystem Context:\n{past_context}" if past_context else ""
    prompt = f"As the Root Critic, review this diff. If perfect, output ONLY 'PASS'. Otherwise, list actionable systemic risks in Hebrew.{context_str}\n\nDiff:\n{diff_text}"
    
    try:
        res = client.chat.completions.create(
            model=os.environ["MODEL"],
            messages=[
                {"role": "system", "content": "You are the Root Critic. Brutally honest, objective, atomic."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        return res.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ [API Error]: {e}")
        return None

def export_core_dump(run_mode, analysis, critic_feedback):
    try:
        payload = {"timestamp": datetime.now().isoformat(), "mode": run_mode, "analysis": analysis, "critic": critic_feedback}
        with open(RAW_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=4)
    except: pass

# ==========================================
# 6. הזרם המרכזי (The Orchestration Loop)
# ==========================================
if __name__ == "__main__":
    os.chdir(PROJECT_DIR)
    
    # הבטחת היסטוריה חסינה
    if not os.path.exists("HISTORY.md"):
        with open("HISTORY.md", "w", encoding="utf-8") as f:
            f.write("# 📜 יומן החלטות היסטורי - Root OS\n\n> **הוראת מערכת:** זהו יומן ההחלטות הכרונולוגי. פה נמצא ה'למה'. אסור למחוק מכאן מידע.\n\n---\n")

    # קריאה למנוע הראייה
    diff, metadata, run_mode = get_git_info(PROJECT_DIR)
    
    if diff and run_mode in ["LIVE", "FINAL"]:
        root_memory = RootMemory()
        print(f"🚀 [Ingestor] Mode: {run_mode} | Executing context extraction...")
        
        past_context = ""
        try:
            results = root_memory.search_memory(query=diff, top_k=2)
            if results: past_context = "\n".join([r[1]["text"] for r in results if isinstance(r, tuple)])
        except: pass

        analysis = analyze_diff(diff)
        critic = run_critic(diff, past_context)
        
        # הגנת Github
        if run_mode == "FINAL" and critic and not critic.startswith("PASS"):
            create_github_issue(f"Root Critic Alert: Commit {metadata['commit']}", f"### Issue:\n{critic}")
        
        if analysis:
            print(f"⚙️  [Ingestor] Activating the Sovereign Trinity...")
            update_manifest(analysis, critic)
            
            if run_mode == "FINAL":
                agentic_roadmap_sync(analysis, critic)
                agentic_history_sync(analysis, critic, "Monster Ingestor")
                root_memory.add_memory(text=f"Analysis: {analysis}\nCritic: {critic}", metadata=metadata)
                
                print("🌐 [Ingestor] Pushing states to cloud...")
                autonomous_push(PROJECT_DIR)
                print("✨ [Ingestor] Final sequence complete.")
            else:
                print("⚡ [Ingestor] Live sequence complete.")
                
            export_core_dump(run_mode, analysis, critic)
    else:
        print("ℹ️ [Ingestor] No critical mass shifts detected.")
