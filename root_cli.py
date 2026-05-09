# =====
import requests
import json
import sys
# =====

# =====
class RootCLI:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def call_api(self, endpoint, method="GET", data=None):
        try:
            if method == "GET":
                response = requests.get(f"{self.base_url}/{endpoint}", params=data)
            else:
                response = requests.post(f"{self.base_url}/{endpoint}", json=data)
            return response.json()
        except Exception as e:
            return {"error": f"Is the server running? {str(e)}"}
# =====

# =====
if __name__ == "__main__":
    cli = RootCLI()
    print("🌿 Root OS Interface Online")
    print("Commands: 'run [cmd]' for terminal | just type for memory search")
    
    while True:
        try:
            user_input = input("\nroot@os > ").strip()
            if not user_input: continue
            if user_input.lower() in ['exit', 'quit']: break
            
            # =====
            if user_input.startswith("run "):
                # פקודת טרמינל
                cmd = user_input[4:]
                print(f"🛠️ Executing: {cmd}...")
                res = cli.call_api("execute", method="POST", data={"command": cmd})
                print(res.get("output", res))
            else:
                # חיפוש סמנטי (ברירת מחדל)
                print(f"🧠 Searching memory for: '{user_input}'...")
                res = cli.call_api("query", data={"q": user_input})
                
                if "context" in res and res["context"]:
                    for item in res["context"]:
                        print(f"\n📍 File: {item['file']} (Score: {item['score']:.2f})")
                        print(f"💡 {item['content'][:200]}...")
                else:
                    print("🤷 No relevant memory found.")
            # =====
            
        except KeyboardInterrupt:
            break
# =====
