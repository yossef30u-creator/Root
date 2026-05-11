import sys
import os
import time
import json
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# זמן המתנה (שניות) בין הפעלות כדי למנוע הצפת בקשות (Debounce)
COOLDOWN_SECONDS = 15

# מילון לשמירת זמן הפעלה אחרון *לכל פרויקט בנפרד* (Multi-project support)
project_last_triggers = {}

# קבצים ותיקיות בסיס שרות תתעלם מהם
BASE_IGNORE_LIST = [
    '.git', '__pycache__', 'node_modules', 'venv', 'env',
    'ROOT.md', 'HISTORY.md', 'ROADMAP.md', '.root_config',
    '.root_core_dump.json', '.DS_Store', '.rootignore'
]

REGISTRY_PATH = os.path.expanduser('~/.root_projects_registry.json')

class CodeChangeHandler(FileSystemEventHandler):
    def __init__(self, project_path, ingestor_script):
        self.project_path = project_path
        self.ingestor_script = ingestor_script
        self.ignore_list = self._load_dynamic_ignore()

    def _load_dynamic_ignore(self):
        """טוען התעלמויות מהקובץ .rootignore של הפרויקט הספציפי"""
        combined_ignore = set(BASE_IGNORE_LIST)
        rootignore_path = os.path.join(self.project_path, '.rootignore')
        
        if os.path.exists(rootignore_path):
            try:
                with open(rootignore_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        clean_line = line.strip()
                        if clean_line and not clean_line.startswith('#'):
                            combined_ignore.add(clean_line.replace('*', ''))
            except Exception as e:
                print(f"⚠️ [Root Service] Failed to read .rootignore in {self.project_path}: {e}")
                
        return list(combined_ignore)

    def is_ignored(self, path):
        for ignored_item in self.ignore_list:
            if ignored_item in path:
                return True
        return False

    def trigger_ingestor(self, event, action_name):
        if event.is_directory or self.is_ignored(event.src_path):
            return

        current_time = time.time()
        last_trigger = project_last_triggers.get(self.project_path, 0)

        # בדיקת Cooldown פרטנית לפרויקט הזה בלבד
        if current_time - last_trigger > COOLDOWN_SECONDS:
            project_last_triggers[self.project_path] = current_time
            filename = os.path.basename(event.src_path)
            
            # הדפסה נקייה שמראה באיזה פרויקט קרה השינוי
            project_name = os.path.basename(self.project_path)
            print(f'\n👀 [{project_name}] זיהיתי שקובץ {action_name}: {filename}')
            print(f'🧠 [{project_name}] מעירה את ה-Ingestor לניתוח...')

            try:
                # הרצת Ingestor ברקע עבור הפרויקט הספציפי
                subprocess.Popen(
                    [sys.executable, self.ingestor_script, self.project_path],
                    stdout=subprocess.DEVNULL, # מונע הצפת הטרמינל הגלובלי בלוגים
                    stderr=subprocess.DEVNULL
                )
            except Exception as e:
                print(f"❌ [Root Service] שגיאה בהפעלת Ingestor עבור {project_name}: {e}")

    def on_modified(self, event):
        self.trigger_ingestor(event, "השתנה")

    def on_created(self, event):
        self.trigger_ingestor(event, "נוצר")

    def on_deleted(self, event):
        self.trigger_ingestor(event, "נמחק")

    def on_moved(self, event):
        self.trigger_ingestor(event, "שינה מיקום/שם")

def load_registry():
    """קורא את הרג'יסטרי הגלובלי כדי לדעת על אילו פרויקטים להשגיח"""
    if os.path.exists(REGISTRY_PATH):
        try:
            with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def main():
    core_dir = os.path.dirname(os.path.abspath(__file__))
    ingestor_script = os.path.join(core_dir, 'ingestor.py')

    if not os.path.exists(ingestor_script):
        print(f'❌ [Critical Error] לא מצאתי את מנוע הליבה: {ingestor_script}')
        sys.exit(1)

    observer = Observer()
    observer.start()
    print('🌍 [Root Global Service] המנוע התעורר. משגיח על כל הפרויקטים ברקע...')

    active_watches = {} # מילון לשמירת המעקבים הפעילים: project_path -> watch_instance

    try:
        # לולאה ראשית - Hot Reloading
        while True:
            registry = load_registry()
            current_projects = set(registry.keys())
            watched_projects = set(active_watches.keys())

            # 1. הוספת פרויקטים חדשים (משתמש עשה root בתיקייה חדשה)
            for proj in current_projects - watched_projects:
                if os.path.exists(proj):
                    handler = CodeChangeHandler(proj, ingestor_script)
                    watch = observer.schedule(handler, proj, recursive=True)
                    active_watches[proj] = watch
                    print(f"👁️  [Root Service] מחובר כעת לפרויקט: {os.path.basename(proj)}")

            # 2. הסרת פרויקטים שכבר לא קיימים במחשב
            for proj in watched_projects - current_projects:
                observer.unschedule(active_watches[proj])
                del active_watches[proj]
                # מנקה גם את מילון הזמנים כדי לא לצבור זבל בזיכרון
                if proj in project_last_triggers:
                    del project_last_triggers[proj]
                print(f"🚫 [Root Service] מנותק מהפרויקט (הוסר): {os.path.basename(proj)}")

            # בדיקה כל 5 שניות אם נרשמו פרויקטים חדשים
            time.sleep(5)
            
    except KeyboardInterrupt:
        print('\n🛑 [Root Global Service] מכבה מנועים...')
        observer.stop()
    
    observer.join()

if __name__ == '__main__':
    main()
