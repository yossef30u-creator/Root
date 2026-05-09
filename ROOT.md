
# ROOT - Project Manifest 🌳
> **Tagline:** The Proactive Context Layer for Autonomous AI Agents.
> **Status:** Last Update - This code update introduces a caching mechanism for vector memory in GitHub Actions, adds vector memory integration for historical context reference in both synthesis and critic processes, and enhances GitHub issue creation for critic feedback. Additionally, it restructures command execution logic to securely use subprocess while removing the `RootBrain` dependency in `main.py`, and refines the memory storage process, enriching project capabilities for more robust automation and historical context utilization.
> **Critic Alert:** The code diff introduces potential architectural and technical issues. Here are the key concerns:  1. **Comment Redundancy**: Many comments are overly verbose and repeated, cluttering the codebase without adding significant value.     2. **Cache Implementation**: The caching mechanism, while beneficial, seems to lack removal logic, potentially resulting in the persistence of outdated cache files.  3. **Error Handling**: There's a lack of robust error handling, especially in subprocess execution, which now includes a timeout but does not adequately handle all failure modes.  4. **Critical Warnings**: Removal of the brain module (`root_brain`) from `main.py` introduces inconsistency, as it's still referenced in related methods. This suggests incomplete refactoring.  5. **Code Duplication**: Similar patterns are reoccurring, especially at the start and end of methods, which could benefit from utility functions to streamline maintenance.  6. **Unhandled Newlines**: The lack of a newline at the end of files is non-compliant with POSIX standards, affecting code portability.  These points indicate that the changes could lead to increased technical debt and potential runtime issues.
> 
> [!IMPORTANT]
> **זמני:** הפרויקט מנוהל ומפותח כרגע באופן בלעדי דרך **מכשיר נייד (Termux & Acode)**. סביבת העבודה תועבר למחשב (PC) בשלב מאוחר יותר. כל הליכי הריצה והבדיקה מותאמים כרגע לארכיטקטורת ARM/Android.
> 
## 🎯 חזון ומטרה (Vision)
Root היא תשתית ה-Agentic OS לניהול הקשר (Context) וזיכרון עבור סוכני AI. המערכת הופכת מאגרי קוד לישויות "מודעות לעצמן" המבטיחות שכל סוכן AI יבין מיידית את הארכיטקטורה והכוונות של הפרויקט.
## 🏗️ רכיבי ליבה (Core Components)
## ⚙️ Architecture
Root OS is structured as a Three-Layer system:

1. **Memory Layer:** This layer is responsible for managing both short-term and long-term memory using markdown files and a vector database.
2. **Brain Layer:** This layer interprets and processes data using LLMs to understand changes and provide context-aware analysis especially in code refactoring.
3. **Bridge Layer:** It connects and extends Root’s capabilities to external agents by providing structured context ensuring they operate with coherent project architecture.

 Root OS is now capable of autonomous code execution and self-correction.
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
