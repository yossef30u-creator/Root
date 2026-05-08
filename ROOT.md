# ROOT - Project Manifest 🌳

> **Tagline:** The Proactive Context Layer for Autonomous AI Agents.
> **Status:** Initializing (MVP Phase - Year 1)

## 🎯 חזון ומטרה (Vision)
Root היא תשתית ה-Agentic OS לניהול הקשר (Context) וזיכרון עבור סוכני AI. המערכת הופכת מאגרי קוד לישויות "מודעות לעצמן" המבטיחות שכל סוכן AI יבין מיידית את הארכיטקטורה והכוונות של הפרויקט.

## 🏗️ רכיבי ליבה (Core Components)
| רכיב | תיאור | טכנולוגיה |
| :--- | :--- | :--- |
| **Root Ingestor** | ניתוח Diffs ושינויים בזמן אמת. | GitHub Actions |
| **Semantic Engine** | פירוש שינויי קוד להקשר עסקי/ארכיטקטוני. | GPT-4o / LangChain |
| **Context Storage** | ניהול זיכרון לטווח קצר (Markdown) וארוך (Vector DB). | ChromaDB / ROOT.md |
| **MCP Bridge** | הנגשת ה-Context לסוכנים חיצוניים. | Model Context Protocol |

## ⚙️ מחזור חיים וטריגרים (Lifecycle & Triggers)
המערכת פועלת אוטונומית על בסיס אירועי Git:
* **Push:** סריקת Diff, עדכון `ROOT.md` ואינדקס וקטורי.
* **Pull Request:** בדיקת "בריאות הקשר" (Context Health Check) אל מול הארכיטקטורה.
* **Manual Dispatch:** סריקת עומק מלאה (Full Crawl) של המאגר.

## 🛠️ מפרט טכני (Technical Specs)
* **Stack:** Python 3.10+, Docker.
* **Infrastructure:** GitHub Actions (Runner: `ubuntu-latest`).
* **Secrets:** `OPENAI_API_KEY`, `GITHUB_TOKEN`.

## 🔗 כלי MCP זמינים (Available Tools)
* `read_root_state`: החזרת הסטטוס הארכיטקטוני המעודכן.
* `query_memory`: חיפוש סמנטי בהיסטוריית ההחלטות והקוד.
* `validate_action`: וידוא התאמת קוד מוצע ל-Context הנוכחי.

## 📍 אבני דרך קרובות (Year 1 Roadmap)
1. פיתוח ה-GitHub Action לניתוח Diffs ועדכון אוטומטי.
2. השקת VS Code Extension להצגת Context חי למפתח.
3. הטמעת ChromaDB לניהול זיכרון סמנטי מקומי.

---
> "If you aren't at the root, you're just on the surface."
