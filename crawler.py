#!/usr/bin/env python3
import os
from memory import RootMemory

# תיקיות שאנחנו רוצים שהסורק יתעלם מהן כדי לחסוך מקום וטוקנים
IGNORE_DIRS = ['.git', '.root', 'venv', '__pycache__']
# סוגי קבצים שחשובים ל-Context של הפרויקט
ALLOWED_EXTENSIONS = ['.py', '.md']

def crawl_project():
    print("🕷️ [Crawler] Starting full project scan...")
    mem = RootMemory()
    files_indexed = 0

    # ריצה על כל הקבצים והתיקיות בפרויקט
    for root_dir, dirs, files in os.walk('.'):
        # סינון התיקיות שברשימת ההתעלמות
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            if any(file.endswith(ext) for ext in ALLOWED_EXTENSIONS):
                file_path = os.path.join(root_dir, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # דילוג על קבצים ריקים
                    if not content.strip():
                        continue

                    # יצירת ה"זיכרון" שישמר במסד הנתונים
                    memory_text = f"File Path: {file_path}\nFile Content:\n{content}"
                    metadata = {"type": "file_crawl", "file": file_path}
                    
                    # הוספה לזיכרון הוקטורי (זה גם שולח ל-OpenAI להמרה לוקטור)
                    mem.add_memory(text=memory_text, metadata=metadata)
                    print(f"✅ Indexed: {file_path}")
                    files_indexed += 1
                    
                except Exception as e:
                    print(f"❌ Failed to read or index {file_path}: {e}")

    print(f"\n🎉 [Crawler] Crawl complete! {files_indexed} core files added to Vector Memory.")

if __name__ == "__main__":
    crawl_project()
