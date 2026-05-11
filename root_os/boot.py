#!/usr/bin/env python3
# =====
import os
import sys
import platform
import subprocess
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# 1. טעינת מנהל ההגדרות האחיד והזיכרון
from config_manager import Config
from memory import RootMemory

# =====
def check_api_health():
    api_key = Config.API_KEY
    if not api_key:
        return False, "מפתח ה-API חסר בקובץ ההגדרות. הרץ את 'root' להגדרתו."
    # מסתיר את המפתח ללוגים בטוחים
    safe_key = f"{api_key[:6]}...{api_key[-4:]}" if len(api_key) > 10 else "Invalid Length"
    return True, f"מפתח API זוהה: {safe_key}"
# =====

# 2. אתחול השרת
app = FastAPI(title="Root Agentic OS - MCP Bridge", version="1.0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. אתחול בטוח
memory = None
startup_error = None
is_mobile = "termux" in os.getenv("PREFIX", "").lower() or "android" in platform.processor().lower()

try:
    is_healthy, health_msg = check_api_health()
    print(f"[Root_Diag] {health_msg}")
    
    if not is_healthy:
        raise Exception(health_msg)

    memory = RootMemory()
except Exception as e:
    startup_error = str(e)
    print(f"⚠️ אזהרה קריטית: רכיבי הליבה לא עלו. שגיאה: {startup_error}")

# ===== מודלים לבקשות =====
class CommandRequest(BaseModel):
    command: str

# ===== נתיבי ה-API =====

@app.get("/status")
async def get_status():
    """החזרת הסטטוס הארכיטקטוני והבריאותי של השרת - צופה פני עתיד"""
    status_data = {
        "status": "online" if not startup_error else "degraded",
        "environment": "Mobile/Termux" if is_mobile else "Desktop/Server",
        "memory_type": "Vector DB (Chroma)" if memory and memory.use_chroma else "Lite DB (JSON)",
        "errors": startup_error
    }
    
    # ניסיון לשאוב את המניפסט הנוכחי
    try:
        if os.path.exists("ROOT.md"):
            with open("ROOT.md", "r", encoding="utf-8") as f:
                status_data["manifest"] = f.read(2000) + "..." # מחזיר רק תקציר למניעת עומס
        else:
             status_data["manifest"] = "קובץ ROOT.md טרם נוצר בפרויקט זה."
    except Exception as e:
        status_data["manifest_error"] = str(e)
        
    return status_data

@app.get("/query")
async def query_context(query_string: str = Query(..., min_length=2)):
    """חיפוש סמנטי עמוק בזיכרון הפרויקט"""
    if not memory:
        raise HTTPException(status_code=503, detail="Memory module is offline.")
    
    try:
        results = memory.search(query_string)
        return {"query": query_string, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/execute")
async def execute_command(request: CommandRequest):
    """
    הרצת פקודות טרמינל מקומיות. 
    כולל הגנה "צופת פני עתיד" נגד פקודות הרסניות.
    """
    cmd = request.command.strip()
    
    # הגנה פשוטה נגד פקודות מסוכנות (ניתן להרחבה בעתיד)
    dangerous_commands = ["rm -rf /", "mkfs", "dd if="]
    for bad_cmd in dangerous_commands:
        if bad_cmd in cmd:
            return {"command": cmd, "output": "❌ Security Alert: Command blocked by Root OS."}

    try:
        print(f"⚙️ [OS] Executing command: {cmd}")
        
        # הרצת הפקודה. shell=True דרוש ברוב פקודות הטרמינל הפשוטות
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=45 # הוארך כדי לאפשר התקנות pip או פעולות קצת ארוכות יותר
        )
        
        # שילוב נקי של פלט רגיל ופלט שגיאות
        output = result.stdout if result.stdout else result.stderr
        
        # חיתוך הפלט אם הוא ארוך מדי (למניעת קריסת הדפדפן של הלקוח)
        if len(output) > 10000:
             output = output[:10000] + "\n... [Output Truncated] ..."
             
        return {"command": cmd, "output": output.strip(), "success": result.returncode == 0}
    
    except subprocess.TimeoutExpired:
         return {"command": cmd, "output": "⚠️ Failed: Command timed out after 45 seconds.", "success": False}
    except Exception as e:
        return {"command": cmd, "output": f"❌ Error executing command: {str(e)}", "success": False}

# =====
if __name__ == "__main__":
    # אתחול השרת על הפורט הנכון. חשוב שיעבוד מכל הרשת (0.0.0.0) כדי שהטלפון/מחשב יוכלו לגשת אחד לשני
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
# =====