
# ROOT - Project Manifest 🌳
> **Tagline:** The Proactive Context Layer for Autonomous AI Agents.
> **Status:** Last Update - Full modular reconstruction completed. Integrated Semantic Vector Memory (JSON-based), Action Execution Module, and MCP FastAPI Bridge. The system now supports real-time CLI interaction and remote context retrieval.
> 
> [!IMPORTANT]
> **זמני:** הפרויקט מנוהל ומפותח כרגע באופן בלעדי דרך **מכשיר נייד (Termux & Acode)**. סביבת העבודה תועבר למחשב (PC) בשלב מאוחר יותר. כל הליכי הריצה והבדיקה מותאמים כרגע לארכיטקטורת ARM/Android.
> 
## 🎯 חזון ומטרה (Vision)
Root היא תשתית ה-Agentic OS לניהול הקשר (Context) וזיכרון עבור סוכני AI. המערכת הופכת מאגרי קוד לישויות "מודעות לעצמן" המבטיחות שכל סוכן AI יבין מיידית את הארכיטקטורה והכוונות של הפרויקט.
## 🏗️ רכיבי ליבה (Core Components)
| רכיב | תיאור | טכנולוגיה |
|---|---|---|
| **Root Ingestor** | מנגנון קליטת שינויים מה-Git. מנתח Diffs ושינויי קבצים בזמן אמת. | Python / Git |
| **Semantic Engine & Memory** | "המוח" שמפרש שינויים להקשר עסקי, ומנהל זיכרון וקטורי בפורמט JSON. | OpenAI API (GPT-4o) / Embeddings |
| **Action Module** | "הידיים" של המערכת - הרצת פקודות טרמינל וניהול קבצים בצורה מאובטחת. | Python Subprocess |
| **MCP Bridge** | הנגשת ה-Context לסוכנים חיצוניים (כגון Cursor). | FastAPI / Uvicorn (Model Context Protocol) |
| **Root CLI** | ממשק משתמש אינטראקטיבי לחיפוש סמנטי וביצוע פקודות. | Requests / Python |
## ⚙️ מחזור חיים וטריגרים (Lifecycle & Triggers)
המערכת פועלת כרגע במודל היברידי (במעבר לענן בעתיד):
 * **Manual Ingestion:** הרצת סקריפט ה-Ingestor לאחר קומיטים לעדכון ה-Context.
 * **Full Crawl:** סריקת עומק מלאה (Full Crawl) של המאגר לאינדוקס מחדש באמצעות ה-Crawler.
 * **Continuous Bridge:** השרת רץ ברקע ומאפשר תקשורת ושאילתות רציפות.
## 🛠️ מפרט טכני (Technical Specs)
 * **Stack:** Python 3.10+, FastAPI, Uvicorn, NumPy.
 * **Infrastructure:** Termux (Android) - Local Environment (הכנה ל-GitHub Actions ו-Docker בעתיד).
 * **Memory Storage:** .root/memory.json (JSON-based Vector Storage).
 * **Secrets:** OPENAI_API_KEY, GITHUB_TOKEN.
## 🔗 פונקציות MCP זמינות (Available API Endpoints)
 * GET /query: חיפוש סמנטי עמוק בהיסטוריית ההחלטות והקוד.
 * GET /status: החזרת הסטטוס הארכיטקטוני המעודכן מתוך המניפסט.
 * POST /execute: וידוא והרצת פקודות טרמינל (Git, Filesystem) מרחוק.
## 🚀 עקרונות תכנון לעתיד (5 שנים קדימה)
הארכיטקטורה נבנתה להיות **Proactive** ולא Reactive. היא לא מחכה לשאלה, היא מכינה את התשובה מראש. המבנה תומך בריבוי סוכנים (Multi-Agent) שיכולים לשתף פעולה על גבי אותו "שורש" מידע אחיד.
## 📍 אבני דרך קרובות (Current Roadmap)
 1. ✅ **שלב א':** הקמת תשתית זיכרון סמנטי וסורק קבצים.
 2. ✅ **שלב ב':** בניית ה-MCP Bridge וממשק ה-CLI.
 3. 🔄 **שלב ג':** פיתוח ה-Self-Correction Loop (תיקון שגיאות אוטונומי) תחת root_brain.py.
 4. ⏳ **שלב ד':** השקת VS Code Extension להצגת Context חי למפתח, פיתוח ה-GitHub Action לניתוח Diffs אוטומטי בענן, ומעבר לניהול זיכרון וקטורי מלא.
> "If you aren't at the root, you're just on the surface."
> 
