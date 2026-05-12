#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# #=====
# 🧠 Root OS: Dashboard Brain (Central Nervous System)
# ------------------------------------------------------------------------------
# תפקיד: תזמור פעולות הסוכנים, ניהול מצב המניפסט וסנכרון תור המשימות.
# פילוסופיה: הפרדה מוחלטת בין מוח הקבצים לממשק המשתמש. חסינות לקריסות.
# #=====

import os
import json
import time
import uuid
import atexit
from datetime import datetime

# #=====
# [1] ייבוא לוגיקת סוכנים וניהול נתיבים
# #=====
try:
    from agent_coder import execute_task_logic, generate_roadmap_strategy
except ImportError:

    def execute_task_logic(title, model):
        return False, "Agent Coder not found"

    def generate_roadmap_strategy(idea, model):
        return False, "Agent Architect not found"


DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))
CORE_DUMP_FILE = os.path.join(DASHBOARD_DIR, "core_dump.json")
STATE_FILE = os.path.join(DASHBOARD_DIR, "state_manifest.json")
ACTIONS_FILE = os.path.join(DASHBOARD_DIR, "actions_queue.json")


# #=====
# [2] פונקציות עזר לניהול JSON ומשאבים (atexit)
# #=====
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


def emergency_state_save():
    """מבטיח שמירת מצב אחרונה של המערכת לפני יציאה[span_4](start_span)[span_4](end_span)."""
    print("🔒 [Dashboard Brain] שומר מצב אחרון ומשחרר משאבי זיכרון...")


atexit.register(emergency_state_save)


# #=====
# [3] סנכרון מצב המערכת (State Sync)
# #=====
def sync_state():
    """מסנכרן את המידע הגולמי ממוח הקבצים אל ה-UI Manifest[span_5](start_span)[span_5](end_span)[span_6](start_span)[span_6](end_span)."""
    if not os.path.exists(CORE_DUMP_FILE):
        return

    print("🔄 [Dashboard Brain] מעבד נתונים חדשים...")
    core_data = load_json(CORE_DUMP_FILE, {})
    state = load_json(
        STATE_FILE,
        {
            "system_status": "idle",
            "root": {},
            "roadmap": [],
            "history": [],
            "user_credits": 1000,
            "statistics": { # Initializing statistics for the dashboard
                "credit_balance_history": [
                    {"timestamp": datetime.now().isoformat(), "balance": 1000}
                ],
                "task_summary": {
                    "total_tasks": 0,
                    "completed_tasks": 0,
                    "failed_tasks": 0,
                    "pending_tasks": 0,
                    "avg_completion_time_seconds": 0.0,
                },
                "llm_usage": [], # To be populated by agent_coder updates
            },
        },
    )

    state["last_updated"] = datetime.now().isoformat()

    if "analysis" in core_data:
        state["root"]["latest_analysis"] = core_data["analysis"]

    if "critic" in core_data:
        critic = core_data["critic"]
        state["root"]["critic_status"] = (
            "FAIL" if critic and "PASS" not in critic else "PASS"
        )
        state["root"]["critic_alerts"] = (
            [critic] if critic and "PASS" not in critic else []
        )

    if "proposed_tasks" in core_data and core_data["proposed_tasks"]:
        existing_titles = {t.get("title") for t in state.get("roadmap", [])}
        for task_title in core_data["proposed_tasks"]:
            if task_title not in existing_titles:
                state.setdefault("roadmap", []).append(
                    {
                        "id": f"task_{int(time.time())}_{uuid.uuid4().hex[:4]}",
                        "title": task_title,
                        "status": "pending",
                        "created_at": datetime.now().isoformat(),
                        "start_time": None, # Add new fields for task tracking
                        "end_time": None,   # Add new fields for task tracking
                        "error_message": None, # Add new fields for task tracking
                    }
                )

    save_json(STATE_FILE, state)
    try:
        os.remove(CORE_DUMP_FILE)
    except:
        pass


