#!/usr/bin/env python3
import os
import subprocess
from datetime import datetime
from openai import OpenAI
from config import Config
from memory import RootMemory

# הגדרת נתיבי עבודה מדויקים
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_DIR)

# וידוא שקובץ ה-.env מוגדר כראוי
if not Config.OPENAI_API_KEY:
    print("❌ [Critical Error] API Key missing! Check your .env file.")
    exit(1)

# אתחול הלקוח של OpenAI לתהליך הניתוח הסמנטי
client = OpenAI(
    base_url=Config.BASE_URL,
    api_key=Config.OPENAI_API_KEY,
    default_headers={
        "HTTP-Referer": "https://github.com/RootProject",
        "X-Title": "Root Agentic OS",
    }
)

def get_git_info():
    """שואב את פרטי הקומיט והשינויים מ-Git"""
    try:
        # שליפת ה-Diff של הקוד
        diff_result = subprocess.run(['git', 'diff', 'HEAD~1', 'HEAD'], capture_output=True, text=True)
        # שליפת היסטוריית הקומיט (מחבר, תאריך, הודעה) עבור ה-Metadata
        log_result = subprocess.run(['git', 'log', '-1', '--pretty=format:%h|%an|%s'], capture_output=True, text=True)
        
        diff_text = diff_result.stdout.strip()
        log_text = log_result.stdout.strip()
        
        if not diff_text:
            return None, None
            
        commit_hash, author, message = log_text.split('|', 2)
        metadata = {
            "commit": commit_hash,
            "author": author,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        return diff_text, metadata
    except Exception as e:
        print(f"❌ [Error] Git tracking failed: {e}")
        return None, None

def analyze_diff(diff_text):
    """(Synthesis) מנתח את ההשפעה הארכיטקטונית בעזרת ה-LLM"""
    print(f"[Root] Analyzing semantic impact with {Config.MODEL}...")
    prompt = f"Analyze this code diff and provide a short, 1-2 sentence summary of its impact on the project architecture. Focus on logic and structure:\n\n{diff_text}"
    
    try:
        response = client.chat.completions.create(
            model=Config.MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ [API Error]: Semantic Engine failed. Details: {e}")
        return None

def update_manifest(analysis):
    """מעדכן את קובץ ה-ROOT.md (זיכרון לטווח קצר וסטטוס)"""
    if os.path.exists(Config.MANIFEST_PATH):
        with open(Config.MANIFEST_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        with open(Config.MANIFEST_PATH, "w", encoding="utf-8") as f:
            for line in lines:
                if line.startswith("> **Status:**"):
                    clean_analysis = analysis.replace('\n', ' ')
                    f.write(f"> **Status:** Last Update - {clean_analysis}\n")
                else:
                    f.write(line)
        print("✅ [Root] ROOT.md updated with fresh context.")

if __name__ == "__main__":
    # 1. Trigger & Analysis
    diff, metadata = get_git_info()
    
    if diff:
        # 2. Synthesis
        analysis = analyze_diff(diff)
        
        if analysis:
            # 3. Persistence - Short Term Memory (Markdown)
            update_manifest(analysis)
            
            # 4. Persistence - Long Term Memory (Vector DB)
            root_memory = RootMemory()
            memory_saved = root_memory.add_memory(
                text=analysis, 
                metadata=metadata
            )
            
            if memory_saved:
                print("🚀 [Root] Continuous Context Loop Completed Successfully.")
        else:
            print("⚠️ [Root] Update aborted due to API error. Files preserved.")
    else:
        print("ℹ️ [Root] No structural changes found. Commit some files first.")
