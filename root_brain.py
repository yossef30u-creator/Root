# =====
import requests
from openai import OpenAI
from config import Config
# =====

# =====
class RootBrain:
    def __init__(self, mcp_url="http://127.0.0.1:8000"):
        self.mcp_url = mcp_url
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
            return "No memory available."
        except:
            return "Memory server offline."
# =====

# =====
    def execute_action(self, command):
        """שולח פקודה לשרת ה-MCP כדי שיבצע אותה בטרמינל"""
        try:
            res = requests.post(f"{self.mcp_url}/execute", json={"command": command})
            if res.status_code == 200:
                return res.json().get("output", "")
            return f"⚠️ Failed: {res.text}"
        except Exception as e:
            return f"❌ Error: {e}"
# =====

# =====
    def solve_task(self, task):
        """הלולאה המרכזית: מנתח משימה, מקבל החלטה, מבצע ומתקן במידת הצורך"""
        print(f"\n🧠 [Brain] Analyzing task: '{task}'...")
        context = self.ask_memory(task)
        
        prompt = f"""
        You are Root OS, an autonomous agent running in Termux (Android).
        Task to achieve: {task}
        Context from memory: {context}
        
        Provide ONLY the raw terminal command to execute to achieve this task. 
        Do not include markdown blocks like ```bash, just the raw string.
        """
        
        try:
            # שלב 1: החלטה
            response = self.client.chat.completions.create(
                model=Config.MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            command = response.choices[0].message.content.strip().replace("`", "")
            
            # שלב 2: ביצוע
            print(f"🛠️ [Brain] Decided to execute: {command}")
            output = self.execute_action(command)
            print(f"📊 [Brain] Output:\n{output}")
            
            # שלב 3: תיקון אוטומטי
            if "⚠️ Failed" in output or "❌ Error" in output or "not found" in output.lower():
                print("🔄 [Brain] Error detected! Initiating self-correction...")
                self.self_correct(command, output)
                
        except Exception as e:
            print(f"❌ [Brain] Critical failure: {e}")
# =====

# =====
    def self_correct(self, failed_command, error_msg):
        """לוגיקת התיקון: מנתח את השגיאה ומנסה פקודה חדשה"""
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
            print(f"📊 [Brain] Correction Output:\n{output}")
            
        except Exception as e:
            print(f"❌ [Brain] Self-correction logic failed: {e}")
# =====

# =====
if __name__ == "__main__":
    print("🤖 Root Brain OS is Online.")
    print("Give me a task in plain English (e.g., 'Check the git status')")
    brain = RootBrain()
    
    while True:
        try:
            user_task = input("\nroot@agent > ")
            if not user_task.strip(): continue
            if user_task.lower() in ['exit', 'quit']: break
            
            brain.solve_task(user_task)
            
        except KeyboardInterrupt:
            break
# =====
