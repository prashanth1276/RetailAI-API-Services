from fastapi import APIRouter, Query, HTTPException
from app.services.rec_engine import rec_engine

router = APIRouter()

@router.get("/recommendations", summary="Get personalized product recommendations")
async def get_recommendations(query: str = Query(..., description="User's search query"), user_id: str | None = None):
    try:
        recommendations = await rec_engine.get_recommendations(query, user_id)
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation error: {str(e)}")