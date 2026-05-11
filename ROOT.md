# 🌳 Root OS: Sovereign Atomic Architecture

> **הוראת מערכת:** זהו מניפסט ה-DNA המוחלט. כל בורג מתועד. אין פה היסטוריה.

# Root OS - High-Level and Low-Level Design Document

## 🏗️ Runtime Topology (The Orchestration Engine & Process Model)

Root OS operates as an orchestration engine based on a daemon model, continuously running across various platforms (Windows, macOS, Linux, Termux). The core runtime units include:

- **rootd (Main Daemon):** Manages all worker processes.
- **Watcher Worker:** Listens to real-time filesystem events.
- **Ingestion Worker (Monster Ingestor):** Processes changed code using a smart diff mechanism, filtering through `.rootignore`.

## 📦 Micro-Component Inventory (EVERY file mapped in an atomic table)

| Path                                      | Role                                      | Logic Gate | Data Contracts | Dependencies |
|-------------------------------------------|-------------------------------------------|------------|----------------|--------------|
| `=0.5.0`                                  | Dependency management log                 | N/A        | N/A            | N/A          |
| `.env`                                    | Environment variables configuration       | N/A        | N/A            | N/A          |
| `.gitignore`                              | Git ignore rules                          | N/A        | N/A            | N/A          |
| `README_SECURITY.md`                      | Security and environment guide            | N/A        | N/A            | N/A          |
| `README.md`                               | Project overview and vision               | N/A        | N/A            | N/A          |
| `פקודות הפעלה.md`                        | Execution commands guide                  | N/A        | N/A            | N/A          |
| `Architecture.md`                         | System architecture and runtime blueprint | N/A        | N/A            | N/A          |
| `requirements.txt`                        | Python dependencies list                  | N/A        | N/A            | N/A          |
| `ONBOARDING.md`                           | Onboarding guide for new developers       | N/A        | N/A            | N/A          |
| `pyproject.toml`                          | Project metadata and build configuration  | N/A        | N/A            | N/A          |
| `start.sh`                                | Shell script to start the system          | N/A        | N/A            | N/A          |
| `Setup_root.py`                           | Setup script for environment preparation  | N/A        | N/A            | N/A          |
| `.github/workflows/root_action.yml`       | GitHub Actions workflow for CI/CD         | N/A        | N/A            | N/A          |
| `root_os.egg-info/entry_points.txt`       | Entry points for the package              | N/A        | N/A            | N/A          |
| `root_os.egg-info/PKG-INFO`               | Package metadata                          | N/A        | N/A            | N/A          |
| `root_os.egg-info/requires.txt`           | Package requirements                      | N/A        | N/A            | N/A          |
| `root_os.egg-info/top_level.txt`          | Top-level package directory               | N/A        | N/A            | N/A          |
| `root_os.egg-info/SOURCES.txt`            | Source files list                         | N/A        | N/A            | N/A          |
| `root_os/config.py`                       | Configuration management                  | N/A        | N/A            | N/A          |
| `root_os/memory.py`                       | Memory management and storage             | N/A        | N/A            | N/A          |

## 🔌 Data Contracts & Logic Interfaces (How modules talk to each other)

- **Environment Variables (.env):** Used for API keys, model configurations, and system settings.
- **Configuration Management (config.py):** Loads environment variables and provides configuration settings to other modules.
- **Memory Management (memory.py):** Handles both short-term and long-term memory using JSON and ChromaDB (if available).

## 🛡️ Operational Boundaries (Resource limits, RAM guards, Security rules)

- **Memory Limits:** Maximum of 1500 records for lite mode and 50 MB file size limit to prevent RAM overload.
- **Python Version:** Requires Python 3.8 or higher.
- **Security:** Sensitive files like `.env` are protected and not included in version control.

## 📊 Persistence Matrix (Path-specific storage rules)

| Storage Path                | Description                           |
|-----------------------------|---------------------------------------|
| `.root/memory.json`         | JSON file for short-term memory       |
| `.root/chroma_db`           | Directory for ChromaDB storage        |
| `ROOT.md`                   | Markdown file for project documentation |

BlueprintID: 9edaf09ec8ed

---
*📐 אדריכלות מאומתת: 11/05/2026 17:56 | מנוע: Root OS Master Architect V2*