#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ==============================================================================
# 👁️ Root OS: Sovereign Git Engine (Vision Module)
# ------------------------------------------------------------------------------
# תפקיד: קריאת מערכת הקבצים, ניהול .rootignore, והפקת Diff נקי מרעשים.
# ==============================================================================

import os
import subprocess
import fnmatch
from datetime import datetime

DEFAULT_IGNORE = [
    "node_modules/*",
    ".git/*",
    "venv/*",
    "__pycache__/*",
    "*.pyc",
    "*.exe",
    "*.dll",
    "*.so",
    "*.dat",
    "*.lock",
    "package-lock.json",
    "yarn.lock",
    ".DS_Store",
]


def load_rootignore(project_dir):
    """טוען חוקי סינון מ-.rootignore מהפרויקט הנוכחי"""
    ignore_patterns = DEFAULT_IGNORE.copy()
    ignore_file = os.path.join(project_dir, ".rootignore")
    if os.path.exists(ignore_file):
        with open(ignore_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    ignore_patterns.append(line)
    return ignore_patterns


def is_ignored(file_path, patterns):
    """בדיקה אטומית האם קובץ נמצא תחת חוקי הסינון"""
    for pattern in patterns:
        if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(
            os.path.basename(file_path), pattern
        ):
            return True
    return False


def get_git_info(project_dir):
    """
    סורק את ה-Git Repo ומחזיר Diff מסונן ומידע על הקומיט.
    מחזיר: (diff_text, metadata, run_mode)
    """
    original_dir = os.getcwd()
    os.chdir(project_dir)

    try:
        ignore_patterns = load_rootignore(project_dir)

        # --- בדיקת מצב LIVE (שינויים שטרם נשמרו בקומיט) ---
        files_live = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"], capture_output=True, text=True
        ).stdout.splitlines()
        valid_live_files = [f for f in files_live if not is_ignored(f, ignore_patterns)]

        if valid_live_files:
            diff_cmd = ["git", "diff", "HEAD", "--"] + valid_live_files
            diff_live = subprocess.run(
                diff_cmd, capture_output=True, text=True
            ).stdout.strip()
            if diff_live:
                return diff_live, None, "LIVE"

        # --- בדיקת מצב FINAL (שינויים מהקומיט האחרון) ---
        files_final = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        valid_final_files = [
            f for f in files_final if not is_ignored(f, ignore_patterns)
        ]

        if not valid_final_files:
            return None, None, "NONE"

        diff_cmd_final = ["git", "diff", "HEAD~1", "HEAD", "--"] + valid_final_files
        diff_final = subprocess.run(
            diff_cmd_final, capture_output=True, text=True
        ).stdout.strip()

        if not diff_final:
            return None, None, "NONE"

        # חילוץ נתוני מז"פ על הקומיט
        log_text = subprocess.run(
            ["git", "log", "-1", "--pretty=format:%h|%an|%s"],
            capture_output=True,
            text=True,
        ).stdout.strip()
        commit_hash, author, message = log_text.split("|", 2)
        metadata = {
            "commit": commit_hash,
            "author": author,
            "message": message,
            "timestamp": datetime.now().isoformat(),
        }
        return diff_final, metadata, "FINAL"

    except Exception as e:
        print(f"❌ [Git Engine Error] Tracking failed: {e}")
        return None, None, "ERROR"
    finally:
        os.chdir(original_dir)  # הבטחת חזרה לנתיב המקורי
