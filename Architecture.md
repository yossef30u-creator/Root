# Root OS - System Architecture & Runtime Blueprint

## 1. Vision & System Definition
Root OS היא לא רק כלי עזר, אלא **מערכת הפעלה מבוססת סוכנים (Agentic OS)** הרצה מקומית. היא הופכת מאגרי קוד פסיביים לסביבות עבודה אקטיביות, מודעות לעצמן, המבצעות פעולות אוטונומיות תוך שמירה על זיכרון אדפטיבי לאורך זמן[span_7](start_span)[span_7](end_span)[span_8](start_span)[span_8](end_span).

---

## 2. Runtime Topology
Root OS פועלת כמערכת Orchestration מבוססת Daemon הפועלת באופן רציף[span_9](start_span)[span_9](end_span).
המערכת אגנוסטית לחומרה (פועלת על Windows, macOS, Linux ו-Termux)[span_10](start_span)[span_10](end_span).

**Core Runtime Units:**
*   **rootd (Main Daemon):** תהליך האב המנהל את כל ה-Workers[span_11](start_span)[span_11](end_span).
*   **Watcher Worker:** מאזין לאירועי מערכת קבצים בזמן אמת[span_12](start_span)[span_12](end_span).
*   **Ingestion Worker (Monster Ingestor):** שואב קוד שהשתנה (Smart Diff) ומסנן דרך `.rootignore`[span_13](start_span)[span_13](end_span)[span_14](start_span)[span_14](end_span).
*   **Execution Worker (Agent Coder):** מבצע שינויי קוד פיזיים[span_15](start_span)[span_15](end_span)[span_16](start_span)[span_16](end_span).
*   **Validation Worker (TestSentry):** מריץ טסטים ומאמת תקינות[span_17](start_span)[span_17](end_span)[span_18](start_span)[span_18](end_span).
*   **Memory Sync Worker:** מנהל אינדוקס ווקטורי[span_19](start_span)[span_19](end_span).
*   **Dashboard Bridge:** שרת Flask/FastAPI המגיש את ה-Neural Map (Mermaid.js)[span_20](start_span)[span_20](end_span).

---

## 3. Internal Event System (Message Bus)
כדי למנוע צימוד (Coupling), כל הרכיבים מתקשרים דרך Event Bus מרכזי.

**Supported Events:**
*   `FILE_CHANGED`: טריגר מה-Watcher.
*   `INGESTION_DONE`: סיום יצירת Diff מה-Ingestor.
*   `TASK_CREATED`: הוספת פקודה מ-Dashboard Brain לתור[span_21](start_span)[span_21](end_span).
*   `TASK_COMPLETED` / `TASK_FAILED`: סטטוס ביצוע מה-Agent Coder.
*   `TEST_FAILED`: דיווח מה-TestSentry המחייב התערבות[span_22](start_span)[span_22](end_span).
*   `MEMORY_UPDATED`: טריגר לסנכרון RAG מול ה-UI.

---

## 4. State Management Engine
מערכת ה-Daemon מנהלת State Machine קשיח לכל פרויקט:

**System States:**
*   `IDLE`: המתנה לאירועים.
*   `WATCHING`: ה-Daemon פעיל ומאזין[span_23](start_span)[span_23](end_span).
*   `ANALYZING`: ה-Handlers (אדריכל, אסטרטג, ארכיונאי) מעבדים נתונים[span_24](start_span)[span_24](end_span).
*   `EXECUTING`: ה-Agent Coder נוגע בקבצים[span_25](start_span)[span_25](end_span).
*   `VERIFYING`: ה-TestSentry בודק את הקוד[span_26](start_span)[span_26](end_span).
*   `RECOVERING`: המערכת משחררת מנעולים ומתאוששת מקריסה.

---

## 5. Source Of Truth Hierarchy
במקרה של קונפליקט, סדר העדיפויות הקשיח הוא:
1.  **Repository Files:** קוד המקור הפיזי הוא המלך.
2.  **Runtime Locks (`.root.lock`):** קובע מי רשאי לכתוב[span_27](start_span)[span_27](end_span).
3.  **Memory Vector DB:** (ChromaDB / JSON) מכיל את ההיסטוריה הסמנטית[span_28](start_span)[span_28](end_span).
4.  **Manifests:** קבצי `ROOT.md`, `ROADMAP.md`, `HISTORY.md`[span_29](start_span)[span_29](end_span)[span_30](start_span)[span_30](end_span).
5.  **Core Dump:** `.root_core_dump.json` (תצוגת UI)[span_31](start_span)[span_31](end_span).

---

