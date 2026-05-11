import os
import sys
from datetime import datetime
from openai import OpenAI
from config_manager import Config

def agentic_history_sync(analysis, critic_feedback):
    """
    (הארכיונאי - The Archivist)
    מוסיף תיעוד אסטרטגי לראש יומן ההיסטוריה, מתחת לכותרת הראשית.
    מבטיח סדר כרונולוגי הפוך (החדש ביותר למעלה).
    """
    history_file = "HISTORY.md"
    now_str = datetime.now().strftime('%d/%m/%Y %H:%M')
    
    # 1. הגדרת כותרת קבועה לקובץ
    HEADER = "# 📜 יומן החלטות היסטורי - Root OS\n\n> **הוראת מערכת:** זהו יומן ההחלטות הכרונולוגי. פה נמצא ה'למה'. אסור למחוק מכאן מידע.\n\n---\n"

    # 2. קריאת ההיסטוריה הקיימת
    current_content = ""
    if os.path.exists(history_file):
        with open(history_file, "r", encoding="utf-8") as f:
            current_content = f.read()
    else:
        current_content = HEADER

    # 3. הכנת הלקוח (שימוש ב-Config המרכזי)
    client = OpenAI(
        base_url=Config.BASE_URL,
        api_key=Config.API_KEY,
        default_headers={"X-Title": "Root Agentic OS"}
    )

    system_prompt = f"""
    You are the 'Historical Analyst Agent' for Root OS. 
    Your task is to write a strategic log entry for the date: {now_str}.
    
    CRITICAL RULES:
    1. FOCUS ON STRATEGY: Explain WHY changes were made based on the analysis.
    2. ARCHITECTURAL SHIFTS: If the Critic found issues, document them as "Lessons Learned".
    3. TONE: Professional, concise, and Hebrew-based.
    4. FORMAT: Use the following structure:
       ## 📅 {now_str}
       - 🎯 **מטרה אסטרטגית:** (Why we did this)
       - 🏗️ **שינוי מבני:** (What actually changed in the logic)
       - 💡 **תובנות ביקורת:** (Insights from Critic feedback)
    """

    # שליחת הקשר מצומצם ל-AI כדי לשמור על סגנון
    context_snippet = current_content.replace(HEADER, "")[:3000]

    try:
        print(f"📜 [Root Archivist] Archiving strategic rationale for {now_str}...")
        
        response = client.chat.completions.create(
            model=Config.MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context:\n{context_snippet}\n\nAnalysis:\n{analysis}\n\nCritic:\n{critic_feedback}"}
            ]
        )
        
        new_entry = response.choices[0].message.content.strip()
        
        # ניקוי שאריות Markdown אם ה-AI התחכם
        new_entry = new_entry.replace("```markdown", "").replace("```", "").strip()

        # 4. המניפולציה המפלצתית: הזרקה לראש הקובץ מתחת לכותרת
        # מסירים את הכותרת הישנה מהתוכן הקיים כדי שלא תשתכפל
        old_history_clean = current_content.replace(HEADER, "").strip()
        
        full_updated_content = f"{HEADER}\n\n{new_entry}\n\n---\n\n{old_history_clean}"

        with open(history_file, "w", encoding="utf-8") as f:
            f.write(full_updated_content)
            
        print("✅ [History] Strategic entry injected to the top of HISTORY.md.")

    except Exception as e:
        print(f"⚠️ [History Error] Failed to sync history: {e}")

if __name__ == "__main__":
    # בדיקה מהירה
    agentic_history_sync("שיפור מנגנון הזרקת קוד", "הקוד עבר בהצלחה אבל דורש תשומת לב לביצועים")