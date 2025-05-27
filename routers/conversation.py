from fastapi import APIRouter

router = APIRouter()

@router.post("/process")
async def process_conversation(data: dict):
    return {"success": True, "data": {"aiResponse": "AI 응답", "audioUrl": "/static/audio/ai.mp3"}}
