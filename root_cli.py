#!/usr/bin/env python3
# =====
import requests
import json
import sys
import os
from openai import OpenAI
from config import Config
# =====

# =====
class RootCLI:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        
        # התנעה של ה-AI
        self.client = OpenAI(
            base_url=Config.BASE_URL,
            api_key=Config.OPENAI_API_KEY,
            default_headers={"HTTP-Referer": "https://github.com/RootProject", "X-Title": "Root Agentic OS"}
        )

    def call_api(self, endpoint, method="GET", data=None):
        try:
            if method == "GET":
                response = requests.get(f"{self.base_url}/{endpoint}", params=data)
            else:
                response = requests.post(f"{self.base_url}/{endpoint}", json=data)
            return response.json()
        except Exception as e:
            return {"error": f"Is the server running? {str(e)}"}

    def get_live_status(self):
        """קורא את הסטטוס החי של המערכת מתוך ROOT.md"""
        if os.path.exists("ROOT.md"):
            try:
                with open("ROOT.md", "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                return "Could not read ROOT.md"
        return "ROOT.md does not exist yet."

    def synthesize_answer(self, query, context_data, live_status):
        """מנוע סינתזה משולב: היסטוריה (Vector DB) + מציאות (ROOT.md)"""
        context_str = "\n".join([f"- {item['content']}" for item in context_data]) if context_data else "No historical context found."
        
        prompt = f"""You are Root, an elite Agentic OS Architect.
        
        LIVE SYSTEM STATUS (from ROOT.md):
        {live_status}
        
        HISTORICAL MEMORY CHUNKS:
        {context_str}
        
        Answer the user's prompt in professional Hebrew. 
        Use BOTH the live status and historical memory to form a complete picture.
        
        User Prompt: {query}"""
        
        try:
            response = self.client.chat.completions.create(
                model=Config.MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"⚠️ שגיאת סינתזה: {e}"
# =====

# =====
if __name__ == "__main__":
    cli = RootCLI()
    print("🌿 Root OS Interface Online")
    print("Commands: 'run [cmd]' for terminal | just type to chat with the Agent")
    
    while True:
        try:
            user_input = input("\nroot@os > ").strip()
            if not user_input: continue
            if user_input.lower() in ['exit', 'quit']: break
            
            # =====
            if user_input.startswith("run "):
                # פקודת טרמינל - מועברת לשרת ה-MCP
                cmd = user_input[4:]
                print(f"🛠️ Executing: {cmd}...")
                res = cli.call_api("execute", method="POST", data={"command": cmd})
                print(res.get("output", res))
            else:
                # 1. שולפים זיכרון היסטורי
                print(f"🧠 Searching memory & reading live status...")
                res = cli.call_api("query", data={"q": user_input})
                context_data = res.get("context", [])
                
                # 2. קוראים סטטוס חי מהדשבורד
                live_status = cli.get_live_status()
                
                # 3. מסנתזים תשובה שמכילה את הכל
                print("🤖 Synthesizing answer...\n")
                answer = cli.synthesize_answer(user_input, context_data, live_status)
                print(f"✨ Root:\n{answer}\n")
                
                # תצוגת מקורות
                if context_data:
                    print(f"--- (מבוסס על ROOT.md + {len(context_data)} קבצי זיכרון) ---")
                else:
                    print(f"--- (מבוסס על הסטטוס החי ב-ROOT.md בלבד) ---")
            # =====
            
        except KeyboardInterrupt:
            print("\n👋 Exiting Root CLI...")
            break
# =====
