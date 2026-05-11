#!/usr/bin/env python3
# =====
import os
import sys
import json
import subprocess
import fnmatch # נוסף עבור מנגנון הסינון
from datetime import datetime
import atexit # נוסף נטו כדי לשחרר את הנעילה בסוף בלי להזיז קוד

# ==========================================
# מנגנון נעילה (Concurrency Lock)
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
                    print(f"⏳ [Root Ingestor] המערכת עובדת כרגע (PID {old_pid}). ממתין לתור הבא.")
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
            except OSError:
                pass

    def _is_pid_running(self, pid):
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False
# ==========================================

# ==========================================
# 1. הגדרת סביבת עבודה דינמית (Cross-Platform)
# ==========================================
if len(sys.argv) < 2:
    print("❌ [Critical] Project path missing! Run via boot.py or root_service.py.")
    sys.exit(1)

PROJECT_DIR = sys.argv[1]

# --- הפעלת הנעילה ---
LOCK = RootLock(PROJECT_DIR)
if not LOCK.acquire():
    sys.exit(0)
atexit.register(LOCK.release) # מבטיח את שחרור הנעילה בסיום הריצה באופן אוטומטי
# --------------------

os.chdir(PROJECT_DIR) # מעבר לתיקיית הפרויקט שעליו אנחנו עובדים כרגע

# הוספת תיקיית core לנתיב כדי שנוכל לייבא את המודולים שלנו מכל מקום
CORE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CORE_DIR)

# נתיב לקובץ הנתונים שיוצג בדשבורד (נשמר באופן נסתר בתוך הפרויקט עצמו)
RAW_DATA_FILE = os.path.join(PROJECT_DIR, ".root_core_dump.json")

# ==========================================
# 2. טעינת קונפיגורציה גלובלית
# ==========================================
CONFIG_PATH = os.path.expanduser("~/.root_config")
try:
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
        # הזרקת הנתונים למשתני סביבה כדי שהמודולים הקיימים ימשיכו לעבוד
        os.environ["OPENAI_API_KEY"] = config_data.get("API_KEY", "")
        os.environ["GITHUB_TOKEN"] = config_data.get("GITHUB_TOKEN", "")
        os.environ["BASE_URL"] = config_data.get("BASE_URL", "https://openrouter.ai/api/v1")
        os.environ["MODEL"] = config_data.get("MODEL", "google/gemini-pro-1.5")
except Exception as e:
    print(f"❌ [Critical Error] Failed to load global config at {CONFIG_PATH}: {e}")
    sys.exit(1)

if not os.environ["OPENAI_API_KEY"]:
    print("❌ [Critical Error] API Key missing! Please run root boot setup.")
    sys.exit(1)

# ==========================================
# 3. ייבוא מודולים אחרי עדכון משתני הסביבה
# ==========================================
from openai import OpenAI
from config import Config
from memory import RootMemory

# --- חיבור לשלישיית הסוכנים האוטונומיים ---
from root_handler import update_manifest
from git_handler import autonomous_push
from history_handler import agentic_history_sync
from roadmap_handler import agentic_roadmap_sync, create_github_issue

# אתחול הלקוח של OpenAI
client = OpenAI(
    base_url=os.environ["BASE_URL"],
    api_key=os.environ["OPENAI_API_KEY"],
    default_headers={
        "HTTP-Referer": "https://github.com/RootProject",
        "X-Title": "Root Agentic OS",
    }
)
# =====

# =====
# --- תוספת מנגנון הסינון (.rootignore) ---
DEFAULT_IGNORE = [
    'node_modules/*', '.git/*', 'venv/*', '__pycache__/*', 
    '*.pyc', '*.exe', '*.dll', '*.so', '*.dat', '*.lock',
    'package-lock.json', 'yarn.lock', '.DS_Store'
]

