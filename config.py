import os
from pathlib import Path
from dotenv import load_dotenv

# טעינה של ה-.env מהתיקייה הנוכחית
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    BASE_URL = "https://openrouter.ai/api/v1"
    MODEL = "openai/gpt-4o"
    
    LOG_PATH = ".root/logs/context_history.md"
    MANIFEST_PATH = "ROOT.md"
