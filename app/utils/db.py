from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
        self.db = self.client["retail_db"]
        self.products = self.db["products"]
        self.users = self.db["users"]

    def get_products(self):
        return list(self.products.find())

    def get_user(self, user_id):
        return self.users.find_one({"user_id": user_id})

    def get_products_by_ids(self, product_ids):
        return list(self.products.find({"id": {"$in": product_ids}}))

db = Database()