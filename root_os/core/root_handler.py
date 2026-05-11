#!/usr/bin/env python3
# =====
import os
from datetime import datetime
from openai import OpenAI
from config_manager import Config

# =====
def update_manifest(analysis, critic_feedback=None):
    """
    (אדריכל המערכת)
    קורא את הארכיטקטורה הקיימת, מבין את השינויים החדשים, 
    וכותב מחדש את מפת ה-ROOT במלואה - ללא היסטוריה, רק הווה אסטרטגי.
    """
    manifest_path = getattr(Config, 'MANIFEST_PATH', 'ROOT.md')
    
    # 1. קריאת המפה הקיימת (כדי לא לאבד את המבנה של שאר המערכת)
    current_root = ""
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            current_root = f.read()

    # 2. אתחול חיבור למוח ה-AI
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("BASE_URL", "https://openrouter.ai/api/v1")
    model = os.environ.get("MODEL", "google/gemini-pro-1.5")
    
    if not api_key:
        print("⚠️ [Root Architect] חסר API Key, מבצע ניקוי בסיסי ללא ניתוח עומק...")
        return # במערכת אמיתית נעשה פה Fallback, אבל רות דורשת AI.

    client = OpenAI(base_url=base_url, api_key=api_key)

    # 3. הפרומפט המפלצתי - חוקי הברזל לאדריכל
    system_prompt = """
    You are the 'System Architect Agent' for Root OS.
    Your objective is to maintain the ROOT.md file. This file is the strategic DNA of the project.
    
    CRITICAL RULES:
    1. META-INSTRUCTION: You must start the document with:
       "> **הוראת מערכת:** זה המצב הנוכחי בלבד. אל תחפש פה היסטוריה."
    2. NO HISTORY: Do not write "Added", "Changed", or "Fixed". Only describe how the system works RIGHT NOW.
    3. NO TASKS: Do not write what needs to be done. That belongs in the Roadmap.
    4. STRUCTURE REQUIRED:
       - 🏗️ מפת זרימה לוגית (Logic Flow)
       - 🧠 הנחות יסוד (Core Assumptions)
       - 🔗 מפת תלות (Dependency Graph)
       - 🔌 ממשקים מרכזיים (APIs & Contracts)
    
    Read the 'Current ROOT.md' and the 'Latest Changes'. 
    Synthesize them, remove obsolete components, and output the entirely rewritten ROOT.md.
    Output ONLY valid Markdown.
    """

    user_prompt = f"""
    --- Current ROOT.md ---
    {current_root if current_root else "Empty (New Project. Build the baseline architecture)."}
    
    --- Latest Changes (Diff Analysis) ---
    {analysis}
    
    --- Architect Warnings (Critic) ---
    {critic_feedback if critic_feedback else "None"}
    """

    print(f"🏗️ [Root Architect] Synthesizing full system blueprint...")

    try:
        # 4. כתיבת הארכיטקטורה מחדש
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        new_root_content = response.choices[0].message.content.strip()

        # ניקוי אם המודל עטף ב-```markdown
        if new_root_content.startswith("```markdown"):
            new_root_content = new_root_content[11:-3].strip()
        elif new_root_content.startswith("```"):
            new_root_content = new_root_content[3:-3].strip()

        # 5. חותמת זמן ושמירה ("הלוח המחיק")
        now_str = datetime.now().strftime('%d/%m/%Y %H:%M')
        final_content = f"# 🌳 Root OS: Master Architecture\n\n{new_root_content}\n\n---\n*📐 אדריכלות עודכנה: {now_str} | מערכת Root OS*"

        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(final_content)
            
        print("✅ [Root Architect] Blueprint regenerated successfully. Context is sharp.")

    except Exception as e:
        print(f"❌ [Root Architect Error] Failed to generate strategic root: {e}")
# =====
