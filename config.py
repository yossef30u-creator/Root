import os
from pathlib import Path
from dotenv import load_dotenv

# טעינה של ה-.env
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    # הוספנו .strip() כדי להוריד רווחים או תווים נסתרים מהמפתח
    raw_key = os.getenv("OPENAI_API_KEY", "")
    OPENAI_API_KEY = raw_key.strip().strip('"').strip("'")
    
    BASE_URL = "https://openrouter.ai/api/v1"
    MODEL = "openai/gpt-4o"
    
    LOG_PATH = ".root/logs/context_history.md"
    MANIFEST_PATH = "ROOT.md"
