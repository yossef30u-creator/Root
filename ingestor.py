import os
import subprocess
from openai import OpenAI
from dotenv import load_dotenv

# טעינת המפתח באופן מאובטח מקובץ .env
load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENAI_API_KEY"),
)

def get_git_diff():
    try:
        # קבלת השינויים מהקומיט האחרון
        result = subprocess.run(['git', 'diff', 'HEAD~1', 'HEAD'], capture_output=True, text=True)
        return result.stdout
    except:
        return ""

def analyze_diff_with_ai(diff_text):
    if not diff_text.strip(): return None
    
    print("[Root] Analyzing architectural impact...")
    prompt = f"Analyze this code diff and provide a 2-line summary of its impact on the project architecture:\n\n{diff_text}"
    
    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

def update_root_manifest(analysis):
    """מעדכן את קובץ ה-ROOT.md הראשי עם הסטטוס החדש"""
    manifest_path = "ROOT.md"
    if not os.path.exists(manifest_path): return

    with open(manifest_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # חיפוש שורת הסטטוס לעדכון
    with open(manifest_path, "w", encoding="utf-8") as f:
        for line in lines:
            if line.startswith("> **Status:**"):
                f.write(f"> **Status:** Last Update - {analysis[:100]}...\n")
            else:
                f.write(line)

def save_to_logs(analysis):
    log_path = ".root/logs/context_history.md"
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n## Update\n{analysis}\n")

if __name__ == "__main__":
    diff = get_git_diff()
    analysis = analyze_diff_with_ai(diff)
    if analysis:
        save_to_logs(analysis)
        update_root_manifest(analysis)
        print("[Root] Context Updated Successfully.")
