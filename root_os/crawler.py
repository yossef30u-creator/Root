# =====
import os
from memory import RootMemory

# =====

# =====
IGNORE_DIRS = [".git", ".root", "venv", "__pycache__"]
ALLOWED_EXTENSIONS = [".py", ".md"]
# =====


# =====
def crawl_project():
    print("🕷️ [Crawler] Starting scan...")
    mem = RootMemory()
    files_indexed = 0

    for root_dir, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file in files:
            if any(file.endswith(ext) for ext in ALLOWED_EXTENSIONS):
                file_path = os.path.join(root_dir, file)
                # =====
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    if content.strip():
                        mem.add_memory(
                            text=f"File: {file_path}\nContent:\n{content}",
                            metadata={"type": "crawl", "file": file_path},
                        )
                        files_indexed += 1
                except Exception as e:
                    print(f"❌ Error indexing {file_path}: {e}")
                # =====

    print(f"🎉 Indexed {files_indexed} files.")


# =====

# =====
if __name__ == "__main__":
    crawl_project()
# =====
