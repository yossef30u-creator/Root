#!/usr/bin/env python3
# =====
import os
import json
import subprocess
import requests
from datetime import datetime
from openai import OpenAI
from config import Config
from memory import RootMemory
# =====

# =====
# הגדרת נתיבי עבודה מדויקים
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_DIR)

# תיקון קריטי: מושכים מ-Config ולא מ-os.getenv כדי שה-.env ייקרא בטרמינל
GITHUB_TOKEN = Config.GITHUB_TOKEN
REPO_NAME = Config.GITHUB_REPOSITORY

# בדיקת תקינות (Debug)
if not GITHUB_TOKEN:
    print("❌ [Critical] GITHUB_TOKEN is missing in .env!")
if not REPO_NAME:
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
def update_history_log(critic_feedback, tasks_list):
    """(Future-Proof) מעדכן את קובץ ההיסטוריה בעיצוב נקי וקריא"""
    history_file = "HISTORY.md"
    now = datetime.now().strftime("%d/%m/%Y %H:%M") # פורמט קריא יותר
    
    # עיצוב משימות כרשימה מסודרת
    tasks_str = "\n".join([f"  - [ ] {t}" for t in tasks_list]) if tasks_list else "  - *לא הופקו משימות חדשות*"
    
    # ניקוי הביקורת אם היא 'PASS'
    critic_clean = critic_feedback if (critic_feedback and not critic_feedback.startswith("PASS")) else "הקוד תקין, אין הערות ארכיטקטוניות (PASS)."
    
    # יצירת רשומה בעיצוב "דשבורד"
    new_entry = (
        f"## 📅 {now}\n"
        f"**🔍 ניתוח וביקורת:**\n"
        f"> {critic_clean}\n\n"
        f"**🛠️ משימות לביצוע:**\n"
        f"{tasks_str}\n\n"
        f"---\n\n"
    )
    
    try:
        existing_content = ""
        if os.path.exists(history_file):
            with open(history_file, "r", encoding="utf-8") as f:
                existing_content = f.read()
                # הגבלה ל-50 רשומות למניעת ניפוח הקובץ
                if "## 📅" in existing_content:
                    entries = existing_content.split("## 📅")
                    if len(entries) > 50:
                        existing_content = "## 📅" + "## 📅".join(entries[1:51])

        with open(history_file, "w", encoding="utf-8") as f:
            if not existing_content or "# 📜 יומן ניתוחים היסטורי" not in existing_content:
                f.write("# 📜 יומן ניתוחים היסטורי - Root Agentic OS\n\n")
            
            clean_existing = existing_content.replace("# 📜 יומן ניתוחים היסטורי - Root Agentic OS\n\n", "")
            f.write(new_entry + clean_existing)
            
        print(f"✅ [History] Formatted entry added to {history_file}")
    except Exception as e:
        print(f"⚠️ [History] Failed to write history log: {e}")
# =====

