import os
from dotenv import load_dotenv

# טעינה אקטיבית של הסביבה
load_dotenv()

def run_diagnostics():
    print('--- אבחון מערכת Root ---')
    
    # 1. בדיקת מפתח API
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key.startswith("sk-"):
        print(f"✅ API Key: Detected (Starts with {api_key[:7]}...)")
    else:
        print("❌ API Key: Missing or Invalid format in .env")

    # 2. בדיקת מודולים
    try:
        from root_brain import RootBrain
        from memory import RootMemory
        b = RootBrain()
        m = RootMemory()
        print(f"✅ Brain Module: Ready")
        print(f"✅ Memory Module: Ready ({m.__class__.__name__})")
    except ImportError as e:
        print(f"❌ Module Error: {e}")
    except Exception as e:
        print(f"❌ Init Error: {e}")

    # 3. בדיקת קבצי ליבה
    manifest_exists = os.path.exists("ROOT.md")
    print(f"✅ Manifest Check: {'Exists' if manifest_exists else 'Missing'}")
    
    if manifest_exists:
        with open("ROOT.md", "r", encoding="utf-8") as f:
            content = f.read()
            print(f"✅ Context awareness: {len(content)} characters loaded")

if __name__ == "__main__":
    run_diagnostics()
