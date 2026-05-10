#!/usr/bin/env python3
import os
import json
import time
from openai import OpenAI
from dotenv import load_dotenv

# אתחול נתיבים וטעינת ה-.env ישירות כדי למנוע תלות בקבצים חיצוניים שעשויים להשתנות
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

# אתחול הלקוח של OpenRouter - מחובר לחשבון שלך
client = OpenAI(
    base_url=os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1"),
    api_key=os.getenv("OPENAI_API_KEY"),
    default_headers={"HTTP-Referer": "https://github.com/RootProject", "X-Title": "Root Agentic OS"}
)

def execute_task_logic(task_title, model=None):
    """
    הלוגיקה האוטונומית: מנחה את ה-LLM לכתוב קוד עבור המשימה ולייצר קובץ.
    מקבלת את המודל הנבחר (model) ישירות ממוח הדשבורד!
    """
    # אם לא נשלח מודל מהדשבורד, הוא ייקח את ברירת המחדל מה-.env
    target_model = model if model else os.getenv("MODEL", "anthropic/claude-3.5-sonnet")
    
    print(f"🤖 [Agent Coder] מקמפל מחשבות עבור המשימה: '{task_title}'")
    print(f"🧠 משתמש באינטליגנציה: {target_model}")
    
    prompt = f"""
    You are the Root Agentic OS, an autonomous AI developer.
    The user has approved the following task from the roadmap: "{task_title}".
    
    Your job is to generate the working code to fulfill this task.
    Return your response STRICTLY as a JSON object with no additional markdown formatting outside the JSON block.
    The JSON must contain two keys:
    1. "file_path": The path where the file should be saved (e.g., "core/new_feature.py" or "src/utils.py").
    2. "content": The actual code to be written into that file.
    
    Make the code robust, fully functional, and ready to run.
    """
    
    try:
        response = client.chat.completions.create(
            model=target_model,  # כאן מוזרק המודל הדינמי!
            messages=[
                {"role": "system", "content": "You are a machine that outputs strict JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"} 
        )
        
        # פענוח התשובה
        response_text = response.choices[0].message.content.strip()
        result = json.loads(response_text)
        
        file_path = result.get("file_path", f"auto_generated_{int(time.time())}.py")
        content = result.get("content", "")
        
        # אבטחה: וידוא שהנתיב יחסי לתיקיית הפרויקט ולא דורס קבצי מערכת חיצוניים (מעולה!)
        full_path = os.path.abspath(os.path.join(PROJECT_ROOT, file_path))
        if not full_path.startswith(PROJECT_ROOT):
            raise Exception("Security Error: Agent tried to write outside the project directory.")
            
        # יצירת התיקיות אם הן לא קיימות
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # כתיבת הקוד לקובץ הפיזי
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        print(f"✅ [Agent Coder] הקוד נכתב בהצלחה לקובץ: {file_path}")
        return True, file_path
        
    except json.JSONDecodeError:
        print(f"❌ [Agent Coder] הסוכן לא החזיר JSON תקין. התשובה הגולמית:\n{response_text}")
        return False, "Agent returned invalid JSON format."
    except Exception as e:
        print(f"❌ [Agent Coder] שגיאה בכתיבת הקוד: {e}")
        return False, str(e)
