#!/usr/bin/env python3
# =====
import os
import sys
import fnmatch
import time
from pathlib import Path

# --- מנגנון הזרקת נתיבים מפלצתי (Self-Healing Paths) ---
CURRENT_FILE = os.path.abspath(__file__)
CORE_DIR = os.path.dirname(CURRENT_FILE)
ROOT_OS_DIR = os.path.dirname(CORE_DIR)
PROJECT_ROOT = os.path.dirname(ROOT_OS_DIR)

for path in [PROJECT_ROOT, ROOT_OS_DIR, CORE_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

# ייבוא חכם ועמיד לקריסות
try:
    from root_os.memory import RootMemory
    from root_os.core.root_handler import update_manifest
    from root_os.core.config_manager import Config
    
    # טעינת הסוכנים הנוספים בכוח
    try:
        from root_os.core.history_handler import agentic_history_sync
        from root_os.core.roadmap_handler import agentic_roadmap_sync
        AGENTS_AVAILABLE = True
    except ImportError:
        AGENTS_AVAILABLE = False

except ImportError:
    try:
        from memory import RootMemory
        from root_handler import update_manifest
        from config_manager import Config
        from history_handler import agentic_history_sync
        from roadmap_handler import agentic_roadmap_sync
        AGENTS_AVAILABLE = True
    except ImportError as e:
        print(f"❌ [Fatal Error] המערכת קורסת. חסר קובץ ליבה: {e}")
        sys.exit(1)
# =====

IGNORE_DIRS = {'.git', '__pycache__', 'node_modules', 'venv', 'env', '.root', 'dist', 'build', '.idea', '.vscode'}
IGNORE_EXTS = {'.pyc', '.exe', '.bin', '.pdf', '.jpg', '.jpeg', '.png', '.zip', '.tar', '.gz', '.DS_Store', '.mp4'}

class ProjectScanner:
    def __init__(self, project_path):
        self.project_path = os.path.abspath(project_path)
        
        if not Config.API_KEY:
            print("⚠️ [Scanner Warning] מפתח API חסר. הזיכרון הוקטורי עלול לא לעבוד כראוי.")
            
        self.memory = RootMemory()
        self.files_count = 0
        self.total_size_kb = 0
        self.user_ignore_patterns = self._load_rootignore()
        self.collected_content = [] # [תוספת] אוסף קוד אמיתי עבור ה-AI

    def _load_rootignore(self):
        patterns = []
        ignore_file = os.path.join(self.project_path, ".rootignore")
        if os.path.exists(ignore_file):
            try:
                with open(ignore_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            patterns.append(line)
                print(f"🛡️  נטענו {len(patterns)} חוקי סינון מ-.rootignore")
            except Exception:
                pass
        return patterns

    def _is_user_ignored(self, file_path):
        for pattern in self.user_ignore_patterns:
            if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(os.path.basename(file_path), pattern):
                return True
        return False

    def scan(self):
        print(f"\n🚀 [Monster Scanner V2] מתחיל סריקת עומק פסיכוטית ב:\n📂 {self.project_path}")
        print("-" * 50)
        start_time = time.time()
        
        file_structure = []
        
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not self._is_user_ignored(os.path.join(root, d))]
            
            for file in files:
                if any(file.endswith(ext) for ext in IGNORE_EXTS):
                    continue
                    
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, self.project_path)
                
                if self._is_user_ignored(rel_path):
                    continue
                
                try:
                    print(f"⏳ מאנדקס: {rel_path[:50].ljust(50)}", end='\r')
                    
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if not content.strip(): continue
                        
                        file_size_kb = len(content) / 1024
                        self.total_size_kb += file_size_kb
                        
                        # איסוף התוכן עבור ה-AI (מוגבל ל-20 קבצים ו-1000 תווים לקובץ למניעת עומס עוקבים)
                        if self.files_count < 20:
                             self.collected_content.append(f"--- File: {rel_path} ---\n{content[:1000]}")
                        
                        if len(content) > 50000:
                            content = content[:50000] + "\n\n... [Content Truncated due to size limits] ..."
                        
                        self.memory.add_memory(
                            text=f"File: {rel_path}\nContent:\n{content}",
                            metadata={"path": rel_path, "action": "initial_scan", "size_kb": round(file_size_kb, 1)}
                        )
                        file_structure.append(rel_path)
                        self.files_count += 1
                except Exception as e:
                    print(f"\n⚠️ דילגתי על {rel_path} עקב שגיאה: {e}")

        print(" " * 70, end='\r')
        self._finalize(file_structure, time.time() - start_time)

    def _finalize(self, file_list, duration):
        print(f"\n🧠 [Monster Brain] מעבד תובנות ומפעיל את 'השילוש הקדוש'...")
        
        # בניית פרומפט חזק ועשיר בקונטקסט אמיתי מהקוד
        project_context = "\n".join(self.collected_content)
        analysis_payload = f"INITIAL SYSTEM SCAN.\nTotal Files: {self.files_count}\n\nKey File Contents:\n{project_context}"
        critic_payload = "Initial scan completed. Baseline architecture needs to be established. Please generate documentation based on the provided code content."

        # 1. אדריכל (ROOT.md)
        try:
            print("🏗️  מאלץ יצירת ארכיטקטורה אמיתית (ROOT.md)...")
            update_manifest(analysis_payload, critic_payload)
            print("✅ ROOT.md נוצר/עודכן בהצלחה.")
        except Exception as e:
            print(f"⚠️ שגיאה בעדכון ROOT.md: {e}")

        # 2. שאר הסוכנים בכוח (אם זמינים)
        if AGENTS_AVAILABLE:
            try:
                print("📜 מאלץ כתיבת היסטוריה (HISTORY.md)...")
                agentic_history_sync(analysis_payload, critic_payload)
                print("✅ HISTORY.md נוצר/עודכן בהצלחה.")
                
                print("🗺️  מאלץ כתיבת רודמאפ (ROADMAP.md)...")
                agentic_roadmap_sync(analysis_payload, critic_payload)
                print("✅ ROADMAP.md נוצר/עודכן בהצלחה.")
            except Exception as e:
                print(f"⚠️ שגיאה בהפעלת סוכני משנה: {e}")

        print("-" * 50)
        print(f"✨ [Root] התשתית הושלמה. 'השילוש הקדוש' מוכן.")
        print(f"📊 סטטיסטיקה: {self.files_count} קבצים | {self.total_size_kb:.1f} KB | זמן: {duration:.2f} שניות.")
        print("-" * 50)

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    ProjectScanner(target).scan()