# #=====
# [4] עיבוד תור פעולות (Action Processing)
# #=====
def process_actions():
    """סורק את תור הפקודות, בודק קרדיטים, ומפעיל את הסוכן[span_7](start_span)[span_7](end_span)[span_8](start_span)[span_8](end_span)."""
    actions = load_json(ACTIONS_FILE, [])
    if not actions:
        return

    state = load_json(STATE_FILE, {})
    state_changed = False
    remaining_actions = []
    selected_model = state.get("selected_model", "anthropic/claude-3.5-sonnet")

    for action in actions:
        if action.get("status") == "pending":
            action_type = action.get("type")
            target_id = action.get("target_id")
            cost = action.get("payload", {}).get("cost", 0)

            # --- משימת כתיבת קוד ---
            if action_type == "EXECUTE_TASK":
                task_entry = next(
                    (t for t in state.get("roadmap", []) if t["id"] == target_id),
                    None,
                )

                if task_entry:
                    task_to_run = task_entry["title"]
                    if state.get("user_credits", 0) >= cost:
                        task_entry["status"] = "in_progress"
                        task_entry["start_time"] = datetime.now().isoformat()
                        state["system_status"] = "busy"
                        state.setdefault("history", []).append(
                            {
                                "timestamp": time.time(),
                                "message": f"⏳ מתחיל בביצוע משימה: {task_to_run}",
                                "type": "action_status", # [תוספת] סוג הודעה
                                "status_detail": "in_progress",
                            }
                        )
                        save_json(STATE_FILE, state)

                        print(f"🛠️ [Dashboard Brain] מבצע: {task_to_run}")
                        # Modify execute_task_logic to return LLM metrics
                        success, info, llm_model, llm_duration, llm_success, llm_cost = execute_task_logic(
                            task_to_run, model=selected_model
                        )

                        # [תוספת] רישום שינוי קרדיטים להיסטוריית גרף
                        if "credit_balance_history" not in state["statistics"]:
                            state["statistics"]["credit_balance_history"] = []
                        state["statistics"]["credit_balance_history"].append(
                            {"timestamp": datetime.now().isoformat(), "balance": state["user_credits"]}
                        )
                        state["user_credits"] -= cost
                        state["statistics"]["credit_balance_history"].append(
                            {"timestamp": datetime.now().isoformat(), "balance": state["user_credits"]}
                        )

                        # [תוספת] רישום שימוש ב-LLM
                        state.setdefault("statistics", {}) \
                            .setdefault("llm_usage", []).append({
                                "timestamp": datetime.now().isoformat(),
                                "type": "EXECUTE_TASK",
                                "model": llm_model,
                                "duration": llm_duration,
                                "success": llm_success,
                                "cost": llm_cost,
                            })

                        task_entry["end_time"] = datetime.now().isoformat()
                        task_entry["status"] = "completed" if success else "failed"
                        if not success: # [תוספת] שמירת הודעת שגיאה
                            task_entry["error_message"] = info

                        state.setdefault("history", []).append(
                            {
                                "timestamp": time.time(),
                                "message": (
                                    f"✅ הושלם: {task_to_run} (-{cost} Cr)"
                                    if success
                                    else f"❌ כשל: {info}"
                                ),
                                "type": "action_status", # [תוספת] סוג הודעה
                                "status_detail": "completed" if success else "failed",
                            }
                        )
                        action["status"] = "completed"
                        state_changed = True
                    else:
                        # [תוספת] טיפול בחוסר קרדיטים
                        task_entry["status"] = "skipped"
                        task_entry["error_message"] = "Insufficient credits to execute task."
                        state.setdefault("history", []).append(
                            {
                                "timestamp": time.time(),
                                "message": f"⚠️ דילוג: {task_to_run} (אין מספיק קרדיטים)",
                                "type": "alert",
                                "severity": "warning",
                            }
                        )
                        action["status"] = "skipped"
                        state_changed = True
                else: # [תוספת] טיפול במשימה לא קיימת ב-roadmap
                    state.setdefault("history", []).append(
                        {
                            "timestamp": time.time(),
                            "message": f"❌ שגיאה: משימה לא ידועה {target_id}.",
                            "type": "alert",
                            "severity": "error",
                        }
                    )
                    action["status"] = "failed"
                    state_changed = True

            # --- תכנון מפת דרכים ---
            elif action_type == "GENERATE_ROADMAP":
                idea = action.get("payload", {}).get("idea", "רעיון חדש")

                # [תוספת] עדכון סטטוס ל-"in_progress" עבור פעולת ה-roadmap
                state["system_status"] = "busy"
                state.setdefault("history", []).append(
                    {"timestamp": time.time(), "message": "⏳ מתכנן אסטרטגיה...", "type": "action_status", "status_detail": "in_progress"}
                )
                save_json(STATE_FILE, state) # [חשוב] שמירת המצב לפני זימון ה-AI

                # Modify generate_roadmap_strategy to return LLM metrics
                success, tasks, llm_model, llm_duration, llm_success, llm_cost = generate_roadmap_strategy(idea, model=selected_model)
                
                # [תוספת] רישום שימוש ב-LLM
                state.setdefault("statistics", {}) \
                    .setdefault("llm_usage", []).append({
                        "timestamp": datetime.now().isoformat(),
                        "type": "GENERATE_ROADMAP",
                        "model": llm_model,
                        "duration": llm_duration,
                        "success": llm_success,
                        "cost": llm_cost,
                    })

                if success and isinstance(tasks, list):
                    for t_title in tasks:
                        state.setdefault("roadmap", []).append(
                            {
                                "id": f"task_{uuid.uuid4().hex[:6]}",
                                "title": t_title,
                                "status": "pending",
                                "created_at": datetime.now().isoformat(),
                                "start_time": None,
                                "end_time": None,
                                "error_message": None,
                            }
                        )
                    state.setdefault("history", []).append(
                        {
                            "timestamp": time.time(),
                            "message": f"✅ נוצרו {len(tasks)} משימות חדשות.",
                            "type": "action_status",
                            "status_detail": "completed",
                        }
                    )
                else:
                    # [תוספת] טיפול בכשלון יצירת מפת דרכים
                    state.setdefault("history", []).append(
                        {
                            "timestamp": time.time(),
                            "message": f"❌ כשל ביצירת מפת דרכים: {str(tasks)}",
                            "type": "alert",
                            "severity": "error",
                        }
                    )
                action["status"] = "completed"
                state_changed = True

        # [תוספת] עידכון סטטיסטיקות משימות
        if state_changed:
            total = len(state.get("roadmap", []))
            completed = sum(1 for t in state.get("roadmap", []) if t["status"] == "completed")
            failed = sum(1 for t in state.get("roadmap", []) if t["status"] == "failed")
            pending = sum(1 for t in state.get("roadmap", []) if t["status"] == "pending" or t["status"] == "in_progress" or t["status"] == "skipped")
            
            state["statistics"]["task_summary"]["total_tasks"] = total
            state["statistics"]["task_summary"]["completed_tasks"] = completed
            state["statistics"]["task_summary"]["failed_tasks"] = failed
            state["statistics"]["task_summary"]["pending_tasks"] = pending

            # חישוב זמן ממוצע למשימה שהושלמה
            completed_durations = [
                (datetime.fromisoformat(t["end_time"]) - datetime.fromisoformat(t["start_time"])) \
                .total_seconds() for t in state.get("roadmap", [])
                if t["status"] == "completed" and t["start_time"] and t["end_time"]
            ]
            if completed_durations:
                state["statistics"]["task_summary"]["avg_completion_time_seconds"] = \
                    sum(completed_durations) / len(completed_durations)
            else:
                state["statistics"]["task_summary"]["avg_completion_time_seconds"] = 0.0


        remaining_actions.append(action)

    if state_changed:
        state["system_status"] = "idle"
        save_json(STATE_FILE, state)
        save_json(
            ACTIONS_FILE, [a for a in remaining_actions if a["status"] == "pending"]
        )



        remaining_actions.append(action)

    if state_changed:
        state["system_status"] = "idle"
        save_json(STATE_FILE, state)
        save_json(
            ACTIONS_FILE, [a for a in remaining_actions if a["status"] == "pending"]
        )


# #=====
if __name__ == "__main__":
    print("🧠 [Dashboard Brain] Online - Listening for commands...")
    try:
        while True:
            sync_state()
            process_actions()
            time.sleep(1.5)
    except KeyboardInterrupt:
        pass
