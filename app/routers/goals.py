from fastapi import APIRouter, Depends, HTTPException
from app.middleware.auth import verify_token
from app.services.recommendation_service import RecommendationService
from app.models.requests import DailyGoalsRequest
from app.models.responses import DailyGoalsResponse

router = APIRouter()
recommendation_service = RecommendationService()

@router.post("/goals/daily", response_model=DailyGoalsResponse)
async def get_daily_goals(
    request: DailyGoalsRequest,
    token_data: dict = Depends(verify_token)
):
    """Get daily study goals for user"""
    try:
        user_id = request.userId
        auth_token = token_data.get("sub")  # Extract from token
        
        goals = await recommendation_service.generate_daily_goals(
            user_id,
            auth_token
        )
        
        total_time = sum(g.get("estimatedTime", 0) for g in goals)
        
        return DailyGoalsResponse(
            goals=goals,
            summary={
                "totalGoals": len(goals),
                "estimatedTotalTime": total_time
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))