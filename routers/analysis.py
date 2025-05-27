from fastapi import APIRouter

router = APIRouter()

@router.post("/analyze")
async def analyze(data: dict):
    return {"success": True, "data": {"result": "분석 결과"}}

@router.get("/{session_id}")
async def get_analysis(session_id: str):
    return {"success": True, "data": {"sessionId": session_id, "result": "분석 결과"}}
