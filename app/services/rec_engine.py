import json
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from app.utils.db import db
import redis.asyncio as redis
import os
from dotenv import load_dotenv

load_dotenv()
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

class RecommendationEngine:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.product_ids = [p["id"] for p in db.get_products()]
        self.embeddings = None

    async def _generate_embeddings(self):
        if self.embeddings is not None:
            return

        cache_key = "embeddings"
        cached = await redis_client.get(cache_key)
        if cached:
            embeddings = np.frombuffer(cached, dtype=np.float32).reshape(-1, 384)
            # Build FAISS index from cached embeddings
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)
            self.index.add(embeddings)
            self.embeddings = embeddings
        else:
            texts = [f"{p['name']} {p['description']}" for p in db.get_products()]
            embeddings = self.model.encode(texts, convert_to_numpy=True, clean_up_tokenization_spaces=True)
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)
            faiss.normalize_L2(embeddings)
            self.index.add(embeddings)
            await redis_client.setex(cache_key, 86400, embeddings.tobytes())
            self.embeddings = embeddings

    async def get_recommendations(self, user_query: str, user_id: str = None, top_k: int = 3):
        cache_key = f"rec:{user_query}:{user_id or 'none'}"
        cached = await redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        
        query_text = user_query
        if user_id:
            user = db.get_user(user_id)
            if user:
                user_context = " ".join(user["purchase_history"] + user["preferences"])
                query_text += f" {user_context}"
        
        # Ensure embeddings and index are generated
        if self.embeddings is None:
            await self._generate_embeddings()
        
        query_embedding = self.model.encode([query_text], convert_to_numpy=True, clean_up_tokenization_spaces=True)
        faiss.normalize_L2(query_embedding)  # Normalize query for cosine similarity
        distances, indices = self.index.search(query_embedding, top_k)
        recommended_ids = [self.product_ids[idx] for idx in indices[0]]
        await redis_client.setex(cache_key, 3600, json.dumps(recommended_ids))
        return recommended_ids

    
        """
    def get_recommendations(self, user_query: str, user_id: str = None, top_k: int = 3):
        query_text = user_query
        if user_id:
            user = db.get_user(user_id)
            if user:
                user_context = " ".join(user["purchase_history"] + user["preferences"])
                query_text += f" {user_context}"
        
        query_embedding = self.model.encode([query_text], convert_to_numpy=True)
        distances, indices = self.index.search(query_embedding, top_k)
        recommended_ids = [self.product_ids[idx] for idx in indices[0]]
        return recommended_ids
    """

    """    
    def _generate_embeddings(self):
        texts = [f"{p['name']} {p['description']}" for p in db.get_products()]
        embeddings = self.model.encode(texts, convert_to_numpy=True, clean_up_tokenization_spaces=True)
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)
        return embeddings
    """


rec_engine = RecommendationEngine()