## 6. Execution Lifecycle (The Continuous Loop)
1.  **Watcher Engine:** זיהוי שינוי פיזי או בקשת פעולה[span_32](start_span)[span_32](end_span).
2.  **Locking:** שימוש ב-`atexit` לניהול `PID` נעילה בקובץ `.root.lock`[span_33](start_span)[span_33](end_span)[span_34](start_span)[span_34](end_span).
3.  **Diff Engine:** זיקוק השינוי.
4.  **Context Builder (RAG):** שליפת מידע מהזיכרון[span_35](start_span)[span_35](end_span).
5.  **Planning Engine:** ה-Dashboard Brain מכין תוכנית עבודה[span_36](start_span)[span_36](end_span).
6.  **Queue:** הזרקת המשימה ל-`actions_queue.json`[span_37](start_span)[span_37](end_span).
7.  **Executor:** ה-Agent Coder כותב את הקוד[span_38](start_span)[span_38](end_span).
8.  **Validator:** ה-TestSentry מאשר או פוסל[span_39](start_span)[span_39](end_span).
9.  **Memory Update & Persistence:** כתיבת המניפסטים (אדריכל, ארכיונאי)[span_40](start_span)[span_40](end_span).
10. **Unlock & Dashboard Sync:** שחרור הנעילה ועדכון ה-Neural Map[span_41](start_span)[span_41](end_span).

---

## 7. Task Queue Architecture
התור הווירטואלי (`actions_queue.json`) מנוהל בצורה תעשייתית:
*   **Model:** FIFO (First In, First Out) עם עדיפויות[span_42](start_span)[span_42](end_span)[span_43](start_span)[span_43](end_span).
*   **Task Fields:** `id`, `type`, `priority`, `status`, `retries_left`, `created_at`.
*   **Dead-letter:** משימה שנכשלת 3 פעמים ברצף (למשל, TestSentry נכשל שוב ושוב) נזרקת לקרנטינה וממתינה לאישור משתמש[span_44](start_span)[span_44](end_span)[span_45](start_span)[span_45](end_span).

---

## 8. Failure Recovery System
*   **Stale Lock Cleanup:** אם ה-Daemon קורס ולא הספיק לבצע `atexit`[span_46](start_span)[span_46](end_span), הפעלה חדשה תבדוק את ה-PID ב-`.root.lock`. אם התהליך מת, המנעול יוסר.
*   **Watchdog Restart:** מנגנוני Crontab / Termux:Boot יוודאו שה-Service עולה מחדש[span_47](start_span)[span_47](end_span).
*   **Configuration Survival:** מנגנון Silent Migration ישחזר אוטומטית את `~/.root_config` ללא דריסת מפתחות המשתמש[span_48](start_span)[span_48](end_span)[span_49](start_span)[span_49](end_span).
*   **Token Guard:** חסימה אוטומטית של פעולות אם סריקה עוברת 50,000 תווים (הגנה על תקציב ה-API)[span_50](start_span)[span_50](end_span).

---

## 9. Safety Rules & Execution Permissions (Boundaries)
ה-Agent Coder פועל תחת מגבלות קשיחות:
*   **Allowed:** עריכת קבצים בתוך תיקיית ה-Workspace המוגדרת בלבד.
*   **Forbidden:** 
    *   אין הרשאת מחיקה מחוץ ל-Repo.
    *   אין לגעת בתיקיות מסוננות (`.rootignore` או `node_modules`)[span_51](start_span)[span_51](end_span).
    *   אין להריץ פקודות Shell הרסניות (מותר רק הרצת טסטים בסביבת TestSentry)[span_52](start_span)[span_52](end_span).
    *   חל איסור על עקיפת מנגנון ה-Token Budgeting[span_53](start_span)[span_53](end_span).

---

## 10. Memory Architecture Lifecycle
הזיכרון אינו סטטי אלא פועל במודל אדפטיבי (Adaptive Memory)[span_54](start_span)[span_54](end_span):
*   **Episodic Memory:** אירועים נקודתיים (מי שינה מה, מתי ולמה) – מתועד ב-`HISTORY.md`[span_55](start_span)[span_55](end_span)[span_56](start_span)[span_56](end_span).
*   **Semantic Memory:** כללי הארכיטקטורה והקשרים – נשמרים ב-Vector DB.
*   **Vector Indexing:** משתמש ב-ChromaDB (למחשבים חזקים) או Numpy/JSON (למובייל)[span_57](start_span)[span_57](end_span)[span_58](start_span)[span_58](end_span).
*   **AI Access:** תקשורת דרך OpenAI API (עם תמיכה מובנית עתידית ב-Local LLM / OpenRouter לפרטיות מוחלטת)[span_59](start_span)[span_59](end_span)[span_60](start_span)[span_60](end_span).

---

## 11. File Structure Layout
ארגון התיקיות משקף את הארכיטקטורה הפנימית:

