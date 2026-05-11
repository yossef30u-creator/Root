#!/usr/bin/env python3
import os
import json
import time
import re
from openai import OpenAI
from dotenv import load_dotenv

# אתחול נתיבים וטעינת קובץ ההגדרות
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

# אתחול הלקוח של OpenRouter - כתובות נקיות כטקסט פשוט בלבד!
client = OpenAI(
    base_url=os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1"),
    api_key=os.getenv("OPENAI_API_KEY"),
    default_headers={
        "HTTP-Referer": "https://github.com/RootProject", 
        "X-Title": "Root Agentic OS"
    }
)

def clean_json_response(text):
    """
    מנקה סימני Markdown ותווים מיותרים שה-AI לפעמים מוסיף, 
    כדי להבטיח שפיענוח ה-JSON יצליח תמיד.
    """
    cleaned_text = re.sub(r'^