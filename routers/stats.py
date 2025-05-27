from fastapi import APIRouter

router = APIRouter()

@router.get("/{user_id}")
async def get_stats(user_id: str):
    return {"success": True, "data":
        {
            "userId": user_id,
            "totalSessions": 20,
            "completedSessions": 15,
            "averageScore": 80,
            "improvementRate": 10,
            "favoriteScenarios": ["ars"],
            "weeklyProgress": [{
                "week": "week",
                "sessionsCount": 5,
                "averageScore": 95
            }],
            "lastUpdated": "today"
        }
    }