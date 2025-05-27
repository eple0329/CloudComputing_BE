from fastapi import APIRouter

router = APIRouter()

@router.get("/{user_id}")
async def get_settings(user_id: str):
    return {"success": True, "data": {"userId": user_id, "setting": "설정값"}}

@router.put("/{user_id}")
async def update_settings(user_id: str, settings: dict):
    return {"success": True, "data": settings}
