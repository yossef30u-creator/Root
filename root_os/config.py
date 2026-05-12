# =====
import os
import atexit
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

    # --- הגדרות איכות כתיבה וטוקנים ---
    # מגדיל את רף הקיצוץ של ה-Ingestor כדי למנוע איבוד הקשר (Context)[span_3](start_span)[span_3](end_span)[span_4](start_span)[span_4](end_span)
    TOKEN_GUARD_LIMIT = int(os.getenv("TOKEN_GUARD_LIMIT", "100000"))
    # טמפרטורה נמוכה מבטיחה תיעוד טכני מדויק ועקבי[span_5](start_span)[span_5](end_span)
    AGENT_TEMPERATURE = float(os.getenv("AGENT_TEMPERATURE", "0.2"))

    # נתיבי מערכת ומניפסטים
    MANIFEST_PATH = os.getenv("MANIFEST_PATH", "ROOT.md")

    # --- הגדרות זיכרון (RAG) ---
    # שליטה בכמות פיסות המידע שה-AI שולף מהזיכרון הווקטורי[span_6](start_span)[span_6](end_span)
    RAG_TOP_K = int(os.getenv("RAG_TOP_K", "5"))
    VECTOR_DB_TYPE = os.getenv(
        "VECTOR_DB_TYPE", "ChromaDB"
    )  # [span_7](start_span)[span_7](end_span)[span_8](start_span)[span_8](end_span)

    # --- תשתית רב-לשונית (צופה פני עתיד) ---
    UI_LANGUAGE = os.getenv("UI_LANGUAGE", "Hebrew")

    # --- הגדרות GitHub (לסנכרון ענני) ---
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")

    # --- הגדרות Orchestrator (ניהול זמנים) ---
    POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "60"))
    PROACTIVE_INTERVAL = int(os.getenv("PROACTIVE_INTERVAL", "3600"))

    # --- תקשורת Bridge (MCP) ---
    MCP_URL = os.getenv("MCP_URL", "http://127.0.0.1:8000")


# =====


# =====
def cleanup_on_exit():
    """
    פונקציית ניקוי המופעלת אוטומטית בסיום הריצה דרך atexit.
    מבטיחה שחרור נעילות מערכת בצורה בטוחה[span_9](start_span)[span_9](end_span)[span_10](start_span)[span_10](end_span)[span_11](start_span)[span_11](end_span).
    """
    # כאן יבוצע שחרור הקובץ .root.lock במידה והוא קיים[span_12](start_span)[span_12](end_span)[span_13](start_span)[span_13](end_span)
    pass


atexit.register(cleanup_on_exit)
# =====
