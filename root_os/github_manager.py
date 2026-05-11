#!/usr/bin/env python3
# =====
import requests
from config import Config
# =====

# =====
class GitHubManager:
    # =====
    def __init__(self):
        """אתחול מנהל התקשורת מול GitHub"""
        self.token = Config.GITHUB_TOKEN
        self.repo = Config.GITHUB_REPOSITORY # פורמט: "username/repository"
        
        if not self.token or not self.repo:
            print("⚠️ [GitHubManager] Missing credentials (GITHUB_TOKEN or GITHUB_REPOSITORY). Operating in OFFLINE mode.")
            self.is_active = False
        else:
            self.is_active = True
            self.base_url = f"https://api.github.com/repos/{self.repo}/issues"
            self.headers = {
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json",
                "X-GitHub-Api-Version": "2022-11-28" # קיבוע גרסת API ליציבות עתידית
            }
            self.timeout = 10 # מניעת תקיעות ברשתות איטיות
    # =====

    # =====
    def fetch_tasks(self, label="root-task", state="open"):
        """שולף משימות פתוחות שתויגו עבור הסוכן"""
        if not self.is_active:
            return []
            
        try:
            params = {"labels": label, "state": state}
            response = requests.get(self.base_url, headers=self.headers, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                issues = response.json()
                # מסנן Pull Requests (בגיטהאב, PR נחשב גם כ-Issue ברמת ה-API)
                tasks = [issue for issue in issues if "pull_request" not in issue]
                return tasks
            else:
                print(f"❌ [GitHubManager] Failed to fetch tasks: {response.status_code} - {response.text}")
                return []
        except requests.exceptions.RequestException as e:
            print(f"⚠️ [GitHubManager] Network error while fetching tasks: {e}")
            return []
    # =====

    # =====
    def comment_on_issue(self, issue_number, comment_body):
        """מוסיף תגובה למשימה כדי לעדכן סטטוס התקדמות"""
        if not self.is_active:
            print(f"📴 [Offline] Would have commented on #{issue_number}: {comment_body[:30]}...")
            return False
            
        try:
            url = f"{self.base_url}/{issue_number}/comments"
            data = {"body": comment_body}
            response = requests.post(url, headers=self.headers, json=data, timeout=self.timeout)
            
            if response.status_code == 201:
                return True
            else:
                print(f"❌ [GitHubManager] Failed to post comment on #{issue_number}: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"⚠️ [GitHubManager] Network error while commenting: {e}")
            return False
    # =====

    # =====
    def close_issue(self, issue_number):
        """סוגר את המשימה לאחר שהסוכן סיים לבצע אותה בהצלחה"""
        if not self.is_active:
            print(f"📴 [Offline] Would have closed issue #{issue_number}")
            return False
            
        try:
            url = f"{self.base_url}/{issue_number}"
            data = {"state": "closed"}
            response = requests.patch(url, headers=self.headers, json=data, timeout=self.timeout)
            
            if response.status_code == 200:
                print(f"🔒 [GitHubManager] Issue #{issue_number} successfully closed.")
                return True
            else:
                print(f"❌ [GitHubManager] Failed to close issue #{issue_number}: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"⚠️ [GitHubManager] Network error while closing issue: {e}")
            return False
    # =====
    
    # =====
    def create_issue(self, title, body, labels=None):
        """
        פתיחת משימה חדשה. 
        משמש בעיקר את ה-Proactive mode כשהסוכן מציע שיפורים.
        """
        if not self.is_active:
            return None
            
        try:
            data = {
                "title": title,
                "body": body,
                "labels": labels or ["root-task"]
            }
            response = requests.post(self.base_url, headers=self.headers, json=data, timeout=self.timeout)
            
            if response.status_code == 201:
                return response.json().get('number')
            else:
                print(f"❌ [GitHubManager] Failed to create issue: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"⚠️ [GitHubManager] Network error while creating issue: {e}")
            return None
    # =====
# =====