def load_rootignore():
    """טוען חוקי סינון נוספים מקובץ חיצוני אם קיים"""
    ignore_patterns = DEFAULT_IGNORE.copy()
    if os.path.exists(".rootignore"):
        with open(".rootignore", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    ignore_patterns.append(line)
    return ignore_patterns

def is_ignored(file_path, patterns):
    """בודק אם קובץ מסוים אמור להיות מסונן מהניתוח"""
    for pattern in patterns:
        if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(os.path.basename(file_path), pattern):
            return True
    return False
# ------------------------------------------
# =====

# =====
def get_git_info():
    """
    שואב את פרטי הקומיט והשינויים מ-Git.
    מזהה אוטומטית אם אנחנו במצב לייב (לפני פוש) או מצב סופי (אחרי קומיט).
    משתמש במנגנון rootignore כדי לסנן קבצים כבדים או לא רלוונטיים.
    """
    try:
        ignore_patterns = load_rootignore()
        
        # --- טיפול במצב LIVE ---
        files_live = subprocess.run(['git', 'diff', '--name-only', 'HEAD'], capture_output=True, text=True).stdout.splitlines()
        valid_live_files = [f for f in files_live if not is_ignored(f, ignore_patterns)]
        
        if valid_live_files:
            diff_cmd = ['git', 'diff', 'HEAD', '--'] + valid_live_files
            diff_live = subprocess.run(diff_cmd, capture_output=True, text=True).stdout.strip()
            if diff_live:
                return diff_live, None, "LIVE"
                
        # --- טיפול במצב FINAL ---
        files_final = subprocess.run(['git', 'diff', '--name-only', 'HEAD~1', 'HEAD'], capture_output=True, text=True).stdout.splitlines()
        valid_final_files = [f for f in files_final if not is_ignored(f, ignore_patterns)]
        
        if not valid_final_files:
             return None, None, "NONE"
             
        diff_cmd_final = ['git', 'diff', 'HEAD~1', 'HEAD', '--'] + valid_final_files
        diff_final = subprocess.run(diff_cmd_final, capture_output=True, text=True).stdout.strip()
        
        if not diff_final:
             return None, None, "NONE"

        log_text = subprocess.run(['git', 'log', '-1', '--pretty=format:%h|%an|%s'], capture_output=True, text=True).stdout.strip()
        commit_hash, author, message = log_text.split('|', 2)
        metadata = {
            "commit": commit_hash,
            "author": author,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        return diff_final, metadata, "FINAL"
    except Exception as e:
        print(f"❌ [Error] Git tracking failed: {e}")
        return None, None, "ERROR"
# =====

# =====
def analyze_diff(diff_text):
    if len(diff_text) > 40000:
        diff_text = diff_text[:40000] + "\n\n[... Diff truncated ...]"

    print(f"[Root] Analyzing semantic impact...")
    target_lang = getattr(Config, 'UI_LANGUAGE', 'English')
    
    prompt = f"Analyze this code diff and provide a short summary in {target_lang}. Use bullet points for different points of impact if possible:\n\n{diff_text}"
    
    try:
        response = client.chat.completions.create(
            model=os.environ["MODEL"],
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ [API Error]: {e}")
        return None
# =====

# =====
def run_critic(diff_text, past_context=""):
    if len(diff_text) > 40000:
        diff_text = diff_text[:40000] + "\n\n[... Diff truncated ...]"

    print(f"[Root Critic] Reviewing quality...")
    target_lang = getattr(Config, 'UI_LANGUAGE', 'English')
    context_instruction = f"\nContext:\n{past_context}" if past_context else ""

    critic_prompt = f"As the Root Critic, analyze this code diff. If okay, output ONLY 'PASS'. Otherwise, report issues using bullet points in {target_lang}.{context_instruction}\n\nDiff:\n{diff_text}"
    
    try:
        response = client.chat.completions.create(
            model=os.environ["MODEL"],
            messages=[
                {"role": "system", "content": "You are the Root Critic. Be sharp and use bullet points for clarity."},
                {"role": "user", "content": critic_prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ [API Error]: {e}")
        return None
# =====

# =====
def export_core_dump(run_mode, analysis, critic_feedback):
    """
    (הגשר לדשבורד)
    זורק את תוצאות הניתוח לקובץ גולמי בתיקיית הפרויקט (מוסתר).
    הדשבורד פשוט יקרא את הקובץ הזה.
    """
    try:
        payload = {
            "timestamp": datetime.now().isoformat(),
            "mode": run_mode,
            "analysis": analysis,
            "critic": critic_feedback
        }
        with open(RAW_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=4)
        print("📦 [File Brain] Raw data dumped for Dashboard Brain.")
    except Exception as e:
        print(f"⚠️ [File Brain] Failed to dump data to dashboard: {e}")
# =====

# =====
if __name__ == "__main__":
    # יצירת קובץ HISTORY במידה ולא קיים, עם ה-Header החדש שאוסר מחיקות
    if not os.path.exists("HISTORY.md"):
        print("[History] Initializing HISTORY.md...")
        with open("HISTORY.md", "w", encoding="utf-8") as f:
            f.write("# 📜 יומן החלטות היסטורי - Root OS\n\n> **הוראת מערכת:** זהו יומן ההחלטות הכרונולוגי. פה נמצא ה'למה'. אסור למחוק מכאן מידע.\n\n---\n")

    diff, metadata, run_mode = get_git_info()
    
    if diff and run_mode in ["LIVE", "FINAL"]:
        root_memory = RootMemory()
        
        print(f"[Root] Detected Mode: {run_mode} | Searching long-term memory...")
        past_context = ""
        try:
            search_results = root_memory.search_memory(query=diff, top_k=2)
            if search_results:
                past_context = "\n".join([item[1]["text"] for item in search_results if isinstance(item, tuple)])
        except Exception as e:
            print(f"⚠️ [Memory] Failed: {e}")

        analysis = analyze_diff(diff)
        critic_feedback = run_critic(diff, past_context)
        
        # זיהוי שגיאות חמורות ופתיחת Issue בגיטהאב
        if run_mode == "FINAL" and critic_feedback and not critic_feedback.startswith("PASS"):
            issue_title = f"Root Critic Alert: Review Needed on Commit {metadata['commit']}"
            issue_body = f"### Agent Feedback:\n{critic_feedback}\n\n**Commit Message:** {metadata['message']}"
            create_github_issue(issue_title, issue_body)
        
        if analysis:
            print(f"🚀 [Root] Initiating Architecture Update (Mode: {run_mode})...")
            
            # 1. מפעילים את האדריכל - כותב את תמונת המצב הנוכחית של הפרויקט
            update_manifest(analysis, critic_feedback)
            
            if run_mode == "FINAL":
                # 2. מפעילים את האסטרטג - מנקה משימות ישנות ודוחף חוב טכני
                agentic_roadmap_sync(analysis, critic_feedback)
                
                # 3. מפעילים את הארכיונאי - כותב ביומן הכרונולוגי את ה'למה' של ההחלטה
                agentic_history_sync(analysis, critic_feedback)
                
                # 4. הכנסת הזיכרון למוח הוקטורי (ChromaDB)
                root_memory.add_memory(text=f"Analysis: {analysis}\nCritic: {critic_feedback}", metadata=metadata)
                
                print("✅ [Root] Continuous Context Loop Completed (FINAL).")
                
                # 5. דחיפה אוטונומית לענן דרך המפלצת
                print("🌐 [Root] Pushing documentation to cloud...")
                autonomous_push(PROJECT_DIR)
                
            else:
                print("⚡ [Root] Live Mode cycle completed.")
                
            # שליחת הנתונים למוח הדשבורד בסיום התהליך
            export_core_dump(run_mode, analysis, critic_feedback)
                
        else:
            print("⚠️ [Root] Update aborted due to API error.")
    else:
        print("ℹ️ [Root] No structural changes found.")
# =====