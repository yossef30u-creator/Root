# =====
import os
import sys
import subprocess # הוספנו כדי שהשרת יוכל להריץ פקודות בטרמינל
from dotenv import load_dotenv, find_dotenv

# 1. טעינת משתני הסביבה
dotenv_path = find_dotenv()
if dotenv_path:
    load_dotenv(dotenv_path, override=True)
else:
    load_dotenv()

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# 2. ייבוא הזיכרון (הסרנו את root_brain כדי למנוע לולאה אינסופית)
from memory import RootMemory

#=====
def check_api_health():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return False, "מפתח OPENAI_API_KEY חסר בקובץ ההגדרות."
    return True, f"המפתח זוהה (מתחיל ב-{api_key[:7]}...)"
#=====

# 3. אתחול השרת
app = FastAPI(title="Root Agentic OS - MCP Bridge", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. אתחול בטוח
memory = None
startup_error = None

try:
    is_healthy, health_msg = check_api_health()
    print(f"[Root_Diag] {health_msg}")
    
    if not is_healthy:
        raise Exception(health_msg)

    memory = RootMemory()
except Exception as e:
    startup_error = str(e)
    print(f"⚠️ אזהרה קריטית: רכיבי ה-AI לא עלו. שגיאה: {startup_error}")

class CommandRequest(BaseModel):
    command: str

@app.get("/status")
async def get_status():
    """החזרת הסטטוס הארכיטקטוני והבריאותי של השרת"""
    status_data = {"status": "online" if not startup_error else "degraded", "errors": startup_error}
    try:
        with open("ROOT.md", "r", encoding="utf-8") as f:
            status_data["manifest"] = f.read()
    except Exception as e:
        status_data["manifest_error"] = str(e)
    return status_data

@app.get("/query")
async def query_context(query_string: str = Query(...)):
    """חיפוש סמנטי עמוק בזיכרון הפרויקט"""
    if not memory:
        raise HTTPException(status_code=503, detail="Memory module is offline.")
    results = memory.search(query_string)
    return {"query": query_string, "results": results}

@app.post("/execute")
async def execute_command(request: CommandRequest):
    """הרצת פקודות טרמינל מקומיות בסביבת Termux"""
    try:
        print(f"⚙️ [OS] Executing command: {request.command}")
        # subprocess מריץ את הפקודה בפועל בטרמינל
        result = subprocess.run(
            request.command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        
        output = result.stdout if result.returncode == 0 else f"⚠️ Failed: {result.stderr}"
        return {"command": request.command, "output": output.strip()}
    
    except subprocess.TimeoutExpired:
         return {"command": request.command, "output": "⚠️ Failed: Command timed out after 30 seconds."}
    except Exception as e:
        return {"command": request.command, "output": f"❌ Error executing command: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
# =====
