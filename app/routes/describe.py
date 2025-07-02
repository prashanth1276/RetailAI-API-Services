"""from fastapi import APIRouter, Query, HTTPException
from app.utils.db import db
from app.services.genai_writer import description_generator
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/description", summary="Generate product description")
def get_description(product_id: str = Query(..., description="Product ID to generate description for")):
    logger.info(f"Received request for product_id: {product_id}")
    try:
        # Ensure product_id is a string and not empty
        if not product_id or not isinstance(product_id, str):
            raise HTTPException(status_code=422, detail="Invalid product ID format")
        
        # Fetch product from MongoDB
        product = db.products.find_one({"id": product_id})
        if not product:
            logger.warning(f"Product not found for ID: {product_id}")
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Generate description
        description = description_generator.generate_description(
            product.get("name", "Unknown Product"),  # Fallback if name is missing
            product.get("category", "Unknown Category"),  # Fallback if category is missing
            product.get("material", "cotton")  # Use product material if available
        )
        return {"description": description}
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error generating description: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Description error: {str(e)}")
    
"""

from fastapi import APIRouter, Query, HTTPException
from app.utils.db import db
from app.services.genai_writer import description_generator
import logging
import redis.asyncio as redis
from dotenv import load_dotenv
import os
import json
import asyncio

load_dotenv()
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/description", summary="Generate product description")
async def get_description(product_id: str = Query(..., description="Product ID to generate description for")):
    logger.info(f"Received request for product_id: {product_id}")
    try:
        if not product_id or not isinstance(product_id, str):
            raise HTTPException(status_code=422, detail="Invalid product ID format")
        
        cache_key = f"desc:{product_id}"
        cached = await redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        
        product = db.products.find_one({"id": product_id})
        if not product:
            logger.warning(f"Product not found for ID: {product_id}")
            raise HTTPException(status_code=404, detail="Product not found")
        
        loop = asyncio.get_event_loop()
        description = await loop.run_in_executor(None, lambda: description_generator.generate_description(
            product.get("name", "Unknown Product"),
            product.get("category", "Unknown Category"),
            product.get("material", "cotton")
        ))
        await redis_client.setex(cache_key, 86400, json.dumps({"description": description}))  # Cache for 24 hours
        return {"description": description}
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error generating description: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Description error: {str(e)}")