"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.chatbot_engine import chatbot_engine

router = APIRouter()

class ChatInput(BaseModel):
    message: str

@router.post("/conversation", summary="Get conversational shopping response")
def chat(input: ChatInput):
    try:
        response = chatbot_engine.get_response(input.message)
        return {"reply": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")    
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.chatbot_engine import ChatbotEngine
import asyncio

router = APIRouter()

class ChatInput(BaseModel):
    message: str | list[str]

@router.post("/conversation", summary="Get conversational shopping response")
async def chat(input: ChatInput):
    try:
        if isinstance(input.message, str):
            response = await ChatbotEngine().get_response(input.message)
            return {"reply": response}
        elif isinstance(input.message, list):
            responses = await ChatbotEngine().get_batch_response(input.message)
            return {"replies": responses}
        else:
            raise HTTPException(status_code=400, detail="Invalid input format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")