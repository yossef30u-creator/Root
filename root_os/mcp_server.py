# =====
import os
from fastapi import FastAPI, Query, Body
from memory import RootMemory
from actions import RootActions
from config import Config
import uvicorn

# =====

# =====
app = FastAPI(title="Root Agentic OS - MCP Bridge")
mem = RootMemory()
act = RootActions()
# =====


# =====
@app.get("/query")
def query_root_memory(q: str = Query(..., description="The semantic search query")):
    """שליפת הקשר סמנטי מהזיכרון הוקטורי"""
    results = mem.search(q, top_k=3)
    return {
        "query": q,
        "context": [
            {
                "score": float(r[0]),
                "file": r[1]["metadata"].get("file"),
                "content": r[1]["text"],
            }
            for r in results
        ],
    }


# =====


# =====
@app.post("/execute")
def execute_action(payload: dict = Body(...)):
    """ביצוע פקודת טרמינל דרך ה-Root"""
    command = payload.get("command")
    if not command:
        return {"error": "No command provided"}
    result = act.execute_command(command)
    return {"command": command, "output": result}


# =====

# =====
if __name__ == "__main__":
    # וודא שהשרת רץ על 0.0.0.0 כדי שנוכל לגשת אליו
    uvicorn.run(app, host="0.0.0.0", port=8000)
# =====
