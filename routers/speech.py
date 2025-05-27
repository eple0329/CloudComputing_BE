from fastapi import APIRouter

router = APIRouter()

@router.post("/start-recognition")
async def start_recognition(data: dict):
    return {"success": True, "data": {"streamUrl": "ws://localhost/ws/audio"}}

@router.post("/synthesize")
async def synthesize(data: dict):
    return {"success": True, "data": {"audioUrl": "/static/audio/sample.mp3"}}
