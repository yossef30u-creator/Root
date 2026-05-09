# =====
import json
import os
import numpy as np
from openai import OpenAI
from config import Config

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
        
        # אנחנו שומרים על הלקוח המקורי והחכם שלך! קריטי לעבודה עם OpenRouter ורשתות שונות.
        self.client = OpenAI(
            api_key=Config.OPENAI_API_KEY, 
            base_url=Config.BASE_URL,
            default_headers={
                "HTTP-Referer": "https://github.com/RootProject",
                "X-Title": "Root Agentic OS",
            }
        )
        
        if self.use_chroma:
            print("⚡ [Memory] ChromaDB detected. Initializing Cloud-Scale Vector DB...")
            self.chroma_client = chromadb.PersistentClient(path=self.chroma_path)
            self.collection = self.chroma_client.get_or_create_collection(name="root_project_memory")
        else:
            print("⚠️ [Memory] ChromaDB not found. Falling back to lightweight JSON/Numpy DB.")
            self.memory_data = self._load_memory()
    # =====

    # =====
    def _load_memory(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []
    # =====

    # =====
    def _get_embedding(self, text):
        try:
            response = self.client.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"❌ [Memory Error]: {e}")
            return None
    # =====

    # =====
    def add_memory(self, text, metadata=None, user_id="root_system"):
        """
        צופה פני עתיד: הוספנו user_id למטא-דאטה. בעתיד כשיהיו כמה משתמשים/סוכנים, 
        נוכל לסנן זכרונות לפי מי שיצר אותם.
        """
        embedding = self._get_embedding(text)
        if not embedding:
            return False

        meta = metadata or {}
        meta["user_id"] = user_id # הכנה למולטי-יוזר

        if self.use_chroma:
            import uuid
            doc_id = str(uuid.uuid4())
            self.collection.add(
                documents=[text],
                embeddings=[embedding], # משתמשים ב-Embedding החכם שלנו
                metadatas=[meta],
                ids=[doc_id]
            )
            print(f"🧠 [Memory DB] Saved to Chroma (User: {user_id})")
        else:
            # Fallback ל-JSON
            new_entry = {
                "text": text,
                "vector": embedding,
                "metadata": meta
            }
            self.memory_data.append(new_entry)
            
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self.memory_data, f, ensure_ascii=False, indent=4)
            
            print(f"🧠 [Memory DB] Saved to JSON (Total: {len(self.memory_data)})")
            
        return True
    # =====

    # =====
    def search(self, query, top_k=3, user_id=None):
        query_vector = self._get_embedding(query)
        if not query_vector:
            return []
            
        if self.use_chroma:
            # צופה פני עתיד: חיפוש עם סינון לפי משתמש במידה וצריך
            where_clause = {"user_id": user_id} if user_id else None
            
            results = self.collection.query(
                query_embeddings=[query_vector],
                n_results=top_k,
                where=where_clause
            )
            
            parsed_results = []
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    parsed_results.append((
                        1.0 - results['distances'][0][i] if 'distances' in results else 0, # המרה ל-Similarity
                        {"text": results['documents'][0][i], "metadata": results['metadatas'][0][i]}
                    ))
            return parsed_results
            
        else:
            # Fallback לחיפוש ב-JSON עם Numpy
            if not self.memory_data: return []
            
            results = []
            for item in self.memory_data:
                # סינון מולטי-יוזר גם ברמת ה-JSON
                if user_id and item.get("metadata", {}).get("user_id") != user_id:
                    continue
                    
                similarity = np.dot(query_vector, item["vector"]) / (
                    np.linalg.norm(query_vector) * np.linalg.norm(item["vector"])
                )
                results.append((similarity, item))
                
            results.sort(key=lambda x: x[0], reverse=True)
            return results[:top_k]
    # =====

    # =====
    def search_memory(self, query, top_k=3, user_id=None):
        """ Alias to prevent backwards compatibility issues with ingestor.py """
        return self.search(query, top_k, user_id)
    # =====
# =====
