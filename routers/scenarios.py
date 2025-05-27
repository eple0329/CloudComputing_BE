from fastapi import APIRouter
import json
import os

router = APIRouter()

SCENARIO_JSON_PATH = os.path.join(os.path.dirname(__file__), "../data/scenarios.json")

def load_scenarios():
    with open(SCENARIO_JSON_PATH, encoding="utf-8") as f:
        return json.load(f)

@router.get("")
async def get_scenarios(level: int = None):
    scenarios = load_scenarios()
    if level is not None:
        scenarios = [s for s in scenarios if s.get("level") == level]
    return {"success": True, "data": scenarios}

@router.get("/{scenario_id}")
async def get_scenario(scenario_id: str):
    scenarios = load_scenarios()
    scenario = next((s for s in scenarios if s.get("id") == scenario_id), None)
    return {"success": True, "data": scenario}

@router.get("/recommended/{user_id}")
async def get_recommended(user_id: str):
    scenarios = load_scenarios()
    # 예시: 난이도 1~2만 추천
    recommended = [s for s in scenarios if s.get("level", 0) <= 2]
    return {"success": True, "data": recommended}
