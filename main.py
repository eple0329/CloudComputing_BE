from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import users, call_phobia, scenarios, sessions, speech, conversation, analysis, settings, reservations, stats, websocket
from dotenv import load_dotenv


load_dotenv()
app = FastAPI()

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 필요에 따라 허용할 origin을 지정하세요.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(call_phobia.router, prefix="/api/call-phobia", tags=["call-phobia"])
app.include_router(scenarios.router, prefix="/api/scenarios", tags=["scenarios"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])
app.include_router(speech.router, prefix="/api/speech", tags=["speech"])
app.include_router(conversation.router, prefix="/api/conversation", tags=["conversation"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])
app.include_router(reservations.router, prefix="/api/reservations", tags=["reservations"])
app.include_router(stats.router, prefix="/api/stats", tags=["stats"])
app.include_router(websocket.router, prefix="/api/websocket", tags=["websocket"])

@app.get("/")
async def root():
    return {"message": "Hello World"}