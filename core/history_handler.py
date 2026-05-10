#!/usr/bin/env python3
# =====
import os
from datetime import datetime
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
