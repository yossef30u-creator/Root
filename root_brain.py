# =====
import requests
from openai import OpenAI
from config import Config
# =====

# =====
class RootBrain:
    def __init__(self, mcp_url=None):
        # צופה פני עתיד: מאפשר משיכת URL מההגדרות או שימוש בברירת מחדל מקומית
        self.mcp_url = mcp_url or getattr(Config, 'MCP_URL', "http://127.0.0.1:8000")
        
        self.client = OpenAI(
            base_url=Config.BASE_URL,
            api_key=Config.OPENAI_API_KEY,
            default_headers={"HTTP-Referer": "https://github.com/RootProject", "X-Title": "Root Agentic OS"}
        )
# =====

# =====
    def ask_memory(self, query):
        """שואב הקשר מהזיכרון דרך שרת ה-MCP"""
        try:
            res = requests.get(f"{self.mcp_url}/query", params={"query_string": query})
            if res.status_code == 200:
                return str(res.json().get("results", []))
            return "No specific memory context found."
        except:
            return "[Offline] Memory server unreachable."
# =====

# =====
    def execute_action(self, command):
        """שולח פקודה לשרת ה-MCP כדי שיבצע אותה בטרמינל"""
        try:
            res = requests.post(f"{self.mcp_url}/execute", json={"command": command}, timeout=45) # הוספת Timeout למניעת תקיעות
            if res.status_code == 200:
                return res.json().get("output", "")
            return f"⚠️ Failed: HTTP {res.status_code} - {res.text}"
        except requests.exceptions.RequestException as e:
            return f"❌ Connection Error to MCP: {e}"
# =====

# =====
    def _is_error(self, output):
        """פונקציית עזר לזיהוי שגיאות בפלט"""
        lower_output = output.lower()
        return "⚠️ failed" in lower_output or "❌ error" in lower_output or "not found" in lower_output or "syntax error" in lower_output
# =====

# =====
    def solve_task(self, task, max_retries=3):
        """
        הלולאה המרכזית: מנתח, מבצע, ומתקן בלולאה (Agentic Loop).
        עכשיו גם מחזיר (return) דו"ח מסודר ל-Orchestrator.
        """
        print(f"\n🧠 [Brain] Analyzing task: '{task}'...")
        context = self.ask_memory(task)
        execution_log = [] # שמירת יומן פעולות לטובת הדיווח לגיטהאב
        
        # צופה פני עתיד: פרומפט גמיש שלא כובל אותנו לטרמוקס בלבד
        prompt = f"""
        You are Root OS, an advanced autonomous developer agent.
        Task to achieve: {task}
        Context from memory: {context}
        
        Provide ONLY the raw terminal command to execute to achieve this task. 
        Do not include markdown blocks like ```bash, just the raw string.
        """
        
        try:
            # 1. החלטה ראשונית
            response = self.client.chat.completions.create(
                model=Config.MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            command = response.choices[0].message.content.strip().replace("`", "")
            
            # 2. ביצוע
            print(f"🛠️ [Brain] Executing: {command}")
            output = self.execute_action(command)
            execution_log.append(f"**Command:** `{command}`\n**Output:**\n```text\n{output}\n```")
            
            # 3. לולאת תיקון עצמי - ינסה עד max_retries פעמים
            attempts = 0
            while self._is_error(output) and attempts < max_retries:
                attempts += 1
                print(f"🔄 [Brain] Error detected. Initiating self-correction (Attempt {attempts}/{max_retries})...")
                
                command, output = self.self_correct(command, output)
                execution_log.append(f"**Correction {attempts}:** `{command}`\n**Output:**\n```text\n{output}\n```")

            # 4. הכנת הדו"ח ל-Orchestrator
            final_report = "\n---\n".join(execution_log)
            if self._is_error(output):
                return f"Task Failed after {attempts} retries.\n\n### Execution Log:\n{final_report}"
            else:
                return f"Task Completed Successfully.\n\n### Execution Log:\n{final_report}"
                
        except Exception as e:
            error_msg = f"Critical Brain failure: {e}"
            print(f"❌ [Brain] {error_msg}")
            return f"Error: {error_msg}"
# =====

# =====
    def self_correct(self, failed_command, error_msg):
        """
        לוגיקת התיקון: מחזירה ל-solve_task גם את הפקודה החדשה וגם את התוצאה שלה.
        """
        prompt = f"""
        The following terminal command failed: {failed_command}
        Error output: {error_msg}
        
        Provide ONLY the corrected raw terminal command. No explanations, no markdown blocks.
        """
        try:
            response = self.client.chat.completions.create(
                model=Config.MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            new_command = response.choices[0].message.content.strip().replace("`", "")
            print(f"🛠️ [Brain] Trying corrected command: {new_command}")
            
            output = self.execute_action(new_command)
            return new_command, output
            
        except Exception as e:
            return failed_command, f"❌ Error during self-correction planning: {e}"
# =====

# =====
if __name__ == "__main__":
    print("🤖 Root Brain OS is Online (Interactive Mode).")
    print("Give me a task in plain English (e.g., 'Check the git status')")
    brain = RootBrain()
    
    while True:
        try:
            user_task = input("\nroot@agent > ")
            if not user_task.strip(): continue
            if user_task.lower() in ['exit', 'quit']: break
            
            # עכשיו אנחנו גם מדפיסים את התוצאה הסופית שחזרה
            final_status = brain.solve_task(user_task)
            print(f"\n📋 [Final Report]:\n{final_status}")
            
        except KeyboardInterrupt:
            print("\nShutting down Brain...")
            break
# =====
