#!/usr/bin/env python3
import os
import subprocess
from openai import OpenAI
from config import Config

# חשוב לטרמוקס: מוודא שהסקריפט תמיד ירוץ מתוך תיקיית הפרויקט, גם אם קראת לו מתיקייה אחרת
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_DIR)

# הגדרת הלקוח
client = OpenAI(
    base_url=Config.BASE_URL,
    api_key=Config.OPENAI_API_KEY,
)

def get_git_diff():
    try:
        result = subprocess.run(['git', 'diff', 'HEAD~1', 'HEAD'], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        print(f"❌ [Error] Git diff failed: {e}")
        return ""

def analyze_diff(diff_text):
    if not diff_text.strip(): return None
    
    print(f"[Root] Analyzing impact with {Config.MODEL}...")
    prompt = f"Analyze this code diff and provide a short, 1-2 sentence summary of its impact on the project architecture:\n\n{diff_text}"
    
    try:
        response = client.chat.completions.create(
            model=Config.MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        # התוספת הקריטית: במקום להחזיר את השגיאה כטקסט, אנחנו מדפיסים אותה ומחזירים None
        print(f"❌ [API Error]: Failed to contact Semantic Engine. Details: {e}")
        return None

def update_files(analysis):
    # 1. עדכון הלוגים (הוספה רגילה)
    os.makedirs(os.path.dirname(Config.LOG_PATH), exist_ok=True)
    with open(Config.LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"\n## New Context Update\n{analysis}\n")
    
    # 2. עדכון ה-Manifest (ROOT.md) - החלפה חכמה של הסטטוס
    if os.path.exists(Config.MANIFEST_PATH):
        with open(Config.MANIFEST_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        with open(Config.MANIFEST_PATH, "w", encoding="utf-8") as f:
            for line in lines:
                if line.startswith("> **Status:**"):
                    # מסיר ירידות שורה מהניתוח כדי לשמור על פורמט נקי
                    clean_analysis = analysis.replace('\n', ' ').strip()
                    f.write(f"> **Status:** Last Update - {clean_analysis[:150]}...\n")
                else:
                    f.write(line)

if __name__ == "__main__":
    diff = get_git_diff()
    if diff:
        analysis = analyze_diff(diff)
        
        # מוודא שיש ניתוח אמיתי לפני שנוגעים בקבצים
        if analysis:
            update_files(analysis)
            print("✅ [Root] Context Updated Successfully in logs and ROOT.md.")
        else:
            print("⚠️ [Root] Update aborted due to API error. Files were not changed.")
    else:
        print("ℹ️ [Root] No changes found. Commit some files first.")