# =====
def get_git_info():
    """שואב את פרטי הקומיט והשינויים מ-Git"""
    try:
        diff_result = subprocess.run(['git', 'diff', 'HEAD~1', 'HEAD'], capture_output=True, text=True)
        log_result = subprocess.run(['git', 'log', '-1', '--pretty=format:%h|%an|%s'], capture_output=True, text=True)
        
        diff_text = diff_result.stdout.strip()
        log_text = log_result.stdout.strip()
        
        if not diff_text:
            return None, None
            
        commit_hash, author, message = log_text.split('|', 2)
        metadata = {
            "commit": commit_hash,
            "author": author,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        return diff_text, metadata
    except Exception as e:
        print(f"❌ [Error] Git tracking failed: {e}")
        return None, None
# =====

# =====
def create_github_issue(title, body, labels=None):
    """יוצר Issue בגיטהאב. תומך בתוויות דינמיות למשימות שונות"""
    if not GITHUB_TOKEN or not REPO_NAME:
        print("⚠️ [GitHub API] Missing credentials, skipping issue creation.")
        return

    if labels is None:
        labels = ["root-critic", "automated"]

    url = f"https://api.github.com/repos/{REPO_NAME}/issues"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {"title": title, "body": body, "labels": labels}
    
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 201:
            print(f"📢 [Root] GitHub Issue created: {response.json().get('html_url')}")
        else:
            print(f"❌ [GitHub API] Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ [GitHub API] Connection error: {e}")
# =====

# =====
def analyze_diff(diff_text):
    """(Synthesis) מנתח את ההשפעה הארכיטקטונית - עם דגש על מבנה נקודות"""
    if len(diff_text) > 40000:
        diff_text = diff_text[:40000] + "\n\n[... Diff truncated ...]"

    print(f"[Root] Analyzing semantic impact...")
    target_lang = getattr(Config, 'UI_LANGUAGE', 'English')
    
    # הוספת הנחיה למבנה של נקודות (Bullet Points)
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
    """(Critic) מבקר את הקוד - עם דגש על מבנה נקודות"""
    if len(diff_text) > 40000:
        diff_text = diff_text[:40000] + "\n\n[... Diff truncated ...]"

    print(f"[Root Critic] Reviewing quality...")
    target_lang = getattr(Config, 'UI_LANGUAGE', 'English')
    
    context_instruction = f"\nContext:\n{past_context}" if past_context else ""

    # הנחיה לשימוש בנקודות בביקורת
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
def update_manifest(analysis, critic_feedback=None):
    """מעדכן את ROOT.md בעיצוב דשבורד מקצועי"""
    if os.path.exists(Config.MANIFEST_PATH):
        with open(Config.MANIFEST_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        new_lines = []
        now_str = datetime.now().strftime('%d/%m/%Y %H:%M')
        
        for line in lines:
            if line.startswith("> **Status:**"):
                new_lines.append(f"> **Status:** 🟢 מעודכן ל-{now_str}\n")
                new_lines.append(f"> \n")
                new_lines.append(f"> **ניתוח אחרון:**\n")
                # פירוק הטקסט לנקודות בצורה חכמה
                for part in analysis.split('\n'):
                    if part.strip():
                        prefix = "" if part.strip().startswith(('*', '-', '>')) else "* "
                        new_lines.append(f"> {prefix}{part.strip()}\n")
                
                if critic_feedback and not critic_feedback.startswith("PASS"):
                    new_lines.append(f"> \n")
                    new_lines.append(f"> **⚠️ התראת ארכיטקט (Critic):**\n")
                    for part in critic_feedback.split('\n'):
                        if part.strip():
                            prefix = "" if part.strip().startswith(('*', '-', '>')) else "* "
                            new_lines.append(f"> {prefix}{part.strip()}\n")
                new_lines.append(f">\n")
            elif line.startswith("> **Critic Alert:**"):
                continue # הכל כבר נכנס תחת Status בגרסה החדשה
            else:
                new_lines.append(line)

        with open(Config.MANIFEST_PATH, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print("✅ [Root] ROOT.md updated with Dashboard format.")
# =====

# =====
def propose_improvements(root_memory):
    """(Proactive) סורק את המערכת ומציע שיפורים עתידיים כ-Issues בגיטהאב"""
    print("[Root Proactive] Brainstorming future improvements...")
    target_lang = getattr(Config, 'UI_LANGUAGE', 'English')
    proposed_titles = []
    
    try:
        context_results = root_memory.search_memory("project architecture constraints roadmap features", top_k=5)
        context = ""
        
        if context_results:
            for item in context_results:
                if isinstance(item, tuple) and len(item) == 2:
                    context += f"- {item[1].get('text', '')}\n"

        prompt = f"""Based on context: {context}
        Suggest 1-2 technical improvements. Return JSON object with 'tasks' (array of 'title' and 'description').
        Write in {target_lang}."""

        response = client.chat.completions.create(
            model=Config.MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content.strip())
        tasks = result.get("tasks", [])
        
        for task in tasks:
            title = task.get('title')
            proposed_titles.append(title)
            create_github_issue(
                title=f"🤖 Root Suggestion: {title}",
                body=task.get('description') + "\n\n---\n*Proactively generated by Root OS.*",
                labels=["root-task", "automated-suggestion"]
            )
            
        return proposed_titles
    except Exception as e:
        print(f"⚠️ [Root Proactive] Failed: {e}")
        return proposed_titles
# =====

# =====
if __name__ == "__main__":
    # התנעה עצמית ליומן
    if not os.path.exists("HISTORY.md"):
        print("[History] Initializing HISTORY.md...")
        update_history_log("אתחול מערכת ראשוני.", [])

    diff, metadata = get_git_info()
    
    if diff:
        root_memory = RootMemory()
        
        print("[Root] Searching long-term memory...")
        past_context = ""
        try:
            search_results = root_memory.search_memory(query=diff, top_k=2)
            if search_results:
                past_context = "\n".join([item[1]["text"] for item in search_results if isinstance(item, tuple)])
        except Exception as e:
            print(f"⚠️ [Memory] Failed: {e}")

        analysis = analyze_diff(diff)
        critic_feedback = run_critic(diff, past_context)
        
        if critic_feedback and not critic_feedback.startswith("PASS"):
            issue_title = f"Root Critic Alert: Review Needed on Commit {metadata['commit']}"
            issue_body = f"### Agent Feedback:\n{critic_feedback}\n\n**Commit Message:** {metadata['message']}"
            create_github_issue(issue_title, issue_body)
        
        if analysis:
            update_manifest(analysis, critic_feedback)
            root_memory.add_memory(text=f"Analysis: {analysis}\nCritic: {critic_feedback}", metadata=metadata)
            
            print("✅ [Root] Continuous Context Loop Completed.")
            
            # הרצת מערכת המשימות והיומן המעוצב
            proposed_tasks = propose_improvements(root_memory)
            update_history_log(critic_feedback, proposed_tasks)
        else:
            print("⚠️ [Root] Update aborted due to API error.")
    else:
        print("ℹ️ [Root] No structural changes found.")
# =====
