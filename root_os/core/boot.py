import sys
import os
import time
import json
import subprocess
import platform
import atexit
from pathlib import Path

# נתיבים לקבצי הגדרות גלובליים
CONFIG_PATH = os.path.expanduser("~/.root_config")
REGISTRY_PATH = os.path.expanduser("~/.root_projects_registry.json")


def graceful_shutdown():
    """(atexit) מנגנון שחרור וניקוי בטוח כשה-Bootloader מסיים או קורס"""
    print("\n🛑 [Root OS] תהליך ההתנעה הסתיים בצורה חלקה.")
    print("🌿 המערכת ממשיכה לפעול ברקע במצב Daemon.")


# רישום פונקציית היציאה - תרוץ תמיד בסוף!
atexit.register(graceful_shutdown)


def ensure_dependencies():
    """בודקת אם הספריות הקריטיות מותקנות, ואם לא - מתקינה אותן"""
    try:
        import flask
        import watchdog
        import openai
        import schedule  # נוסף כדי לתמוך בשעון העדכונים
    except ImportError:
        print("📦 [Root] מזהה רכיבים חסרים במערכת. מתקינה אוטומטית...")
        try:
            core_dir = os.path.dirname(os.path.abspath(__file__))
            req_path = os.path.join(os.path.dirname(core_dir), "requirements.txt")

            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-r", req_path]
            )
            print("✅ כל הרכיבים הותקנו בהצלחה. ממשיכה בהתנעה...")
        except Exception as e:
            print(f"⚠️ נכשלה התקנה אוטומטית: {e}")
            print("אנא הרץ ידנית: pip install -r requirements.txt")


def check_and_install_alias():
    """בודקת אם פקודת ה-root כבר קיימת בטרמינל, תומכת Bash/ZSH"""
    system = platform.system()
    current_path = os.path.abspath(__file__)

    if system in ["Linux", "Darwin"] or "termux" in os.getenv("PREFIX", "").lower():
        possible_shells = ["~/.bashrc", "~/.zshrc"]
        alias_line = f"alias root='python \"{current_path}\"'"
        installed = False

        for shell in possible_shells:
            shell_path = os.path.expanduser(shell)
            if os.path.exists(shell_path):
                try:
                    with open(shell_path, "r", encoding="utf-8") as f:
                        if alias_line in f.read():
                            installed = True
                            continue

                    with open(shell_path, "a", encoding="utf-8") as f:
                        f.write(f"\n# Root OS Global Command\n{alias_line}\n")
                    installed = True
                except Exception:
                    pass

        if installed:
            print("🚀 [Root] פקודת 'root' זמינה בטרמינל שלך.")


def setup_autostart():
    """(מפלצת) מתקינה את המנוע הגלובלי שירוץ אוטומטית כשהמחשב/שרת עולה"""
    system = platform.system()
    core_dir = os.path.dirname(os.path.abspath(__file__))
    service_script = os.path.join(core_dir, "core", "root_service.py")

    if not os.path.exists(service_script):
        return

    # יצירת פקודת הריצה השקטה
    run_cmd = f"{sys.executable} {service_script} > /dev/null 2>&1 &"

    try:
        if system == "Linux" and "termux" not in os.getenv("PREFIX", "").lower():
            # סביבת לינוקס רגילה (Ubuntu/Debian) - הוספה ל-Cron
            cron_cmd = f"@reboot {run_cmd}\n"
            current_crontab = subprocess.run(
                ["crontab", "-l"], capture_output=True, text=True
            ).stdout

            if service_script not in current_crontab:
                new_crontab = current_crontab + cron_cmd
                p = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE)
                p.communicate(input=new_crontab.encode("utf-8"))
                print("⚙️  [Auto-Start] המנוע הוגדר לעלות אוטומטית עם הפעלת המחשב.")

        elif "termux" in os.getenv("PREFIX", "").lower():
            # סביבת Termux (אנדרואיד) - הוספה ל-bashrc או boot script
            termux_boot_dir = os.path.expanduser("~/.termux/boot")
            if not os.path.exists(termux_boot_dir):
                os.makedirs(termux_boot_dir, exist_ok=True)

            boot_script = os.path.join(termux_boot_dir, "start_root_os")
            if not os.path.exists(boot_script):
                with open(boot_script, "w") as f:
                    f.write(
                        f"#!/data/data/com.termux/files/usr/bin/sh\ntermux-wake-lock\n{run_cmd}\n"
                    )
                os.chmod(boot_script, 0o755)
                print(
                    "⚙️  [Auto-Start] Root הוגדרה לעלות אוטומטית באנדרואיד (דורש Termux:Boot)."
                )
    except Exception as e:
        print(f"⚠️ [Auto-Start] דילוג על הגדרת הפעלה אוטומטית: {e}")


