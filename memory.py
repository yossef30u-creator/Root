# =====
import json
import os
import numpy as np
from openai import OpenAI
from config import Config
# =====

# =====
class RootMemory:
    # =====
    def __init__(self, storage_path=".root/memory.json"):
        self.storage_path = storage_path
        self.client = OpenAI(
            api_key=Config.OPENAI_API_KEY, 
            base_url=Config.BASE_URL,
            default_headers={
                "HTTP-Referer": "https://github.com/RootProject",
                "X-Title": "Root Agentic OS",
            }
        )
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
    def add_memory(self, text, metadata=None):
        embedding = self._get_embedding(text)
        if not embedding:
            return False

        new_entry = {
            "text": text,
            "vector": embedding,
            "metadata": metadata or {}
        }
        self.memory_data.append(new_entry)
        
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(self.memory_data, f, ensure_ascii=False, indent=4)
        
        print(f"🧠 [Memory DB] Saved (Total: {len(self.memory_data)})")
        return True
    # =====

    # =====
    def search(self, query, top_k=3):
        if not self.memory_data:
            return []
            
        query_vector = self._get_embedding(query)
        if not query_vector:
            return []
        
        results = []
        for item in self.memory_data:
            similarity = np.dot(query_vector, item["vector"]) / (
                np.linalg.norm(query_vector) * np.linalg.norm(item["vector"])
            )
            results.append((similarity, item))
            
        results.sort(key=lambda x: x[0], reverse=True)
        return results[:top_k]
    # =====
# =====
