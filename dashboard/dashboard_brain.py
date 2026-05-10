#!/usr/bin/env python3
import os
import json
import time
from datetime import datetime

# ייבוא הלוגיקה של הסוכן (המתכנת האוטונומי)
try:
    from agent_coder import execute_task_logic
except ImportError:
    # הוספנו תמיכה בקבלת פרמטר 'model'
    def execute_task_logic(title, model): return False, "Agent Coder not found"

# הגדרת נתיבים בתוך תיקיית ה-Dashboard
DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))
CORE_DUMP_FILE = os.path.join(DASHBOARD_DIR, "core_dump.json")
STATE_FILE = os.path.join(DASHBOARD_DIR, "state_manifest.json")
ACTIONS_FILE = os.path.join(DASHBOARD_DIR, "actions_queue.json")

def load_json(filepath, default_value):
    if not os.path.exists(filepath):
        return default_value
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ [Dashboard Brain] Error reading {os.path.basename(filepath)}: {e}")
        return default_value

def save_json(filepath, data):
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"⚠️ [Dashboard Brain] Error writing {os.path.basename(filepath)}: {e}")

def sync_state():
    """מסנכרן את המידע הגולמי ממוח הקבצים אל ה-UI Manifest."""
    if not os.path.exists(CORE_DUMP_FILE):
        return 

    print("🔄 [Dashboard Brain] מעבד נתונים חדשים ממוח הקבצים...")
    core_data = load_json(CORE_DUMP_FILE, {})
    
    # טוען את המצב הקיים כדי לא לדרוס קרדיטים והגדרות מודל
    state = load_json(STATE_FILE, {"system_status": "idle", "root": {}, "roadmap": [], "history": [], "user_credits": 1000})
    state["last_updated"] = datetime.now().isoformat()
    
    # עדכון ניתוח ה-Root
    if "analysis" in core_data:
        state["root"]["latest_analysis"] = core_data["analysis"]
    
    # עדכון ה-Critic
    if "critic" in core_data:
        critic = core_data["critic"]
        state["root"]["critic_status"] = "FAIL" if critic and "PASS" not in critic else "PASS"
        state["root"]["critic_alerts"] = [critic] if critic and "PASS" not in critic else []
    
    # עדכון משימות חדשות ב-Roadmap
    if "proposed_tasks" in core_data and core_data["proposed_tasks"]:
        existing_titles = {t.get("title") for t in state.get("roadmap", [])}
        for task_title in core_data["proposed_tasks"]:
            if task_title not in existing_titles:
                state.setdefault("roadmap", []).append({
                    "id": f"task_{int(time.time())}_{len(state.get('roadmap', []))}",
                    "title": task_title,
                    "status": "pending",
                    "created_at": datetime.now().isoformat()
                })

    save_json(STATE_FILE, state)
    
    try:
        os.remove(CORE_DUMP_FILE)
    except:
        pass
    print("✅ [Dashboard Brain] ה-Manifest עודכן בהצלחה.")

def process_actions():
    """סורק את תור הפקודות, בודק קרדיטים, ומפעיל את הסוכן."""
    actions = load_json(ACTIONS_FILE, [])
    if not actions:
        return

    state = load_json(STATE_FILE, {})
    state_changed = False
    remaining_actions = []

    # שולף את המודל שהמשתמש בחר מהדשבורד (ברירת מחדל: קלוד)
    selected_model = state.get("selected_model", "anthropic/claude-3.5-sonnet")

    for action in actions:
        if action.get("status") == "pending":
            action_type = action.get("type")
            target_id = action.get("target_id")
            cost = action.get("payload", {}).get("cost", 0)

            if action_type == "EXECUTE_TASK":
                # בדיקת תקציב לפני ביצוע
                if state.get("user_credits", 0) >= cost:
                    task_to_run = "משימה לא ידועה"
                    for task in state.get("roadmap", []):
                        if task["id"] == target_id:
                            task["status"] = "in_progress"
                            task_to_run = task["title"]
                            break
                    
                    state["system_status"] = "busy"
                    save_json(STATE_FILE, state)
                    
                    print(f"🛠️ [Dashboard Brain] מזניק את הסוכן לביצוע: {task_to_run}")
                    print(f"🤖 מודל נבחר: {selected_model}")
                    
                    # הפעלת הסוכן ושליחת המודל הספציפי שנבחר!
                    success, info = execute_task_logic(task_to_run, model=selected_model)
                    
                    # גביית התשלום
                    state["user_credits"] -= cost
                    
                    for task in state.get("roadmap", []):
                        if task["id"] == target_id:
                            task["status"] = "completed" if success else "failed"
                            break
                    
                    state.setdefault("history", []).append({
                        "timestamp": time.time(),
                        "message": f"הושלם ({selected_model.split('/')[-1]}): {task_to_run} (-{cost} Cr)"
                    })
                    
                    action["status"] = "completed"
                    state_changed = True
                    print(f"💰 [Brain] פעולה הושלמה. יתרה מעודכנת: {state['user_credits']} Cr")
                else:
                    print(f"⚠️ [Brain] נדחה: אין מספיק קרדיטים לפעולה.")
                    state.setdefault("history", []).append({
                        "timestamp": time.time(),
                        "message": "שגיאת תקציב: אין מספיק קרדיטים לביצוע הפעולה."
                    })
                    action["status"] = "failed"
                    state_changed = True

        remaining_actions.append(action)

    if state_changed:
        state["system_status"] = "idle"
        save_json(STATE_FILE, state)
        
        # שמירת משימות שעדיין ממתינות (אם יש)
        pending_only = [a for a in remaining_actions if a['status'] == 'pending']
        save_json(ACTIONS_FILE, pending_only)

if __name__ == "__main__":
    print("🧠 [Dashboard Brain] המערכת באוויר - מאזינה לנתונים ופקודות...")
    try:
        while True:
            sync_state()
            process_actions()
            time.sleep(1.5)
    except KeyboardInterrupt:
        print("\n🛑 [Dashboard Brain] סגירת מערכת.")
