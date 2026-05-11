#!/usr/bin/env python3
# =====
import os
import sys
import fnmatch
from pathlib import Path

# --- וידוא שניתן לייבא את הקבצים הפנימיים שלנו ---
CORE_DIR = os.path.dirname(os.path.abspath(__file__))
if CORE_DIR not in sys.path:
    sys.path.append(CORE_DIR)

from memory import RootMemory
from root_handler import update_manifest
from config_manager import Config # נטען כדי לוודא שההגדרות קיימות
# =====

# רשימת התעלמות - לא סורקים זבל
IGNORE_DIRS = {'.git', '__pycache__', 'node_modules', 'venv', 'env', '.root', 'dist', 'build'}
IGNORE_EXTS = {'.pyc', '.exe', '.bin', '.pdf', '.jpg', '.png', '.zip', '.DS_Store'}

class ProjectScanner:
    def __init__(self, project_path):
        self.project_path = os.path.abspath(project_path)
        self.memory = RootMemory()
        self.files_count = 0
        self.user_ignore_patterns = self._load_rootignore()

    def _load_rootignore(self):
        """טוען את החוקים המותאמים אישית של המשתמש מקובץ .rootignore"""
        patterns = []
        ignore_file = os.path.join(self.project_path, ".rootignore")
        if os.path.exists(ignore_file):
            try:
                with open(ignore_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            patterns.append(line)
            except Exception:
                pass
        return patterns

    def _is_user_ignored(self, file_path):
        """בודק אם הקובץ נמצא ברשימת ההתעלמות של המשתמש"""
        for pattern in self.user_ignore_patterns:
            if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(os.path.basename(file_path), pattern):
                return True
        return False

    def scan(self):
        print(f"🔍 [Root Scanner] מתחיל סריקת עומק: {self.project_path}")
        
        file_structure = []
        
        for root, dirs, files in os.walk(self.project_path):
            # סינון תיקיות חכם (ברירת מחדל + מה שהמשתמש הוסיף)
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not self._is_user_ignored(os.path.join(root, d))]
            
            for file in files:
                if any(file.endswith(ext) for ext in IGNORE_EXTS):
                    continue
                    
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, self.project_path)
                
                # התעלמות מקבצים שהמשתמש ביקש
                if self._is_user_ignored(rel_path):
                    continue
                
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if not content.strip(): continue
                        
                        # [גימור] הגנה נגד קבצים ענקיים שייחנקו את הזיכרון (Token Budgeting בסיסי)
                        if len(content) > 50000:
                            content = content[:50000] + "\n\n... [Content Truncated due to size] ..."
                        
                        # הזרקה לזיכרון הוקטורי של רות
                        print(f"📄 מאנדקס: {rel_path}")
                        self.memory.add_memory(
                            text=f"File: {rel_path}\nContent:\n{content}",
                            metadata={"path": rel_path, "action": "initial_scan"}
                        )
                        file_structure.append(rel_path)
                        self.files_count += 1
                except Exception as e:
                    print(f"⚠️ דילגתי על {rel_path} עקב שגיאה: {e}")

        # עדכון המניפסט (ROOT.md)
        self._finalize(file_structure)

    def _finalize(self, file_list):
        analysis = f"סריקה ראשונית הושלמה. נמצאו {self.files_count} קבצים רלוונטיים."
        critic = "הפרויקט אונדקס בהצלחה בזיכרון הוקטורי. רות מוכנה לעבודה עם הקשר מלא."
        update_manifest(analysis, critic)
        print(f"\n✨ [Root] הסריקה הסתיימה. {self.files_count} קבצים בזיכרון.")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    ProjectScanner(target).scan()