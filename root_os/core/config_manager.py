import os
import sys
import json

CONFIG_PATH = os.path.expanduser("~/.root_config")

DEFAULT_CONFIG = {
    "API_KEY": "",
    "GITHUB_TOKEN": "",
    "BASE_URL": "https://openrouter.ai/api/v1",
    "MODEL": "openai/gpt-4o",
    "UI_LANGUAGE": "Hebrew",
    "USER_CREDITS": 1000,
    "VERSION": "1.0.0",
}


class ConfigManager:
    """
    מחלקת התצורה (Configuration) המרכזית של Root OS.
    פועלת כ"מוח שואב" - מחפשת מפתחות והגדרות מכל מקור אפשרי:
    1. משתני סביבה קיימים (OS).
    2. קובץ .env מקומי (פיתוח).
    3. קובץ ~/.root_config (התקנה גלובלית).

    בנוסף, דואגת להגירה ולשמירה על מבנה אחיד.
    """

    def __init__(self):
        # אתחול ה-State הפנימי עם ערכי ברירת מחדל
        self._state = DEFAULT_CONFIG.copy()

        # שלב 1: הגירה ווידוא קובץ גלובלי
        self._ensure_global_config_exists()

        # שלב 2: שאיבת הנתונים מכל המקורות לפי סדר עדיפות
        self._load_all_sources()

        # שלב 3: חשיפת הערכים החשובים ישירות על ה-Object לנוחות
        self.API_KEY = self.get("API_KEY")
        self.GITHUB_TOKEN = self.get("GITHUB_TOKEN")
        self.BASE_URL = self.get("BASE_URL")
        self.MODEL = self.get("MODEL")
        self.UI_LANGUAGE = self.get("UI_LANGUAGE")

        # שלב 4: הזרקת הנתונים למערכת כדי שספריות (כמו OpenAI) ימצאו אותם
        self._inject_to_environment()

        # שלב 5: בקרת איכות - אם המפתח הראשי ריק, אנחנו בבעיה
        self._validate_critical_keys()

    def _ensure_global_config_exists(self):
        """מנגנון הגירה שקט - מוודא שהקובץ ב- ~/.root_config קיים ומעודכן"""
        existing_data = {}
        needs_update = False

        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
            except Exception:
                pass  # נטפל כקובץ פגום

        updated_data = existing_data.copy()
        for key, default_val in DEFAULT_CONFIG.items():
            if key not in updated_data:
                updated_data[key] = default_val
                needs_update = True

        if needs_update or not os.path.exists(CONFIG_PATH):
            try:
                os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
                with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                    json.dump(updated_data, f, indent=4, ensure_ascii=False)
            except Exception as e:
                print(f"⚠️ [Config] אזהרה: לא הצלחתי לכתוב ל- {CONFIG_PATH}: {e}")

    def _load_all_sources(self):
        """
        הליבה של המפלצת: טוענת נתונים בשכבות.
        השכבה העליונה דורסת את התחתונה.
        סדר העדיפויות (מהחלש לחזק):
        1. ~/.root_config
        2. .env בתיקייה המקומית
        3. משתני סביבה קיימים (export בטרמינל)
        """
        # 1. טעינה מהקובץ הגלובלי
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    global_data = json.load(f)
                    self._state.update(global_data)
            except Exception:
                pass

        # 2. טעינה מ-.env מקומי (למצב פיתוח)
        env_path = os.path.join(os.getcwd(), ".env")
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if "=" in line:
                            key, val = line.split("=", 1)
                            key = key.strip()
                            val = val.strip().strip('"').strip("'")

                            # תרגום מפתחות סביבה נפוצים לפורמט הפנימי שלנו
                            if key == "OPENAI_API_KEY":
                                key = "API_KEY"

                            self._state[key] = val
            except Exception as e:
                print(f"⚠️ [Config] שגיאה בקריאת .env מקומי: {e}")

        # 3. טעינה ממשתני סביבה של מערכת ההפעלה (הכי חזק)
        if os.environ.get("OPENAI_API_KEY"):
            self._state["API_KEY"] = os.environ.get("OPENAI_API_KEY")
        if os.environ.get("GITHUB_TOKEN"):
            self._state["GITHUB_TOKEN"] = os.environ.get("GITHUB_TOKEN")

    def _inject_to_environment(self):
        """מזריק את המפתחות שגילינו חזרה ל-os.environ כדי שספריות חיצוניות יעבדו"""
        if self._state.get("API_KEY"):
            os.environ["OPENAI_API_KEY"] = self._state["API_KEY"]
        if self._state.get("GITHUB_TOKEN"):
            os.environ["GITHUB_TOKEN"] = self._state["GITHUB_TOKEN"]

    def _validate_critical_keys(self):
        """בדיקת שפיות - אם הלב של המערכת (המפתח) חסר, המערכת קורסת באלגנטיות"""
        if not self.API_KEY or self.API_KEY.strip() == "":
            print(f"\n❌ [Root OS Fatal Error] לא נמצא מפתח API חוקי!")
            print(f"🔍 חיפשתי ב-3 מקומות:")
            print(f"   1. קובץ גלובלי: {CONFIG_PATH}")
            print(f"   2. קובץ .env בתיקייה: {os.path.join(os.getcwd(), '.env')}")
            print(f"   3. משתנה סביבה: OPENAI_API_KEY")
            print(f'\n👉 פתרון: הוסף את המפתח לאחד מהמקומות הנ"ל או הרץ את boot.py')
            # אנחנו לא עושים sys.exit כאן כדי לא לקרוס באמצע ייבוא,
            # אבל מזהירים בצורה מאוד בולטת.

    def get(self, key, default=None):
        """מתודה לשליפת הגדרות בצורה דינמית"""
        return self._state.get(key, default)

    def set(self, key, value, save=False):
        """עדכון הגדרה בזמן ריצה (ואופציה לשמירה בדיסק)"""
        self._state[key] = value
        setattr(self, key, value)  # עדכון ה-Property הישיר

        if save:
            self._save_to_disk()

    def _save_to_disk(self):
        """שומר את המצב הנוכחי לקובץ הגלובלי"""
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self._state, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ [Config] שגיאה בשמירת הגדרות לדיסק: {e}")


# יצירת מופע יחיד (Singleton)
Config = ConfigManager()
