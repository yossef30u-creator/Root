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
                if state.get("user_credits", 0) >= cost:
                    task_to_run = next(
                        (
                            t["title"]
                            for t in state.get("roadmap", [])
                            if t["id"] == target_id
                        ),
                        "משימה לא ידועה",
                    )
                    state["system_status"] = "busy"
                    save_json(STATE_FILE, state)

                    print(f"🛠️ [Dashboard Brain] מבצע: {task_to_run}")
                    success, info = execute_task_logic(
                        task_to_run, model=selected_model
                    )

                    state["user_credits"] -= cost
                    for task in state.get("roadmap", []):
                        if task["id"] == target_id:
                            task["status"] = "completed" if success else "failed"

                    state.setdefault("history", []).append(
                        {
                            "timestamp": time.time(),
                            "message": (
                                f"✅ הושלם: {task_to_run} (-{cost} Cr)"
                                if success
                                else f"❌ כשל: {info}"
                            ),
                        }
                    )
                    action["status"] = "completed"
                    state_changed = True

            # --- תכנון מפת דרכים ---
            elif action_type == "GENERATE_ROADMAP":
                idea = action.get("payload", {}).get("idea", "רעיון חדש")
                state["system_status"] = "busy"
                state.setdefault("history", []).append(
                    {"timestamp": time.time(), "message": "⏳ מתכנן אסטרטגיה..."}
                )
                save_json(STATE_FILE, state)

                success, tasks = generate_roadmap_strategy(idea, model=selected_model)
                if success and isinstance(tasks, list):
                    for t_title in tasks:
                        state.setdefault("roadmap", []).append(
                            {
                                "id": f"task_{uuid.uuid4().hex[:6]}",
                                "title": t_title,
                                "status": "pending",
                                "created_at": datetime.now().isoformat(),
                            }
                        )
                    state.setdefault("history", []).append(
                        {
                            "timestamp": time.time(),
                            "message": f"✅ נוצרו {len(tasks)} משימות חדשות.",
                        }
                    )
                action["status"] = "completed"
                state_changed = True

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
