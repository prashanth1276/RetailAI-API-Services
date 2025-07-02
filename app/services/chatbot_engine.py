"""import requests
from langchain.prompts import PromptTemplate
from app.utils.db import db
import logging
from app.services.rec_engine import rec_engine  # Import rec_engine here

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatbotEngine:
    def __init__(self, model="llama3"):
        self.model = model
        self.ollama_url = "http://localhost:11434/api/generate"
        self.prompt_template = PromptTemplate(
            input_variables=["query", "context"],
            template="You are a retail shopping assistant. The user asked: {query}\n"
                     "Available products:\n{context}\n"
                     "Provide a concise, friendly response in 2-3 sentences, recommending the most relevant products from the context."
        )

    def get_response(self, user_query: str):
        logger.info(f"Received user query: {user_query}")
        budget = None
        if "under" in user_query.lower():
            try:
                budget = float(user_query.lower().split("under")[1].split()[0])
            except:
                pass
        
        product_ids = rec_engine.get_recommendations(user_query, top_k=5)  # Use rec_engine
        products = db.get_products_by_ids(product_ids)
        if budget:
            products = [p for p in products if p.get("price", float("inf")) <= budget]
        
        context = "\n".join([f"- {p['name']}: {p['description']} (₹{p['price']})" for p in products])
        if not context:
            context = "No matching products found."
        
        prompt = self.prompt_template.format(query=user_query, context=context)
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        try:
            response = requests.post(self.ollama_url, json=payload)
            response.raise_for_status()
            result = response.json().get("response", "").strip()
            return result.split("<|end_header_id>")[-1].strip() if "<|end_header_id>" in result else result
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API error: {e}")
            return f"Error: {e}"

chatbot_engine = ChatbotEngine()
"""

import asyncio
import requests
from langchain.prompts import PromptTemplate
from app.utils.db import db
import logging
from app.services.rec_engine import rec_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatbotEngine:
    def __init__(self, model="llama3"):
        self.model = model
        self.ollama_url = "http://localhost:11434/api/generate"
        self.prompt_template = PromptTemplate(
            input_variables=["query", "context"],
            template="Summarize products for: {query}\nContext: {context}\nRespond in 2 sentences."
        )

    async def get_response(self, user_query: str):
        logger.info(f"Received user query: {user_query}")
        budget = None
        if "under" in user_query.lower():
            try:
                budget = float(user_query.lower().split("under")[1].split()[0])
            except:
                pass
        
        product_ids = await rec_engine.get_recommendations(user_query, top_k=5)
        products = db.get_products_by_ids(product_ids)
        if budget:
            products = [p for p in products if p.get("price", float("inf")) <= budget]
        
        context = "\n".join([f"- {p['name']}: {p['description']} (₹{p['price']})" for p in products])
        if not context:
            context = "No matching products found."
        
        prompt = self.prompt_template.format(query=user_query, context=context)
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        try:
            response = requests.post(self.ollama_url, json=payload)
            response.raise_for_status()
            result = response.json().get("response", "").strip()
            return result.split("<|end_header_id>")[-1].strip() if "<|end_header_id>" in result else result
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API error: {e}")
            return f"Error: {e}"

    async def get_batch_response(self, queries: list[str]):
        tasks = [self.get_response(query) for query in queries]
        return await asyncio.gather(*tasks)

chatbot_engine = ChatbotEngine()