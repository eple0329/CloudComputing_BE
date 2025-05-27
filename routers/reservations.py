from fastapi import APIRouter

router = APIRouter()

@router.post("")
async def create_reservation(reservation: dict):
    return {"success": True, "data": reservation}

@router.get("/user/{user_id}")
async def get_user_reservations(user_id: str):
    return {"success": True, "data": [{"id": "1", "userId": user_id}]}

@router.delete("/{reservation_id}")
async def cancel_reservation(reservation_id: str):
    return {"success": True}
