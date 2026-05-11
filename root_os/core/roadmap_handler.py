#!/usr/bin/env python3
# =====
import os
import json
import requests
import subprocess
from datetime import datetime
from openai import OpenAI
from config_manager import Config

# =====
def get_current_repo():
    """שולף את שם המאגר מהתיקייה הנוכחית"""
    try:
        url = subprocess.check_output(
            ['git', 'remote', 'get-url', 'origin'], 
            stderr=subprocess.DEVNULL
        ).decode().strip()
        if "github.com/" in url:
            return url.split("github.com/")[-1].replace(".git", "")
    except:
        return None
    return None

# =====
def create_github_issue(title, body, labels=None):
    """יוצר Issue בגיטהאב למשימות דחופות"""
    repo = get_current_repo()
    if not Config.GITHUB_TOKEN or not repo:
        return

    if labels is None:
        labels = ["root-task", "automated"]

    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {
        "Authorization": f"token {Config.GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {"title": title, "body": body, "labels": labels}
    
    try:
        requests.post(url, json=data, headers=headers)
    except:
        pass

# =====
def agentic_roadmap_sync(analysis, critic_feedback):
    """
    (מנהל המוצר - The Strategist)
    קורא את ה-Roadmap הקיים, מסנן החוצה משימות שבוצעו בקוד החדש,
    ומעדכן סדרי עדיפויות וחוב טכני. 
    """
    roadmap_file = getattr(Config, 'ROADMAP_PATH', 'ROADMAP.md')
    
    # 1. קריאת ה-Roadmap הקיים
    current_roadmap = ""
    if os.path.exists(roadmap_file):
        with open(roadmap_file, "r", encoding="utf-8") as f:
            current_roadmap = f.read()

    # אתחול מול ה-AI
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key: return []
    client = OpenAI(base_url=os.environ.get("BASE_URL"), api_key=api_key)

    # 2. חוקי הברזל למנהל המוצר
    system_prompt = """
    You are the 'Strategic Product Manager Agent' for Root OS.
    Your job is to rewrite the ROADMAP.md file based on the latest code changes.
    
    CRITICAL RULES:
    1. META-INSTRUCTION: Start the document with:
       "> **הוראת מערכת:** אלו הפעולות העתידיות. משימות שבוצעו נמחקו מכאן ועברו ל-HISTORY."
    2. REMOVE DONE TASKS: If the 'Latest Changes' show that a task from the 'Current Roadmap' is completed, DELETE IT from the new roadmap. Do not strike it out. Remove it.
    3. ADD TECH DEBT: If the 'Critic Feedback' mentions bugs, messy code, or vulnerabilities, ADD them as high-priority tasks in a "Technical Debt" section.
    4. REQUIRED STRUCTURE:
       - 🚨 צווארי בקבוק וחוב טכני (Urgent Fixes)
       - 🚧 הנתיב הקריטי (Critical Path - Next immediate steps)
       - 💡 בקלוג רעיונות (Future Backlog)
       
    Output ONLY valid Markdown.
    """

    user_prompt = f"""
    --- Current ROADMAP.md ---
    {current_roadmap if current_roadmap else "Empty (New Project)."}
    
    --- Latest Changes (Tasks that might be completed now) ---
    {analysis}
    
    --- Critic Feedback (New technical debt to add) ---
    {critic_feedback if critic_feedback else "No new technical debt."}
    """

    print(f"🗺️ [Root PM] Syncing roadmap: removing done tasks, prioritizing debt...")

    try:
        response = client.chat.completions.create(
            model=os.environ.get("MODEL", "google/gemini-pro-1.5"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        new_roadmap = response.choices[0].message.content.strip()

        # ניקוי פורמט
        if new_roadmap.startswith("
http://googleusercontent.com/immersive_entry_chip/0
http://googleusercontent.com/immersive_entry_chip/1

**נראה לך נכון? זה משאיר לנו רק את ה-`history_handler.py` (המוח הזוכר, הארכיון), שם נגדיר שהוא פשוט בולע הכל כרונולוגית ולא מוחק כלום.**
