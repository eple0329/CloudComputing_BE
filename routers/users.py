from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class User(BaseModel):
    id: str
    name: str
    email: str
    callPhobiaScore: int
    createdAt: str
    updatedAt: str

def example_user(user_id: str = None):
    return {
        "id": user_id or "user-1234",
        "name": "홍길동",
        "email": "hong@test.com",
        "callPhobiaScore": 73,
        "createdAt": "2024-06-01T12:00:00Z",
        "updatedAt": "2024-06-01T12:00:00Z"
    }

@router.post("")
async def create_user(user: dict):
    return {"success": True, "data": example_user()}

@router.get("/{user_id}")
async def get_user(user_id: str):
    return {"success": True, "data": example_user(user_id)}

@router.put("/{user_id}")
async def update_user(user_id: str, user: dict):
    updated = example_user(user_id)
    updated.update(user)
    updated["updatedAt"] = datetime.utcnow().isoformat() + "Z"
    return {"success": True, "data": updated}
