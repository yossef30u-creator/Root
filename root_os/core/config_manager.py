import os
import sys
import json

# הנתיב הגלובלי שבו נשמרים המפתחות של המשתמש
CONFIG_PATH = os.path.expanduser("~/.root_config")

# [תוספת] רשימת מפתחות ברירת המחדל כדי לוודא ששום דבר לא חסר למשתמשים ישנים
DEFAULT_CONFIG = {
    "API_KEY": "",
    "GITHUB_TOKEN": "",
    "BASE_URL": "https://openrouter.ai/api/v1",
    "MODEL": "google/gemini-pro-1.5",
    "UI_LANGUAGE": "Hebrew",
    "USER_CREDITS": 1000,
    "VERSION": "1.0.0"
}

class ConfigManager:
    """
    מחלקת הזיכרון של רות. 
    היא טוענת את המפתחות מהקובץ הנסתר ודואגת שכל שאר הקבצים (Ingestor, GitHub handlers וכו')
    יוכלו להשתמש בהם בלי לדעת מאיפה הם הגיעו.
    כוללת מנגנון הגירה (Migration) שמוסיף הגדרות חדשות אוטומטית.
    """
    def __init__(self):
        self.API_KEY = ""
        self.GITHUB_TOKEN = ""
        self.BASE_URL = "https://openrouter.ai/api/v1"
        self.MODEL = "google/gemini-pro-1.5"
        self.UI_LANGUAGE = "Hebrew" # שפת העצות של רות
        
        self._migrate_config() # [תוספת] מוודא שהקובץ קיים ושלם לפני הטעינה
        self._load_config()

    def _migrate_config(self):
        """
        [תוספת] מנגנון הגירה שקט: משווה את הקובץ הקיים מול ברירת המחדל
        ומוסיף מפתחות חסרים מבלי למחוק את המידע שהמשתמש כבר הזין.
        """
        existing_data = {}
        needs_update = False

        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except Exception:
                pass # נטפל בזה כקובץ ריק שצריך יצירה מחדש

        updated_data = existing_data.copy()
        for key, default_val in DEFAULT_CONFIG.items():
            if key not in updated_data:
                updated_data[key] = default_val
                needs_update = True

        if needs_update or not os.path.exists(CONFIG_PATH):
            try:
                os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
                with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                    json.dump(updated_data, f, indent=4, ensure_ascii=False)
                # לא מדפיסים פה כלום כדי לא להציף את הטרמינל בכל הרצה
            except Exception as e:
                print(f"⚠️ [Config] לא הצלחתי לעדכן את קובץ ההגדרות: {e}")

    def _load_config(self):
        if not os.path.exists(CONFIG_PATH):
            print(f"❌ [Config] לא מצאתי את קובץ ההגדרות בנתיב {CONFIG_PATH}")
            print("👉 בבקשה תריץ את boot.py כדי להגדיר את המפתחות שלך.")
            sys.exit(1)

        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # טעינת הנתונים
                self.API_KEY = data.get("API_KEY", "")
                self.GITHUB_TOKEN = data.get("GITHUB_TOKEN", "")
                self.BASE_URL = data.get("BASE_URL", self.BASE_URL)
                self.MODEL = data.get("MODEL", self.MODEL)
                self.UI_LANGUAGE = data.get("UI_LANGUAGE", self.UI_LANGUAGE)
                
                # הזרקת הנתונים למשתני הסביבה (Backwards Compatibility)
                # כדי שקוד ישן שעובד עם os.environ ימשיך לעבוד כרגיל
                os.environ["OPENAI_API_KEY"] = self.API_KEY
                os.environ["GITHUB_TOKEN"] = self.GITHUB_TOKEN
                
        except Exception as e:
            print(f"❌ [Config] שגיאה בקריאת קובץ ההגדרות: {e}")
            sys.exit(1)

# יצירת מופע יחיד (Singleton)
# כל קובץ שיעשה import יקבל בדיוק את אותו המידע
Config = ConfigManager()