def setup_wizard():
    print("\n🌟 [Root OS] התקנה ראשונית - ברוך הבא!")
    print("כדי שרות תוכל לפעול, עלינו להגדיר את המפתחות שלך פעם אחת.\n")

    api_key = input("🔑 הכנס API Key של OpenRouter (או OpenAI): ").strip()
    github_token = input("🐙 הכנס GitHub Personal Access Token: ").strip()

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config_data = json.load(f)
    except:
        config_data = {
            "BASE_URL": "https://openrouter.ai/api/v1",
            "MODEL": "openai/gpt-4o",
        }

    config_data["API_KEY"] = api_key
    config_data["GITHUB_TOKEN"] = github_token

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4, ensure_ascii=False)

    print(f"\n✅ ההגדרות נשמרו בנתיב: {CONFIG_PATH}")


def get_git_repo():
    try:
        url = (
            subprocess.check_output(
                ["git", "remote", "get-url", "origin"], stderr=subprocess.DEVNULL
            )
            .decode()
            .strip()
        )

        if "github.com/" in url:
            repo = url.split("github.com/")[-1].replace(".git", "")
            return repo
    except:
        return None
    return None


def update_registry(project_path, repo_name):
    registry = {}
    if os.path.exists(REGISTRY_PATH):
        try:
            with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
                registry = json.load(f)
        except:
            registry = {}

    registry[project_path] = {
        "repo": repo_name,
        "last_active": str(Path(project_path).name),
    }

    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=4)


def check_process_running(script_name):
    """בודק אם סקריפט ספציפי כבר רץ ברקע כדי למנוע כפילויות"""
    try:
        output = subprocess.check_output(["pgrep", "-f", script_name], text=True)
        return len(output.strip().split("\n")) > 0
    except subprocess.CalledProcessError:
        return False
    except Exception:
        return False


def main():
    # 1. בדיקת סביבה והתקנת חוסרים
    ensure_dependencies()
    check_and_install_alias()

    current_dir = os.getcwd()
    core_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(core_dir)

    # טעינת נתיבי הליבה
    sys.path.insert(0, os.path.join(core_dir, "core"))

    # 2. ניהול הגדרות ומפתחות
    try:
        from config_manager import Config

        Config._migrate_config()
        Config._load_config()

        if not Config.API_KEY:
            setup_wizard()
            setup_autostart()
            Config._load_config()
    except ImportError as e:
        print(f"⚠️ [Config Error] לא הצלחתי לטעון את מנגנון ההגדרות: {e}")
        if not os.path.exists(CONFIG_PATH):
            setup_wizard()
            setup_autostart()

    # ==========================================================
    # [מנוע העדכונים האוטומטיים] מופעל בחוט נפרד בזמן ההתנעה
    # ==========================================================
    try:
        from update_scheduler import start_background_updater

        start_background_updater()
    except ImportError as e:
        print(f"⚠️ [Updater Notice] מנגנון העדכונים לא זמין כרגע: {e}")
    # ==========================================================

    # 3. רישום הפרויקט ברג'יסטרי הגלובלי
    repo_name = get_git_repo() or os.path.basename(current_dir)
    update_registry(current_dir, repo_name)
    print(f"\n✅ [Root] הפרויקט '{repo_name}' נרשם במערכת.")

    # 4. שילוב המפלצת (Scanner) - זיהוי פרויקטים חדשים חכם
    root_db_path = os.path.join(current_dir, ".root")
    if not os.path.exists(root_db_path):
        print(f"🌿 נראה שזה פרויקט חדש עבורי ({Path(current_dir).name})")
        choice = input(
            "👉 תרצה שאבצע סריקת עומק (Monster Scan) כדי ללמוד את הארכיטקטורה שלו? (y/n): "
        )
        if choice.lower() == "y":
            try:
                from scanner import MonsterScanner

                scanner = MonsterScanner(current_dir)
                scanner.scan_and_index()
            except ImportError as e:
                print(f"⚠️ לא הצלחתי לטעון את הסורק: {e}")

    # 5. התנעת מנועים גלובלית
    service_script = os.path.join(core_dir, "core", "root_service.py")
    bridge_script = os.path.join(root_dir, "dashboard", "bridge_server.py")

    print("🚀 בודק סטטוס מנועים...")

    # הפעלת ה-Service הגלובלי (רק אם לא רץ כבר)
    if not check_process_running("root_service.py") and os.path.exists(service_script):
        subprocess.Popen(
            [sys.executable, service_script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,  # הופך אותו ל-Daemon עצמאי
        )
        print("🌍 [Global Service] מנוע ההשגחה הופעל ברקע.")
    else:
        print("🌍 [Global Service] המנוע כבר רץ ברקע ומאזין.")

    # הפעלת הדשבורד
    if not check_process_running("bridge_server.py") and os.path.exists(bridge_script):
        subprocess.Popen(
            [sys.executable, bridge_script, current_dir],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        print("🖥️  הדשבורד הופעל. זמין בכתובת: http://localhost:5050")
    else:
        print("🖥️  הדשבורד פעיל.")

    print(
        "\n🌿 Root OS פועלת בצללים. אין צורך להפעיל שוב - פשוט סגור את הטרמינל ותמשיך לעבוד."
    )


if __name__ == "__main__":
    main()
