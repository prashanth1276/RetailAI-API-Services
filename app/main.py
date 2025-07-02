from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import recommend, chat, describe
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis
import os
from dotenv import load_dotenv
from app.utils.db import db

load_dotenv()

app = FastAPI(title="Retail AI API", description="AI-powered retail backend", version="1.0")

# CORS for MERN integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust for your MERN app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis setup for caching and rate limiting
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

# Rate limiting
@app.on_event("startup")
async def startup():
   await FastAPILimiter.init(redis_client)  # Configure Redis

# Include routes
app.include_router(recommend.router, prefix="/api", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
app.include_router(chat.router, prefix="/api", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
app.include_router(describe.router, prefix="/api", dependencies=[Depends(RateLimiter(times=10, seconds=60))])

@app.get("/", summary="Welcome endpoint")
def read_root():
    return {"message": "Welcome to the Retail AI API"}