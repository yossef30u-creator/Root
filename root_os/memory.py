#####
#!/usr/bin/env python3
# =====
import json
import os
import hashlib
import numpy as np
import atexit  # הוסף לתמיכה בנעילה וסגירה אלגנטית (הטאקסיט)
from openai import OpenAI
from root_os.core.config_manager import Config

# ניסיון ייבוא של ChromaDB. מאפשר למערכת לרוץ גם בטרמוקס (ללא כרומה) וגם בענן
try:
    import chromadb

    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
# =====


# =====
class RootMemory:
    # =====
    def __init__(self, storage_path=".root/memory.json", chroma_path=".root/chroma_db"):
        self.storage_path = storage_path
        self.chroma_path = chroma_path
        self.use_chroma = CHROMA_AVAILABLE
        self.max_lite_records = (
            1500  # צופה פני עתיד: הגבלת זיכרון בטלפון למניעת קריסת RAM
        )
        self.max_file_size_mb = 50  # תוספת חדשה: הגבלת משקל קובץ ב-MB למניעת עומס קריאה

        # אתחול הלקוח. משתמש ב-API_KEY מההגדרות המשותפות
        self.client = OpenAI(
            api_key=Config.API_KEY,
            base_url=Config.BASE_URL,
            default_headers={
                "HTTP-Referer": "https://github.com/RootProject",
                "X-Title": "Root Agentic OS",
            },
        )

        if self.use_chroma:
            print(
                "[Memory] ChromaDB detected. Initializing Cloud-Scale Vector DB..."
            )
            self.chroma_client = chromadb.PersistentClient(path=self.chroma_path)
            self.collection = self.chroma_client.get_or_create_collection(
                name="root_project_memory"
            )
        else:
            print(
                "[Memory] ChromaDB not found. Falling back to lightweight JSON/Numpy DB."
            )
            self.memory_data = self._load_memory()
            self._enforce_size_limits()  # בדיקת גודל אקטיבית כבר בהפעלה

        # רישום atexit לסגירה אלגנטית ושמירה בטוחה של זכרונות אם התהליך נקטע
        atexit.register(self.graceful_shutdown)

    # =====

    # =====
    def graceful_shutdown(self):
        """הטאקסיט: פונקציה שתרוץ תמיד בסגירת התוכנית כדי להבטיח שלא נאבד מידע ואין השחתה"""
        print("[Memory] Graceful shutdown initiated. Securing memory states...")
        if not self.use_chroma:
            self._safe_json_save()
        print("[Memory] Memory secured safely.")

    # =====

    # =====
    def _generate_hash(self, text):
        """צופה פני עתיד: ייצור טביעת אצבע לטקסט למניעת כפילויות בזיכרון"""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    # =====

    # =====
    def _load_memory(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print("⚠️ [Memory] Warning: Memory file corrupted. Starting fresh.")
                return []
        return []

    # =====

    # =====
    def _enforce_size_limits(self):
        """
        ניהול זיכרון אוטומטי (מחיקה לפי גודל):
        בודק אם קובץ ה-JSON חורג מהמשקל המותר ב-MB.
        אם כן, מקצץ את 20% מהרשומות הישנות ביותר כדי לפנות אוויר למערכת.
        """
        if not os.path.exists(self.storage_path) or not hasattr(self, "memory_data"):
            return

        file_size_mb = os.path.getsize(self.storage_path) / (1024 * 1024)
        if file_size_mb > self.max_file_size_mb:
            print(
                f"[Memory] File size ({file_size_mb:.2f}MB) exceeds limit ({self.max_file_size_mb}MB). Pruning old memory..."
            )
            trim_count = int(
                self.max_lite_records * 0.2
            )  # מחיקת 20% מהזכרונות העתיקים ביותר
            self.memory_data = self.memory_data[trim_count:]
            # הכתיבה מבוצעת על ידי הקריאות הקיימות ממילא או בסגירה

    # =====

    # =====
    def _safe_json_save(self):
        """צופה פני עתיד: כתיבה אטומית. מונע השחתת קובץ אם התוכנית קורסת באמצע השמירה"""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        temp_path = self.storage_path + ".tmp"

        # ניקוי ישנים אם עברנו את המקסימום המותר לטלפון בכמות הרשומות
        if len(self.memory_data) > self.max_lite_records:
            self.memory_data = self.memory_data[-self.max_lite_records :]

        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(self.memory_data, f, ensure_ascii=False, indent=4)

        # החלפה אטומית - 100% בטוח
        os.replace(temp_path, self.storage_path)

        # אכיפת משקל פיזי מיד אחרי השמירה
        self._enforce_size_limits()

    # =====

    # =====
    def _get_embedding(self, text):
        try:
            # הערה: אם משתמשים ב-OpenRouter, ודא שהמודל נתמך, או השתמש ב-API של OpenAI ישירות
            response = self.client.embeddings.create(
                input=text, model="text-embedding-3-small"
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"❌ [Memory API Error]: Failed to generate embedding. {e}")
            return None

    # =====

    # =====
    def add_memory(self, text, metadata=None, user_id="root_system"):
        """
        שומר זכרונות עם הגנה נגד כפילויות, תמיכה במולטי-יוזר ושמירה בטוחה.
        """
        doc_hash = self._generate_hash(text)
        meta = metadata or {}
        meta["user_id"] = user_id
        meta["hash_id"] = doc_hash

        if self.use_chroma:
            # בדיקה מהירה אם ה-Hash כבר קיים ב-ChromaDB
            existing = self.collection.get(ids=[doc_hash])
            if existing and existing["ids"]:
                print(f"🔄 [Memory DB] Duplicate detected. Skipping Chroma save.")
                return True

            embedding = self._get_embedding(text)
            if not embedding:
                return False

            self.collection.add(
                documents=[text],
                embeddings=[embedding],
                metadatas=[meta],
                ids=[doc_hash],  # מזהה ייחודי מבוסס תוכן
            )
            print(f"🧠 [Memory DB] Saved to Chroma (User: {user_id})")

        else:
            # בדיקת כפילויות ב-JSON Fallback
            if any(
                item.get("metadata", {}).get("hash_id") == doc_hash
                for item in self.memory_data
            ):
                print(f"🔄 [Memory DB] Duplicate detected. Skipping JSON save.")
                return True

            embedding = self._get_embedding(text)
            if not embedding:
                return False

            new_entry = {"text": text, "vector": embedding, "metadata": meta}
            self.memory_data.append(new_entry)
            self._safe_json_save()

            print(
                f"🧠 [Memory DB] Saved to JSON (Total: {len(self.memory_data)}/{self.max_lite_records})"
            )

        return True

    # =====

    # =====
    def search(self, query, top_k=3, user_id=None):
        query_vector = self._get_embedding(query)
        if not query_vector:
            return []

        if self.use_chroma:
            where_clause = {"user_id": user_id} if user_id else None

            results = self.collection.query(
                query_embeddings=[query_vector], n_results=top_k, where=where_clause
            )

            parsed_results = []
            if results["documents"] and results["documents"][0]:
                for i in range(len(results["documents"][0])):
                    parsed_results.append(
                        (
                            (
                                1.0 - results["distances"][0][i]
                                if "distances" in results
                                else 0
                            ),
                            {
                                "text": results["documents"][0][i],
                                "metadata": results["metadatas"][0][i],
                            },
                        )
                    )
            return parsed_results

        else:
            if not self.memory_data:
                return []

            results = []
            for item in self.memory_data:
                if user_id and item.get("metadata", {}).get("user_id") != user_id:
                    continue

                # חישוב מרחק קוסינוס מדויק
                similarity = np.dot(query_vector, item["vector"]) / (
                    np.linalg.norm(query_vector) * np.linalg.norm(item["vector"])
                )
                results.append((similarity, item))

            results.sort(key=lambda x: x[0], reverse=True)
            return results[:top_k]

    # =====

    # =====
    def search_memory(self, query, top_k=3, user_id=None):
        """Alias for backward compatibility"""
        return self.search(query, top_k, user_id)


#####
