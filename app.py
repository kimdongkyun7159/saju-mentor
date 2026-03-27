"""사주멘토 — FastAPI 라우팅 (100줄 이하)"""

import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from modules.chat.service import ChatService

chat_service = ChatService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await chat_service.init_db()
    yield

app = FastAPI(title="사주멘토", version="1.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


class LoginRequest(BaseModel):
    nickname: str = Field(..., min_length=1, max_length=50)
    birth_year: int = Field(..., ge=1900, le=2100)
    birth_month: int = Field(..., ge=1, le=12)
    birth_day: int = Field(..., ge=1, le=31)
    birth_hour: int = Field(..., ge=0, le=23)
    gender: str = Field(default="male")
    calendar_type: str = Field(default="solar")
    is_intercalation: bool = Field(default=False)


class ChatRequest(BaseModel):
    user_id: int
    message: str = Field(..., min_length=1, max_length=2000)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/login")
async def login(req: LoginRequest):
    result = await chat_service.login(
        req.nickname, req.birth_year, req.birth_month,
        req.birth_day, req.birth_hour, gender=req.gender,
        calendar_type=req.calendar_type,
        is_intercalation=req.is_intercalation,
    )
    return result


@app.get("/chat/{user_id}", response_class=HTMLResponse)
async def chat_page(request: Request, user_id: int):
    from modules.memory.user_profile import UserProfileManager
    from modules.memory.database import DB_PATH
    mgr = UserProfileManager(DB_PATH)
    user = await mgr.get_user(user_id)
    if not user:
        return templates.TemplateResponse("index.html", {"request": request})
    saju_data = json.loads(user["saju_data"]) if user.get("saju_data") else {}
    
    from datetime import datetime
    from modules.calculator.daeun import get_current_fortune
    cf = get_current_fortune(saju_data.get('pillars', {}), datetime.now())
    saju_data['yearly_fortune'] = cf['yearly']
    saju_data['monthly_fortune'] = cf['monthly']
    
    from modules.interpreter.base import SajuInterpreter
    interp = SajuInterpreter()
    saju_obj = type("R", (), {"to_dict": lambda s: saju_data, "birth_info": saju_data.get("birth_info", {}), "summary": saju_data.get("summary", {})})()
    greeting = interp.get_greeting(saju_obj)
    return templates.TemplateResponse("chat.html", {
        "request": request,
        "user_id": user_id,
        "nickname": user["nickname"],
        "saju_json": json.dumps(saju_data, ensure_ascii=False),
        "greeting_json": json.dumps(greeting, ensure_ascii=False),
    })


@app.post("/api/chat")
async def chat(req: ChatRequest):
    result = await chat_service.chat(req.user_id, req.message)
    return result


@app.exception_handler(Exception)
async def global_error(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": str(exc)})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5031)
