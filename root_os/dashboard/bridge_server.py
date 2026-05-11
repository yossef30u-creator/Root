#!/usr/bin/env python3
# =====
import os
import sys
import json
import time
import uuid
import tempfile
import logging
import re  # <--- [תוספת] נוסף עבור חילוץ שמות קבצים למפה הגרפית
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# --- תוספות לחיבור הליבה ---
from openai import OpenAI
# הוספת נתיב ה-core ל-sys.path כדי לאפשר ייבוא של המודולים שבנינו
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core"))
from memory import RootMemory
from config_manager import Config
# -----------------------

# 🛠️ מערכת לוגים תעשייתית
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [BRIDGE] - %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger("RootBridge")

app = Flask(__name__)
CORS(app) 

# ==========================================
# 1. הגדרת נתיבי עבודה ואתחול מנועים
# ==========================================
if len(sys.argv) < 2:
    PROJECT_DIR = os.getcwd()
    logger.warning("Project path not provided. Using current directory.")
else:
    PROJECT_DIR = sys.argv[1]

STATE_FILE = os.path.join(PROJECT_DIR, ".root_state_manifest.json")
ACTIONS_FILE = os.path.join(PROJECT_DIR, ".root_actions_queue.json")
DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))
UI_FILENAME = "ui_template.html"

# אתחול הזיכרון וה-AI
# המערכת טוענת את הזיכרון הוקטורי (JSON או ChromaDB) מהתיקייה של הפרויקט
memory = RootMemory()
client = OpenAI(
    api_key=Config.API_KEY, 
    base_url=Config.BASE_URL,
    default_headers={"HTTP-Referer": "https://github.com/RootProject", "X-Title": "Root Agentic OS"}
)

MODEL_PRICING = {
    "anthropic/claude-3.5-sonnet": {"cost_per_action": 15, "label": "Claude 3.5 Sonnet (Pro)"},
    "openai/gpt-4o": {"cost_per_action": 12, "label": "GPT-4o (Analyst)"},
    "meta-llama/llama-3-70b-instruct": {"cost_per_action": 5, "label": "Llama 3 70B (Fast)"},
    "openai/gpt-4o": {"cost_per_action": 8, "label": "Gemini 1.5 Pro"}
}

START_TIME = time.time()

def atomic_write_json(filepath, data):
    try:
        fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(filepath))
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        os.replace(temp_path, filepath)
    except Exception as e:
        logger.error(f"Atomic write failed for {os.path.basename(filepath)}: {e}")

def ensure_files():
    if not os.path.exists(STATE_FILE):
        atomic_write_json(STATE_FILE, {
            "system_status": "idle",
            "last_updated": time.time(),
            "root": {"latest_analysis": "", "critic_status": "PASS", "critic_alerts": []},
            "roadmap": [],
            "history": [{"timestamp": time.time(), "message": f"Root OS Engine Initialized in {PROJECT_DIR}."}],
            "user_credits": 1000, 
            "selected_model": Config.MODEL
        })
    if not os.path.exists(ACTIONS_FILE):
        atomic_write_json(ACTIONS_FILE, [])

# ==========================================
# 2. ה-Endpoints של השרת
# ==========================================

@app.route('/')
def index():
    if os.path.exists(os.path.join(DASHBOARD_DIR, UI_FILENAME)):
        return send_from_directory(DASHBOARD_DIR, UI_FILENAME)
    return jsonify({"error": "UI Core Missing", "status": "Critical"}), 404

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(DASHBOARD_DIR, filename)

