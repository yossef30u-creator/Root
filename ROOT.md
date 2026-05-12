# 🌳 Root OS: Sovereign Atomic Architecture

> **הוראת מערכת:** זהו מניפסט ה-DNA המוחלט. כל בורג מתועד. אין פה היסטוריה.

# Root OS High-Level and Low-Level Design Document

## 1. 100% Inventory

### Files and Their Details

1. **`pyproject.toml`**
   - **Path**: Root directory
   - **Logical Role**: Dependency and project configuration
   - **Micro-Logic Gates**: Parses and validates project dependencies and configurations
   - **Dependencies**: Python 3.8+, Pydantic, Pybase64, ChromaDB

2. **`.env`**
   - **Path**: Root directory
   - **Logical Role**: Environment configuration
   - **Micro-Logic Gates**: Loads environment variables for secure API interactions
   - **Dependencies**: None, but critical for API operations

3. **`.gitignore`**
   - **Path**: Root directory
   - **Logical Role**: Version control configuration
   - **Micro-Logic Gates**: Filters out sensitive and unnecessary files from version control
   - **Dependencies**: None

4. **`ROOT.md`**
   - **Path**: Documentation directory
   - **Logical Role**: System documentation
   - **Micro-Logic Gates**: Provides comprehensive system overview
   - **Dependencies**: None

5. **`rootd.py`**
   - **Path**: Daemon directory
   - **Logical Role**: Main daemon process
   - **Micro-Logic Gates**: Manages worker processes and ensures continuous operation
   - **Dependencies**: Watcher Worker, Ingestion Worker

6. **`watcher_worker.py`**
   - **Path**: Workers directory
   - **Logical Role**: File system event monitoring
   - **Micro-Logic Gates**: Detects file system changes in real-time
   - **Dependencies**: File system APIs

7. **`ingestion_worker.py`**
   - **Path**: Workers directory
   - **Logical Role**: Code change processing
   - **Micro-Logic Gates**: Filters and processes code changes
   - **Dependencies**: `.rootignore`, ChromaDB

8. **`.rootignore`**
   - **Path**: Root directory
   - **Logical Role**: Ingestion filtering
   - **Micro-Logic Gates**: Specifies files to ignore during ingestion
   - **Dependencies**: Ingestion Worker

## 2. Architectural Rationale

### Core Modules

- **ChromaDB Integration**: ChromaDB is integrated to manage vector-based memory, enabling advanced semantic search capabilities. This is crucial for handling large-scale data processing and ensuring efficient retrieval of relevant information.
  
- **Pydantic and Pybase64**: Pydantic ensures robust data validation, while Pybase64 provides efficient base64 encoding/decoding. These libraries are essential for maintaining data integrity and security during API interactions.

- **Python 3.8+ Requirement**: The use of Python 3.8 and above allows for modern syntax and library compatibility, ensuring the system remains up-to-date with current programming standards.

## 3. The Continuous Loop

### Sub-Second Reaction Flow

1. **FileSystem Event**: Triggered by changes in the file system, such as file creation, modification, or deletion.
2. **Watcher**: The Watcher Worker detects these events in real-time and signals the Ingestor.
3. **Ingestor**: The Ingestion Worker processes the changes, filtering through `.rootignore` to exclude unnecessary files.
4. **Logic Handlers**: The processed data is then interpreted by the semantic engine, updating the system's context.
5. **Manifest Update**: The system's state is updated to reflect the new information, ensuring consistency and accuracy.

## 4. Data Contracts

### Schemas and Structures

- **Environment Variables**: Defined in `.env`, including `OPENAI_API_KEY` and `GITHUB_TOKEN`, which are strings used for secure API access.
  
- **Core Dumps (JSON Structure)**:
  ```json
  {
    "timestamp": "2023-10-01T12:00:00Z",
    "event_type": "file_change",
    "file_path": "/path/to/file",
    "change_type": "modified",
    "details": {
      "lines_added": 10,
      "lines_removed": 5
    }
  }
  ```

## 5. Operational Boundaries

### Context Limit and Locking Mechanism

- **220,000 Character Context Limit**: The system is designed to handle up to 220,000 characters in a single context, ensuring efficient processing without overloading memory resources.

- **Industrial Locking (atexit)**: Utilizes an `atexit` mechanism to ensure that all processes are gracefully terminated, preventing data corruption and ensuring system integrity.

## 6. Technical Hebrew

- **חסינות לוגית (Logical Immunity)**: The system's ability to maintain stability and correctness despite changes in the environment or input data.

- **וקטור ביצוע (Execution Vector)**: The path taken by the system to execute a particular task, from input to output.

- **צימוד אטומי (Atomic Coupling)**: The tight integration of system components to ensure seamless operation and data consistency.

---
*BlueprintID: c9f7a5e57df7*
*📐 אדריכלות מאומתת: 12/05/2026 12:40:25 | מנוע: Root OS Master Architect V2*