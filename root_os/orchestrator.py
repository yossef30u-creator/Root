#!/usr/bin/env python3
# =====
import os
import time
import subprocess
import traceback
from datetime import datetime

# ייבוא הרכיבים הפנימיים שלנו
from config import Config
from github_manager import GitHubManager
from root_brain import RootBrain

# =====

# =====
# הגדרת סביבת עבודה מדויקת כדי למנוע בעיות נתיבים ב-Termux או בענן
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_DIR)
# =====


# =====
class RootOrchestrator:
    def __init__(self):
        print("🚀 [Orchestrator] Booting up Agentic OS...")
        self.github = GitHubManager()
        self.brain = RootBrain()

        # תזמונים עתידיים - מאפשר גמישות אם נרצה לשנות זמנים דרך Config
        self.poll_interval = getattr(
            Config, "POLL_INTERVAL", 60
        )  # שניות בין בדיקת משימות (ברירת מחדל דקה)
        self.proactive_interval = getattr(
            Config, "PROACTIVE_INTERVAL", 3600
        )  # שניות בין יזימת משימות (ברירת מחדל שעה)
        self.last_proactive_run = time.time()

    # =====

    # =====
    def _run_ingestor(self):
        """
        צופה פני עתיד: הרצת ה-Ingestor כתהליך נפרד (Subprocess).
        זה מגן על ה-Orchestrator מקריסות במקרה שה-LLM נתקע ומנקה את הזיכרון בסיום הריצה.
        """
        print("🔍 [Orchestrator] Triggering Proactive Ingestor Cycle...")
        try:
            # מריץ את הקובץ שיצרנו קודם שכולל את propose_improvements
            subprocess.run(["python3", "ingestor.py"], check=True)
            print("✅ [Orchestrator] Proactive cycle completed.")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ [Orchestrator] Ingestor cycle failed: {e}")
        except Exception as e:
            print(f"❌ [Orchestrator] Failed to execute ingestor.py: {e}")

    # =====

    # =====
    def process_tasks(self):
        """שליפת משימות מ-GitHub והעברתן למוח לביצוע"""
        print("📡 [Orchestrator] Scanning GitHub for new 'root-task' issues...")
        try:
            tasks = self.github.fetch_tasks()
            if not tasks:
                return

            for task in tasks:
                issue_id = task["number"]
                title = task["title"]
                body = task.get("body", "")

                print(f"🎯 [Orchestrator] Acquired Task #{issue_id}: {title}")
                self.github.comment_on_issue(
                    issue_id,
                    "🤖 **Root OS Status:** Acknowledged. Beginning execution...",
                )

                # בניית הפרומפט הארכיטקטוני למוח
                instruction = f"Task Context from GitHub Issue #{issue_id}\nTitle: {title}\nDescription: {body}\nExecute necessary actions to resolve this. Do not ask for human input."

                # הרצת המוח האוטונומי (נניח שיש מתודה solve_task בקובץ root_brain.py)
                result = self.brain.solve_task(instruction)

                # ניתוח התוצאה וסגירת המעגל מול GitHub
                if "Error" not in result and "Failed" not in result:
                    self.github.comment_on_issue(
                        issue_id,
                        f"✅ **Task Completed Successfully!**\n\n### Agent Report:\n```\n{result}\n```",
                    )
                    self.github.close_issue(issue_id)
                    print(f"✅ [Orchestrator] Task #{issue_id} resolved and closed.")
                else:
                    self.github.comment_on_issue(
                        issue_id,
                        f"⚠️ **Task Execution Encountered Issues:**\n\n```\n{result}\n```\nRequires human review.",
                    )
                    print(
                        f"⚠️ [Orchestrator] Task #{issue_id} requires human intervention."
                    )

        except Exception as e:
            print(f"❌ [Orchestrator] Task processing error: {e}")
            traceback.print_exc()  # צופה פני עתיד: הדפסת מחסנית השגיאה המלאה ללוגים

    # =====

    # =====
    def run_forever(self):
        """הלולאה הראשית - רצה לנצח ומנהלת את סדר היום של הסוכן"""
        print("🟢 [Orchestrator] Online and listening. Press Ctrl+C to stop.")
        while True:
            try:
                # 1. טיפול במשימות קיימות
                self.process_tasks()

                # 2. סייקל פרואקטיבי (הסוכן יוזם בעצמו משימות ומשפר את הקוד)
                current_time = time.time()
                if current_time - self.last_proactive_run > self.proactive_interval:
                    self._run_ingestor()
                    self.last_proactive_run = current_time

                # 3. מנוחה עד הסייקל הבא
                time.sleep(self.poll_interval)

            except KeyboardInterrupt:
                print("\n🛑 [Orchestrator] Shutting down gracefully...")
                break
            except Exception as e:
                print(f"❌ [Orchestrator] Critical Loop Error: {e}")
                # מונע מצב של לולאה אינסופית מהירה במקרה של קריסת רשת
                time.sleep(self.poll_interval)

    # =====


# =====
if __name__ == "__main__":
    # הגנת Boot: נוודא שהמשתנים הקריטיים קיימים לפני שהסוכן מתחיל לרוץ
    if not Config.GITHUB_TOKEN:
        print(
            "❌ [Orchestrator Boot Error] GITHUB_TOKEN is missing. Cannot sync with Command Center."
        )
        exit(1)

    orchestrator = RootOrchestrator()
    orchestrator.run_forever()
# =====
