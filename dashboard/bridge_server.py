#!/usr/bin/env python3
import os
import json
import time
import uuid
import tempfile
import logging
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# 🛠️ מערכת לוגים תעשייתית (מחליפה את ה-Print הרגיל לאמינות גבוהה)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [BRIDGE] - %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger("RootBridge")

app = Flask(__name__)
# פותח את השרת לכל דומיין, הכרחי כשעוברים לענן האמיתי
CORS(app) 

# נתיבים
DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(DASHBOARD_DIR, "state_manifest.json")
ACTIONS_FILE = os.path.join(DASHBOARD_DIR, "actions_queue.json")
UI_FILENAME = "ui_template.html"

# [חדש] מחירון דמיוני בקרדיטים למודלים השונים
MODEL_PRICING = {
    "anthropic/claude-3.5-sonnet": {"cost_per_action": 15, "label": "Claude 3.5 Sonnet (Pro)"},
    "openai/gpt-4o": {"cost_per_action": 12, "label": "GPT-4o (Analyst)"},
    "meta-llama/llama-3-70b-instruct": {"cost_per_action": 5, "label": "Llama 3 70B (Fast)"},
    "google/gemini-pro-1.5": {"cost_per_action": 8, "label": "Gemini 1.5 Pro"}
}

# משתנה למעקב אחרי זמן עליית השרת
START_TIME = time.time()

def atomic_write_json(filepath, data):
    """
    [צופה פני עתיד - Enterprise]
    כתיבה אטומית שמונעת השחתת נתונים (Data Corruption) כשיש מיליוני משתמשים שכותבים וקוראים יחד.
    """
    try:
        fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(filepath))
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        os.replace(temp_path, filepath) # פעולה אטומית ברמת מערכת ההפעלה
    except Exception as e:
        logger.error(f"Atomic write failed for {os.path.basename(filepath)}: {e}")

def ensure_files():
    """מבטיח שהתשתית קיימת ומוכנה ברגע שהשרת עולה"""
    if not os.path.exists(STATE_FILE):
        atomic_write_json(STATE_FILE, {
            "system_status": "idle",
            "last_updated": time.time(),
            "root": {"latest_analysis": "", "critic_status": "PASS", "critic_alerts": []},
            "roadmap": [],
            "history": [{"timestamp": time.time(), "message": "Root OS Engine Initialized."}],
            # [חדש] אתחול ארנק משתמש ובחירת מודל
            "user_credits": 1000, 
            "selected_model": "anthropic/claude-3.5-sonnet"
        })
        
    if not os.path.exists(ACTIONS_FILE):
        atomic_write_json(ACTIONS_FILE, [])

@app.route('/')
def index():
    """הדלת הקדמית: טוען את חללית האם (HTML) ישירות למשתמש"""
    if os.path.exists(os.path.join(DASHBOARD_DIR, UI_FILENAME)):
        return send_from_directory(DASHBOARD_DIR, UI_FILENAME)
    return jsonify({"error": "UI Core Missing. Please check ui_template.html", "status": "Critical"}), 404

@app.route('/api/state', methods=['GET'])
def get_state():
    """מזרים את הסטטוס לכל המשתמשים המחוברים במקביל"""
    ensure_files()
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
        
        # [חדש] הזרקת המחירון ויתרת גיבוי לדשבורד
        state["pricing"] = MODEL_PRICING
        if "user_credits" not in state:
            state["user_credits"] = 1000
            state["selected_model"] = "anthropic/claude-3.5-sonnet"
            
        return jsonify(state), 200
    except Exception as e:
        logger.error(f"State Read Error: {e}")
        return jsonify({"error": "State Synchronization Failed"}), 500

@app.route('/api/settings', methods=['POST'])
def update_settings():
    """
    [חדש] צופה פני עתיד - מאפשר למשתמש להחליף מנוע AI מהדשבורד
    """
    ensure_files()
    data = request.json
    new_model = data.get("model")
    
    if not new_model:
        return jsonify({"error": "No model selected"}), 400

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
        
        state["selected_model"] = new_model
        atomic_write_json(STATE_FILE, state)
        
        logger.info(f"⚙️ [Settings] Model switched to: {new_model}")
        return jsonify({"status": "success", "model": new_model})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/action', methods=['POST'])
def post_action():
    """
    [צופה פני עתיד - המוח המבצעי]
    קולט פקודות מאובטחות, נותן להן מספר סידורי, ומכניס לתור הביצוע.
    """
    ensure_files()
    action_data = request.json
    
    if not action_data or 'type' not in action_data:
        return jsonify({"error": "Invalid payload format. 'type' is required."}), 400
        
    try:
        # קריאה זהירה של התור
        with open(ACTIONS_FILE, "r", encoding="utf-8") as f:
            try:
                actions = json.load(f)
            except json.JSONDecodeError:
                actions = []
        
        # בניית אובייקט הפקודה עם אבטחה ושליטה (UUID)
        enriched_action = {
            "id": f"cmd_{uuid.uuid4().hex[:8]}", # תעודת זהות ייחודית לפקודה
            "type": action_data['type'],
            "target_id": action_data.get('target_id', 'global'),
            "payload": action_data.get('payload', {}),
            "timestamp": time.time(),
            "status": "pending"
        }
        
        actions.append(enriched_action)
        atomic_write_json(ACTIONS_FILE, actions)
            
        logger.info(f"⚡ Action Engaged: [{enriched_action['type']}] Task ID: {enriched_action['id']}")
        return jsonify({
            "message": "Action successfully queued", 
            "command_id": enriched_action['id'],
            "status": "processing"
        }), 201
        
    except Exception as e:
        logger.error(f"Action Queue Error: {e}")
        return jsonify({"error": "Failed to engage action sequence"}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """בדיקת דופק (קריטי למערכות ענן שאמורות לשרת מיליונים)"""
    uptime = round(time.time() - START_TIME, 2)
    return jsonify({"status": "ONLINE", "uptime_seconds": uptime, "engine": "Root 2.0"}), 200

if __name__ == '__main__':
    ensure_files()
    print("\n" + "═"*50)
    print("🚀 [Root OS] THE MONSTER IS AWAKE")
    print("═"*50)
    print("🌐 Cockpit (Local):   http://127.0.0.1:5050")
    print("📡 Fleet (Network):   http://0.0.0.0:5050")
    print("═"*50 + "\n")
    
    # threaded=True הוא קסם - הוא מאפשר ל-Flask לטפל באלף משתמשים במקביל
    app.run(host='0.0.0.0', port=5050, debug=False, threaded=True)
