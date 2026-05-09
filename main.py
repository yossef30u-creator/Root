import os
import sys
from dotenv import load_dotenv, find_dotenv

# 1. טעינת משתני הסביבה חייבת להיות השורה הראשונה בפועל
# כך כל המודולים (המוח והזיכרון) יזהו את מפתח ה-API ברגע שהם מיובאים.
# תוספת: אילוץ טעינה מהקובץ הספציפי במקרה של בעיות נתיב
dotenv_path = find_dotenv()
if dotenv_path:
    load_dotenv(dotenv_path, override=True)
else:
    load_dotenv()

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# 2. ייבוא רכיבי הליבה רק לאחר טעינת הסביבה
from root_brain import RootBrain
from memory import RootMemory

#=====
# פונקציית אבחון לפני עליית רכיבי ה-AI
def check_api_health():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return False, "מפתח OPENAI_API_KEY חסר בקובץ ההגדרות."
    return True, f"המפתח זוהה (מתחיל ב-{api_key[:7]}...)"
#=====

# 3. אתחול השרת
app = FastAPI(title="Root Agentic OS - MCP Bridge", version="1.0.0")

# צופה פני עתיד: איפשור גישה מכל מקור (CORS) - קריטי עבור חיבור ה-VS Code Extension בהמשך
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. אתחול בטוח (Safe Boot) - מונע קריסה מוחלטת של הטרמינל אם המפתח חסר
brain = None
memory = None
startup_error = None

try:
    # אבחון מוקדם לפני ניסיון הדלקת המוח והזיכרון
    is_healthy, health_msg = check_api_health()
    print(f"[Root_Diag] {health_msg}")
    
    if not is_healthy:
        raise Exception(health_msg)

    brain = RootBrain()
    memory = RootMemory()
except Exception as e:
    startup_error = str(e)
    print(f"⚠️ אזהרה קריטית: רכיבי ה-AI לא עלו. בדוק את מפתח ה-API ב-.env. שגיאה: {startup_error}")

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
        raise HTTPException(status_code=503, detail="Memory module is currently offline.")
    results = memory.search(query_string)
    return {"query": query_string, "results": results}

@app.post("/execute")
async def execute_command(request: CommandRequest):
    """הרצת פקודות טרמינל מאובטחות"""
    if not brain:
        raise HTTPException(status_code=503, detail="Brain module is currently offline.")
    result = brain.execute_action(request.command)
    return {"command": request.command, "result": result}

if __name__ == "__main__":
    # שימוש במחרוזת "main:app" מאפשר ל-reload לעבוד בצורה יציבה יותר ב-Windows
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)