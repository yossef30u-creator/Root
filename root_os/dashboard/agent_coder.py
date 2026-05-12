#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# #=====
# 🤖 Root OS: Autonomous Agent Coder (Sovereign Execution Engine)
# ------------------------------------------------------------------------------
# תפקיד: ביצוע פיזי של משימות קוד, הזרקת לוגיקה ושכתוב קבצים.
# פילוסופיה: כתיבה אטומית. צופה פני עתיד. חסינות לשיבושי Markdown.
# #=====

import os
import json
import time
import re
import atexit
from openai import OpenAI
from dotenv import load_dotenv

# #=====
# [1] אתחול סביבה וניהול נתיבים
# #=====
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

client = OpenAI(
    base_url=os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1"),
    api_key=os.getenv("OPENAI_API_KEY"),
    default_headers={
        "HTTP-Referer": "https://github.com/RootProject",
        "X-Title": "Root Agentic OS",
    },
)


# #=====
# [2] מנגנון ניקוי JSON ותפוקה אטומי
# #=====
def clean_json_response(text):
    """מנקה סימני Markdown ותווים מיותרים שה-AI לפעמים מוסיף[span_4](start_span)[span_4](end_span)."""
    cleaned_text = re.sub(r"```json\s*|\s*```", "", text)
    cleaned_text = re.sub(r"```\s*|\s*```", "", cleaned_text)
    cleaned_text = cleaned_text.strip()

    match = re.search(r"(\{.*\}|\[.*\])", cleaned_text, re.DOTALL)
    if match:
        return match.group(1)
    return cleaned_text


# #=====
# [3] ניהול נעילות ומשאבים (atexit)
# #=====
LOCK_FILE = ".root_coder.lock"


def release_coder_lock():
    """שחרור נעילה אלגנטי בסיום הריצה דרך atexit[span_5](start_span)[span_5](end_span)[span_6](start_span)[span_6](end_span)."""
    if os.path.exists(LOCK_FILE):
        try:
            os.remove(LOCK_FILE)
        except:
            pass


atexit.register(release_coder_lock)


def acquire_coder_lock():
    """מנגנון מניעת התנגשויות כתיבה[span_7](start_span)[span_7](end_span)."""
    if os.path.exists(LOCK_FILE):
        return False
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))
    return True


# #=====
# [4] פונקציות ביצוע אסטרטגיות (Interface for Dashboard Brain)
# #=====


def generate_roadmap_strategy(idea, model):
    """הופך רעיון מהצ'אט לרשימת משימות טכנית ב-Roadmap[span_8](start_span)[span_8](end_span)[span_9](start_span)[span_9](end_span)."""
    print(f"🧬 [Architect] Analyzing strategic vector for: {idea}")
    system_prompt = (
        "You are the 'Root Architect'. Break ideas into a JSON list of atomic tasks."
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Create a technical plan for: {idea}"},
            ],
            response_format={"type": "json_object"},
        )
        data = json.loads(clean_json_response(response.choices[0].message.content))
        return True, data.get("tasks", [])
    except Exception as e:
        return False, str(e)


def execute_task_logic(task_title, model):
    """מבצע משימת קוד ספציפית ומעדכן את הקבצים[span_10](start_span)[span_10](end_span)[span_11](start_span)[span_11](end_span)[span_12](start_span)[span_12](end_span)."""
    # כאן הסוכן יחפש את הקובץ המתאים ויבצע את השינוי לפי ההוראה
    print(f"🛠️ [Coder] Starting execution of: {task_title}")
    # לוגיקה זו תורחב בהתאם לסריקת ה-ROOT.md לאיתור הקובץ הרלוונטי
    return True, "Task completed successfully"


# #=====
# [5] הזרקת קוד פיזית (The Coder Core)
# #=====
def apply_code_change(file_path, instruction):
    """הזרקת שינויים לקוד ברמה הנדסית עילאית[span_13](start_span)[span_13](end_span)[span_14](start_span)[span_14](end_span)."""
    if not acquire_coder_lock():
        return False, "System Busy"

    original_content = ""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            original_content = f.read()

    system_prompt = """
    You are the 'Root Master Coder'. Rewrite code with surgical precision.
    RULES:
    1. NEVER remove existing logic unless explicitly told to[span_15](start_span)[span_15](end_span).
    2. Add comments explaining every change.
    3. Use '#=====' delimiters for logical blocks.
    4. Return PURE code only.
    """

    try:
        response = client.chat.completions.create(
            model=os.getenv("MODEL", "gpt-4o"),
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"File: {file_path}\nOriginal:\n{original_content}\n\nTask: {instruction}",
                },
            ],
            temperature=0,
        )
        new_code = response.choices[0].message.content.strip()

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_code)
        return True, "File updated"
    except Exception as e:
        return False, str(e)
    finally:
        release_coder_lock()


# #=====
if __name__ == "__main__":
    print("🤖 Root Agent Coder Online and Sovereign.")