```text
root_os/
 ├── pyproject.toml         # הגדרת פרויקט ותלויות[span_61](start_span)[span_61](end_span)
 ├── boot.py                # Bootloader / Config Init[span_62](start_span)[span_62](end_span)
 ├── core/                  # מנועי הליבה (Daemon, Ingestor, Scanner)[span_63](start_span)[span_63](end_span)
 ├── memory/                # Vector indexing & Semantic memory
 ├── agents/                # Handlers (Architect, Strategist, Archivist, Coder)[span_64](start_span)[span_64](end_span)
 ├── queue/                 # actions_queue logic[span_65](start_span)[span_65](end_span)
 ├── dashboard/             # Bridge server & UI (Flask, HTML, Tailwind)[span_66](start_span)[span_66](end_span)
 ├── tests/                 # TestSentry validation sandboxes
 └── config/                # ~/.root_config & Silent Migration logic[span_67](start_span)[span_67](end_span)

#####
## 12. Data Model & Persistence Matrix
כדי למנוע כאוס ופורמטים סותרים בין ה-Workers השונים, הוגדרה מטריצת אחסון וניהול חוזים קפדנית:

| Data Type | Storage Engine | Lifetime | Schema / Format Contract |
| :--- | :--- | :--- | :--- |
| **System State & Locks** | `.root.lock` (File) | Ephemeral (Runtime) | PID, Timestamp, Current_State |
| **Task Queue** | `.root/actions_queue.json` | Persistent until clear | `TaskSchema` (id, target, priority, retries, status) |
| **Architectural Vectors** | ChromaDB / Vector-Numpy | Persistent | `MemoryEntry` (hash_id, user_id, embedding, text) |
| **Live UI State** | `.root_core_dump.json` | Ephemeral (Auto-Sync) | `GraphSchema` (nodes, edges, active_agents) |
| **Project Manifests** | `ROOT.md`, `ROADMAP.md` | Persistent (Git Tracked) | Markdown with rigid Section Headers |
| **Configuration** | `~/.root_config` | Persistent (Global) | JSON (Model, Keys, Token Budget Limit) |

**Data Contracts (Schemas):**
כל אירוע (Event) או משימה חייבים להיות מאומתים מול Pydantic Models ברמת הליבה לפני עיבוד כדי למנוע חוסר תאימות בין סוכנים.
=====

=====
## 13. Contracts, Isolation & Operational Guarantees
כדי להפוך את Root OS ל-Production-Ready ולמנוע השחתת קוד חיה, הוגדרו מנגנוני ההגנה והביצוע הבאים:

### A. Execution Isolation & Sandboxing
*   **Dry-Run Mode:** כל שינוי קוד המוצע על ידי ה-Agent Coder עובר תחילה ל-Virtual Buffer. 
*   **Branch Strategy:** ה-Agent אינו מורשה לדחוף (Push) שינויים ישירות ל-Main. כל שינוי מורכב מייצר Branch ייעודי (לדוגמה: `root-agent/fix-auth`), ומוגש כ-Patch או Pull Request אוטומטי לאישור המפתח.

### B. Concurrency & Actor Model
*   תהליך ה-Orchestration מתבצע בארכיטקטורה אסינכרונית (AsyncIO / Event Loop) בתוך תהליך ה-Daemon הראשי.
*   **Sub-processes Isolation:** רכיבים מסוכנים כמו TestSentry רצים כ-Subprocesses נפרדים מבודדים (Isolated Bash) כדי שקריסת טסט (למשל, לולאה אינסופית) לא תקריס את הליבה (rootd).

### C. Idempotency & Failure Semantics
*   **Safe Retries:** כל פעולת רשת (API ל-LLM) או פעולת מערכת קבצים מתוכננת להיות אידמפוטנטית. משימה שנכשלת באמצע לא תשאיר "חצי קובץ". המערכת תבצע Rollback לטביעת האצבע (Hash) הקודמת לפני ניסיון חוזר.

### D. Startup & Shutdown Lifecycle (Boot Sequence)
1.  **Health Check:** בדיקת תקינות סביבה (Python, תלויות).
2.  **Config Load:** טעינת `~/.root_config` דרך מנגנון ה-Silent Migration.
3.  **Lock Acquisition:** ניסיון כתיבה ל-`.root.lock`. אם קיים מנעול זומבי מריצה קודמת (Stale Lock Cleanup), הוא מנוקה.
4.  **Queue Resume:** שחזור פעולות שלא הושלמו מ-`actions_queue.json`.
5.  **Workers Ignition:** העלאת סוכני ההאזנה והזיכרון.
6.  **Graceful Shutdown:** במקרה של סיגנל סגירה (SIGINT/SIGTERM), מופעל ה-`atexit` לרוקן תורים, לשחרר מנעולים ולגבות את הזיכרון הוקטורי לדיסק.

### E. Observability & Auditing
המערכת מייצרת Audit Trail מובנה ללא פגיעה בביצועים:
*   `logs/root_runtime.log`: רישום אירועי מערכת (Boot, Lock, Error).
*   `logs/ai_decisions.log`: תיעוד שקוף של *למה* הסוכן קיבל החלטה, כולל טוקנים שנוצלו ורמת ודאות (Confidence Score).
#####
