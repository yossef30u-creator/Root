#!/usr/bin/env python3
# =====
import os
import json
import subprocess
from datetime import datetime
from openai import OpenAI
from config import Config
from memory import RootMemory

# 🧩 ייבוא המודולים החדשים שלנו
from root_handler import update_manifest
from history_handler import update_history_log
from roadmap_handler import propose_improvements, update_roadmap, create_github_issue
# =====

# =====
# הגדרת נתיבי עבודה מדויקים
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_DIR)

# נתיב לתיקיית הדשבורד (לשם נזרוק את הנתונים הגולמיים)
DASHBOARD_DIR = os.path.abspath(os.path.join(PROJECT_DIR, "..", "dashboard"))
RAW_DATA_FILE = os.path.join(DASHBOARD_DIR, "core_dump.json")

# בדיקת תקינות (Debug)
if not Config.GITHUB_TOKEN:
    print("❌ [Critical] GITHUB_TOKEN is missing in .env!")
if not Config.GITHUB_REPOSITORY:
    print("❌ [Critical] GITHUB_REPOSITORY is missing in .env!")
if not Config.OPENAI_API_KEY:
    print("❌ [Critical Error] API Key missing! Check your .env file.")
    exit(1)
# =====

# =====
# אתחול הלקוח של OpenAI לתהליך הניתוח הסמנטי
client = OpenAI(
    base_url=Config.BASE_URL,
    api_key=Config.OPENAI_API_KEY,
    default_headers={
        "HTTP-Referer": "https://github.com/RootProject",
        "X-Title": "Root Agentic OS",
    }
)
# =====

# =====
def get_git_info():
    """
    שואב את פרטי הקומיט והשינויים מ-Git.
    מזהה אוטומטית אם אנחנו במצב לייב (לפני פוש) או מצב סופי (אחרי קומיט).
    """
    try:
        diff_live = subprocess.run(['git', 'diff', 'HEAD'], capture_output=True, text=True).stdout.strip()
        if diff_live:
            return diff_live, None, "LIVE"
            
        diff_final = subprocess.run(['git', 'diff', 'HEAD~1', 'HEAD'], capture_output=True, text=True).stdout.strip()
        log_text = subprocess.run(['git', 'log', '-1', '--pretty=format:%h|%an|%s'], capture_output=True, text=True).stdout.strip()
        
        if not diff_final:
            return None, None, "NONE"
            
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
            model=Config.MODEL,
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
            model=Config.MODEL,
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
def export_core_dump(run_mode, analysis, critic_feedback, proposed_tasks=None):
    """
    (הגשר לדשבורד)
    זורק את תוצאות הניתוח לקובץ גולמי בתיקיית הדשבורד.
    הוא לא יודע מה זה UI, הוא פשוט מעביר את המידע הלאה.
    """
    try:
        if not os.path.exists(DASHBOARD_DIR):
            os.makedirs(DASHBOARD_DIR, exist_ok=True)
            
        payload = {
            "timestamp": datetime.now().isoformat(),
            "mode": run_mode,
            "analysis": analysis,
            "critic": critic_feedback,
            "proposed_tasks": proposed_tasks or []
        }
        with open(RAW_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=4)
        print("📦 [File Brain] Raw data dumped for Dashboard Brain.")
    except Exception as e:
        print(f"⚠️ [File Brain] Failed to dump data to dashboard: {e}")
# =====

# =====
if __name__ == "__main__":
    if not os.path.exists("HISTORY.md"):
        print("[History] Initializing HISTORY.md...")
        update_history_log("אתחול מערכת ראשוני.", [])

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
        proposed_tasks = None
        
        if run_mode == "FINAL" and critic_feedback and not critic_feedback.startswith("PASS"):
            issue_title = f"Root Critic Alert: Review Needed on Commit {metadata['commit']}"
            issue_body = f"### Agent Feedback:\n{critic_feedback}\n\n**Commit Message:** {metadata['message']}"
            create_github_issue(issue_title, issue_body)
        
        if analysis:
            print(f"🚀 [Root] Initiating Architecture Update (Mode: {run_mode})...")
            
            update_manifest(analysis, critic_feedback)
            
            if run_mode == "FINAL":
                proposed_tasks = propose_improvements(root_memory)
                if proposed_tasks:
                    update_roadmap(proposed_tasks)
                
                update_history_log(critic_feedback, proposed_tasks)
                root_memory.add_memory(text=f"Analysis: {analysis}\nCritic: {critic_feedback}", metadata=metadata)
                
                print("✅ [Root] Continuous Context Loop Completed (FINAL).")
            else:
                print("⚡ [Root] Live Mode cycle completed.")
                
            # שליחת הנתונים למוח הדשבורד בסיום התהליך
            export_core_dump(run_mode, analysis, critic_feedback, proposed_tasks)
                
        else:
            print("⚠️ [Root] Update aborted due to API error.")
    else:
        print("ℹ️ [Root] No structural changes found.")
# =====
