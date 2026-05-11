# =====
import os
from dotenv import load_dotenv
# =====

# =====
load_dotenv()
# =====

# =====
class Config:
    # הגדרות LLM וגישה ל-API
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    BASE_URL = os.getenv("BASE_URL", "https://openrouter.ai/api/v1")
    MODEL = os.getenv("MODEL", "openai/gpt-4o")
    
    # נתיבי מערכת
    MANIFEST_PATH = os.getenv("MANIFEST_PATH", "ROOT.md")
    
    # --- תשתית רב-לשונית (צופה פני עתיד) ---
    # כאן המערכת מחליטה באיזו שפה לדווח למשתמש (Hebrew, Russian, English וכו')
    UI_LANGUAGE = os.getenv("UI_LANGUAGE", "Hebrew")
    
    # --- הגדרות GitHub (לסנכרון ענני) ---
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY") # פורמט: username/repo
    
    # --- הגדרות Orchestrator (ניהול זמנים) ---
    POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "60"))       # בדיקת משימות כל דקה
    PROACTIVE_INTERVAL = int(os.getenv("PROACTIVE_INTERVAL", "3600")) # יזימת שיפורים כל שעה
    
    # --- תקשורת Bridge (MCP) ---
    MCP_URL = os.getenv("MCP_URL", "http://127.0.0.1:8000")
# =====
