import subprocess
import os
import sys

def check_for_updates():
    print("🔍 [Updater] בודק אם יש עדכונים למערכת...")
    try:
        if not os.path.exists(".git"):
            print("⚠️ [Updater] לא זוהה Git Repository. עדכון אוטומטי מושבת.")
            return False

        subprocess.run(["git", "fetch"], check=True, capture_output=True)
        status = subprocess.run(["git", "status", "-uno"], check=True, capture_output=True, text=True)

        if "Your branch is behind" in status.stdout:
            print("🚀 [Updater] נמצאה גרסה חדשה! מעדכן...")
            subprocess.run(["git", "pull"], check=True)
            
            if os.path.exists("requirements.txt"):
                subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
            
            print("✅ [Updater] המערכת עודכנה בהצלחה.")
            return True # פה היה חסר!
        else:
            print("✅ [Updater] המערכת מעודכנת.")
            return False

    except Exception as e:
        print(f"❌ [Updater Error] כשל בניסיון העדכון: {e}")
        return False