#!/usr/bin/env python3
import subprocess
import os
import logging
from config_manager import Config

logger = logging.getLogger("RootGitHandler")

def setup_agent_identity(project_path):
    """
    [צופה פני עתיד] מוודא שלסוכן יש תעודת זהות ב-Git המקומי.
    מונע קריסות בסביבות ענן חדשות או בטרמוקס נקי.
    """
    try:
        subprocess.run(["git", "config", "user.name", "Root OS Agent"], cwd=project_path, check=False, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "config", "user.email", "root.os@agent.local"], cwd=project_path, check=False, stderr=subprocess.DEVNULL)
    except:
        pass

def get_current_branch(project_path):
    """
    [צופה פני עתיד] זיהוי דינמי של הבראנץ' הנוכחי.
    המפלצת עובדת איפה שהמשתמש עובד. אין Hardcoding ל-main.
    """
    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], 
            cwd=project_path, stderr=subprocess.DEVNULL
        ).decode().strip()
        return branch if branch else "main"
    except:
        return "main"

def get_authenticated_remote(project_path):
    """
    מזריק את ה-Token בצורה מאובטחת לנתיב ה-Push.
    מונע בקשות סיסמה שיתקעו את המערכת ברקע.
    """
    try:
        remote_url = subprocess.check_output(
            ["git", "remote", "get-url", "origin"], 
            cwd=project_path, stderr=subprocess.DEVNULL
        ).decode().strip()
        
        # אם יש טוקן והנתיב הוא של גיטהאב (HTTPS), מזריקים אותו
        if Config.GITHUB_TOKEN and remote_url.startswith("https://github.com"):
            clean_url = remote_url.replace("https://", "")
            return f"https://{Config.GITHUB_TOKEN}@{clean_url}"
        return "origin"
    except:
        return "origin"

def autonomous_push(project_path):
    """
    מבצע קומיט ופוש אוטונומי, עמיד בפני התנגשויות (Rebase) ודינמי לחלוטין.
    """
    # צופה פני עתיד: הוספנו גם את המניפסט של הדשבורד לסנכרון
    ROOT_DOCS = ["ROOT.md", "HISTORY.md", "ROADMAP.md", ".root_state_manifest.json"]
    
    try:
        setup_agent_identity(project_path)
        
        # 1. הוספת קבצי התיעוד הרלוונטיים בלבד
        added_something = False
        for doc in ROOT_DOCS:
            doc_path = os.path.join(project_path, doc)
            if os.path.exists(doc_path):
                subprocess.run(["git", "add", doc], cwd=project_path, check=True, stdout=subprocess.DEVNULL)
                added_something = True

        if not added_something:
            return

        # 2. האם יש משהו ממשי לעדכן?
        status = subprocess.check_output(["git", "status", "--porcelain"], cwd=project_path).decode()
        if not any(doc in status for doc in ROOT_DOCS):
            return

        # 3. יצירת קומיט של הסוכן
        commit_msg = "🌿 Root OS: Autonomous Memory & Docs Sync"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=project_path, check=True, stdout=subprocess.DEVNULL)

        branch = get_current_branch(project_path)
        auth_remote = get_authenticated_remote(project_path)

        # 4. [הגנה קריטית] משיכה עם Rebase לפני דחיפה
        # מונע שגיאות אם הענן התקדם מאז הפוש האחרון
        subprocess.run(["git", "pull", "--rebase", auth_remote, branch], cwd=project_path, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # 5. דחיפה מאובטחת וישירה
        subprocess.run(["git", "push", auth_remote, branch], cwd=project_path, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        print(f"🚀 [Root OS] סנכרון אוטונומי לבראנץ' '{branch}' הושלם בהצלחה.")

    except subprocess.CalledProcessError as e:
        # שגיאה שקטה ברקע כדי לא להפריע לזרימת העבודה של המשתמש
        logger.error(f"Git Handler Error: Failed to push autonomously. Code: {e.returncode}")
    except Exception as e:
        logger.error(f"Git Handler Critical Error: {e}")
