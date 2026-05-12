#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import signal
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- הגדרת נתיבי מערכת ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_DIR = os.path.join(PROJECT_ROOT, "dashboard")
CORE_DIR = os.path.join(PROJECT_ROOT, "core")

# משתנה לשמירת כל תהליכי הרקע שהמערכת מריצה
background_processes = {"bridge_server": None, "dashboard_brain": None}


def start_background_process(name, script_path):
    """מפעיל סקריפט (שרת או מוח) כתהליך רקע שקט"""
    if os.path.exists(script_path):
        print(f"🚀 [Service] מתניע את {name}...")
        # פתיחת התהליך ברקע
        return subprocess.Popen([sys.executable, script_path])
    else:
        print(f"❌ [Service] שגיאה: לא נמצא הקובץ {script_path}")
        return None


def graceful_shutdown(signum=None, frame=None):
    """מכבה את כל התהליכים בצורה נקייה כשסוגרים את המערכת (Ctrl+C)"""
    print("\n🛑 [Service] מכבה את כל שירותי Root OS בצורה בטוחה...")
    for name, process in background_processes.items():
        if process:
            print(f"   -> סוגר את {name}...")
            process.terminate()
            process.wait()
    sys.exit(0)


class RootEventHandler(FileSystemEventHandler):
    """החיישן שמזהה מתי שמרת קובץ ומפעיל את מוח הקבצים (Ingestor)"""

    def __init__(self):
        self.last_run = 0
        self.debounce = 2  # חסימת הפעלות כפולות

    def on_modified(self, event):
        if event.is_directory:
            return

        filename = os.path.basename(event.src_path)

        # התעלמות מקבצים שהמערכת מעדכנת בעצמה כדי למנוע לולאה אינסופית
        ignored_files = [
            "ROOT.md",
            "HISTORY.md",
            "ROADMAP.md",
            "state_manifest.json",
            "actions_queue.json",
            "core_dump.json",
        ]

        if any(ign in event.src_path for ign in ignored_files) or filename.startswith(
            "."
        ):
            return

        # האזנה רק לקבצי קוד ותצורה
        if filename.endswith((".py", ".js", ".html", ".css", ".json", ".env")):
            now = time.time()
            if now - self.last_run > self.debounce:
                self.trigger_ingestor()
                self.last_run = now

    def trigger_ingestor(self):
        print("⚡ [Service] שינוי קוד זוהה! מזניק את מוח הקבצים (Ingestor)...")
        ingestor_path = os.path.join(CORE_DIR, "ingestor.py")

        # תמיכה בנתיבים חלופיים
        if not os.path.exists(ingestor_path):
            ingestor_path = os.path.join(PROJECT_ROOT, "ingestor.py")

        if os.path.exists(ingestor_path):
            subprocess.run([sys.executable, ingestor_path])
        else:
            print("❌ [Service] שגיאה: מנוע הניתוח (ingestor.py) לא נמצא.")


if __name__ == "__main__":
    # רישום פונקציית הכיבוי
    signal.signal(signal.SIGINT, graceful_shutdown)
    signal.signal(signal.SIGTERM, graceful_shutdown)

    print("========================================")
    print("🌳 [Service] מערכת Root Agentic OS מתעוררת")
    print("========================================")

    # 1. הפעלת שרת התקשורת לדשבורד
    background_processes["bridge_server"] = start_background_process(
        "Bridge Server (API)", os.path.join(DASHBOARD_DIR, "bridge_server.py")
    )

    # 2. הפעלת מוח הדשבורד (הצד הפרואקטיבי שצופה פני עתיד)
    background_processes["dashboard_brain"] = start_background_process(
        "Dashboard Brain (Controller)",
        os.path.join(DASHBOARD_DIR, "dashboard_brain.py"),
    )

    # 3. הפעלת חיישן ההגנה על הקבצים
    event_handler = RootEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path=PROJECT_ROOT, recursive=True)
    observer.start()

    print("🛡️ [Service] ההגנה פעילה. הכל רץ ברקע.")
    print("👉 פתח את הדשבורד (ui_template.html) בדפדפן כדי לראות את המערכת.")
    print("👉 לחץ Ctrl+C כדי לעצור את הכל יחד.")
    print("========================================")

    try:
        # הלולאה שומרת על הסקריפט הראשי באוויר
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        graceful_shutdown()
