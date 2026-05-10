#!/usr/bin/env python3
import os
import sys
import subprocess
import venv

# --- הגדרות התקנה ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
REQUIRED_DIRS = ["core", "dashboard"]
REQUIRED_PACKAGES = [
    "watchdog",      # חיישן הקבצים
    "openai",        # מוח ה-AI
    "flask",         # שרת הדשבורד
    "flask-cors",    # חיבור לדשבורד מכל מקום
    "python-dotenv"  # ניהול משתני סביבה
]

def print_step(msg):
    print(f"\n⚙️  [Setup] {msg}")

def check_python_version():
    """מוודא שהמשתמש מריץ גרסת פייתון עדכנית"""
    print_step("בודק גרסת Python...")
    if sys.version_info < (3, 8):
        print("❌ שגיאה: Root OS דורש Python 3.8 ומעלה.")
        sys.exit(1)
    print("✅ גרסת Python תקינה.")

def create_directories():
    """מקים את מבנה התיקיות הנדרש"""
    print_step("מוודא שמבנה התיקיות קיים...")
    for d in REQUIRED_DIRS:
        dir_path = os.path.join(PROJECT_ROOT, d)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"📁 נוצרה תיקייה: {d}/")
        else:
            print(f"✔️ תיקיית {d}/ כבר קיימת.")

def install_dependencies():
    """מתקין את כל הספריות הנדרשות ישירות לסביבה"""
    print_step("מתקין חבילות ותלויות (זה עשוי לקחת דקה)...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], stdout=subprocess.DEVNULL)
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + REQUIRED_PACKAGES)
        print("✅ כל החבילות הותקנו בהצלחה.")
    except Exception as e:
        print(f"❌ שגיאה בהתקנת חבילות: {e}")
        print("💡 נסה להריץ: pip install " + " ".join(REQUIRED_PACKAGES))

def setup_env_file():
    """מייצר תבנית לקובץ משתני הסביבה אם הוא לא קיים"""
    print_step("מגדיר משתני סביבה (.env)...")
    env_path = os.path.join(PROJECT_ROOT, ".env")
    if not os.path.exists(env_path):
        with open(env_path, "w", encoding="utf-8") as f:
            f.write("OPENAI_API_KEY=your_api_key_here\n")
            f.write("GITHUB_TOKEN=your_github_token_here\n")
            f.write("GITHUB_REPOSITORY=username/repo\n")
            f.write("MODEL=gpt-4o\n")
            f.write("UI_LANGUAGE=Hebrew\n")
        print("📝 נוצר קובץ .env! אל תשכח לעדכן בו את המפתחות שלך.")
    else:
        print("✔️ קובץ .env כבר קיים.")

def create_startup_script():
    """מייצר סקריפט הפעלה קצר למשתמש"""
    print_step("מייצר קובץ הפעלה מהיר...")
    script_path = os.path.join(PROJECT_ROOT, "start.sh")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write("#!/bin/bash\n")
        f.write("echo '🚀 מתניע את Root OS...'\n")
        f.write(f"python3 {os.path.join(PROJECT_ROOT, 'root_service.py')}\n")
    
    # מתן הרשאות הרצה בלינוקס/טרמוקס
    try:
        os.chmod(script_path, 0o755)
        print("⚡ נוצר קובץ הפעלה (start.sh).")
    except:
        pass

if __name__ == "__main__":
    print("========================================")
    print("🌳 ברוכים הבאים להתקנת Root Agentic OS")
    print("========================================")
    
    check_python_version()
    create_directories()
    install_dependencies()
    setup_env_file()
    create_startup_script()
    
    print("\n========================================")
    print("🎉 ההתקנה הושלמה בהצלחה!")
    print("========================================")
    print("👉 מה עכשיו?")
    print("1. פתח את הקובץ .env ועדכן את המפתחות שלך (API Key).")
    print("2. הפעל את המערכת על ידי הפקודה:")
    print("   ./start.sh")
    print("   (או: python3 root_service.py)")
    print("========================================")
