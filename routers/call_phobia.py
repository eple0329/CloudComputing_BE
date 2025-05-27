from fastapi import APIRouter

router = APIRouter()

@router.get("/questions")
async def get_questions():
    return {"success": True, "data": ["질문1", "질문2"]}

@router.post("/submit")
async def submit_test(test_data: dict):
    return {"success": True, "data": test_data}

@router.get("/result/{user_id}")
async def get_result(user_id: str):
    return {"success": True, "data": {"userId": user_id, "score": 80}}
