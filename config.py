# =====
import os
from dotenv import load_dotenv
# =====

# =====
load_dotenv()
# =====

# =====
class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    BASE_URL = os.getenv("BASE_URL", "https://openrouter.ai/api/v1")
    MODEL = os.getenv("MODEL", "openai/gpt-4o")
    MANIFEST_PATH = "ROOT.md"
# =====
