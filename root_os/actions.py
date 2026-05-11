# =====
import subprocess
import os
from config import Config
# =====

# =====
class RootActions:
    def __init__(self):
        # רשימת פקודות אסורות מטעמי בטיחות
        self.forbidden_commands = ["rm -rf /", "mkfs", "shutdown"]
# =====

# =====
    def execute_command(self, command):
        """מבצע פקודת טרמינל ומחזיר את הפלט"""
        # בדיקת בטיחות בסיסית
        if any(forbidden in command for forbidden in self.forbidden_commands):
            return "❌ Error: Command rejected for security reasons."

        print(f"🛠️ [Action] Executing: {command}")
        # =====
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if result.returncode == 0:
                return f"✅ Success:\n{result.stdout}"
            else:
                return f"⚠️ Failed (Code {result.returncode}):\n{result.stderr}"
        except Exception as e:
            return f"❌ Execution Error: {str(e)}"
        # =====
# =====

# =====
    def create_file(self, path, content):
        """יוצר קובץ חדש בפרויקט"""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"✅ File created: {path}"
        except Exception as e:
            return f"❌ File creation failed: {str(e)}"
# =====

# =====
if __name__ == "__main__":
    # בדיקה מהירה של רכיב הביצוע
    actions = RootActions()
    print(actions.execute_command("ls -l"))
# =====