@app.route('/api/state', methods=['GET'])
def get_state():
    ensure_files()
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
        state["pricing"] = MODEL_PRICING
        return jsonify(state), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    [חדש] מנוע הצ'אט של המפלצת:
    משלב חיפוש בזיכרון הוקטורי (RAG) יחד עם ה-AI כדי לענות על שאלות לגבי הפרויקט.
    """
    data = request.json
    user_msg = data.get("message")
    if not user_msg:
        return jsonify({"error": "No message"}), 400

    try:
        # 1. שליפת הקשר מהזיכרון הוקטורי (Top 3 תוצאות הכי רלוונטיות)
        context_items = memory.search_memory(user_msg, top_k=3)
        context_text = ""
        if context_items:
            context_text = "\n".join([f"Context from {item[1]['metadata'].get('path', 'memory')}:\n{item[1]['text']}" for item in context_items])

        # 2. פנייה ל-AI עם ההקשר המקומי
        response = client.chat.completions.create(
            model=Config.MODEL,
            messages=[
                {"role": "system", "content": f"You are Root OS, an expert architect. Use this project context if relevant:\n{context_text}"},
                {"role": "user", "content": user_msg}
            ]
        )
        
        reply = response.choices[0].message.content
        return jsonify({"reply": reply, "context_used": bool(context_items)})

    except Exception as e:
        logger.error(f"Chat Error: {e}")
        return jsonify({"reply": "מצטערת, הייתה לי שגיאה בגישה לזיכרון הוקטורי."}), 500

# ---------------------------------------------------------
# [תוספת - צופת פני עתיד] ה-Endpoint של המפה הארכיטקטונית
# ---------------------------------------------------------
@app.route('/api/graph', methods=['GET'])
def get_graph_data():
    """
    קורא את ה-ROOT.md ומייצר מתוכו מפת קשרים דינמית.
    הנתונים חוזרים בפורמט של nodes (נקודות) ו-links (קשרים) המוכנים להצגה ב-UI.
    """
    root_md_path = os.path.join(PROJECT_DIR, "ROOT.md")
    
    # צומת האב המרכזי - הפרויקט עצמו
    nodes = [{"id": "Core Engine", "group": 0}]
    links = []

    if os.path.exists(root_md_path):
        try:
            with open(root_md_path, "r", encoding="utf-8") as f:
                content = f.read()

            # חילוץ חכם: מוצא כל מילה שמוקפת בגרשיים בודדים כמו `file.py` או מודולים מרכזיים
            # זה מאפשר ל-RootCritic להגדיר קבצים והמפה פשוט תצייר אותם
            files = set(re.findall(r'`([^`]+\.[a-zA-Z0-9]+)`', content))
            
            for idx, f in enumerate(files, start=1):
                nodes.append({"id": f, "group": 1})
                links.append({"source": "Core Engine", "target": f})
                
            # אם אין קבצים שזוהו בבירור, נציג מצב בסיסי
            if len(nodes) == 1:
                nodes.append({"id": "Waiting for Architecture", "group": 2})
                links.append({"source": "Core Engine", "target": "Waiting for Architecture"})

        except Exception as e:
            logger.error(f"Failed to generate graph data: {e}")
            nodes.append({"id": "Error parsing ROOT.md", "group": 3})

    return jsonify({"nodes": nodes, "links": links})
# ---------------------------------------------------------

@app.route('/api/settings', methods=['POST'])
def update_settings():
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
        return jsonify({"status": "success", "model": new_model})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/action', methods=['POST'])
def post_action():
    ensure_files()
    action_data = request.json
    if not action_data or 'type' not in action_data:
        return jsonify({"error": "Invalid action"}), 400
        
    try:
        with open(ACTIONS_FILE, "r", encoding="utf-8") as f:
            actions = json.load(f)
        
        enriched_action = {
            "id": f"cmd_{uuid.uuid4().hex[:8]}",
            "type": action_data['type'],
            "payload": action_data.get('payload', {}),
            "timestamp": time.time(),
            "status": "pending"
        }
        
        actions.append(enriched_action)
        atomic_write_json(ACTIONS_FILE, actions)
        return jsonify({"command_id": enriched_action['id'], "status": "queued"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    uptime = round(time.time() - START_TIME, 2)
    return jsonify({"status": "ONLINE", "uptime_seconds": uptime, "engine": "Root 5.0", "project": PROJECT_DIR}), 200

if __name__ == '__main__':
    ensure_files()
    print("\n" + "═"*50)
    print("🚀 [Root OS] THE MONSTER IS AWAKE")
    print("═"*50)
    print(f"📁 Managing Project:  {PROJECT_DIR}")
    print("🌐 Dashboard: http://127.0.0.1:5050")
    print("═"*50 + "\n")
    
    app.run(host='0.0.0.0', port=5050, debug=False, use_reloader=False, threaded=True)