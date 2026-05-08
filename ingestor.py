import os
import subprocess
from openai import OpenAI

# הגדרת הלקוח של OpenAI (דורש משתנה סביבה OPENAI_API_KEY)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_git_diff():
    """קורא את השינויים בין הקומיט הנוכחי לקודם"""
    try:
        # בודק את ה-diff של הקומיט האחרון
        result = subprocess.run(['git', 'diff', 'HEAD~1', 'HEAD'], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        print(f"[Error] Failed to get git diff: {e}")
        return ""

def analyze_diff_with_ai(diff_text):
    """שולח את ה-diff לניתוח סמנטי ב-GPT-4o"""
    if not diff_text.strip():
        return "No code changes detected."
        
    print("[Ingestor] Analyzing diff with Semantic Engine (GPT-4o)...")
    
    prompt = f"""
    You are the Root Semantic Engine. 
    Analyze the following code diff and summarize its architectural and business logic impact.
    Keep it concise. Do not just list the changed lines, explain *why* it matters.
    
    Diff:
    {diff_text}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[Error] Semantic analysis failed: {e}"

def update_memory(analysis):
    """שומר את הניתוח לתוך זיכרון המערכת"""
    log_path = ".root/logs/latest_analysis.md"
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("# Latest Context Update\n\n")
        f.write(analysis)
    print(f"[Ingestor] Memory updated successfully at {log_path}")

if __name__ == "__main__":
    print("🌳 Root Ingestor initialized.")
    diff = get_git_diff()
    
    if diff:
        analysis = analyze_diff_with_ai(diff)
        update_memory(analysis)
    else:
        print("[Ingestor] No diff found. Make sure this is a Git repository with at least 2 commits.")
