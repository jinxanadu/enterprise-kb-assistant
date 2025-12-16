from typing import Optional
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from app.router_graph import router_graph
from app.db.redis_session import load_session, save_session
import uuid

SESSIONS: dict[str, dict] = {}
app = FastAPI(title="Enterprise KB Assistant")

class ChatReq(BaseModel):
    text: str
    user_role: str = "public"
    requester: str = "anonymous"
    mode: Optional[str] = None
    session_id: Optional[str] = None  # ⚠️加这一行

class ChatResp(BaseModel):
    answer: str
    session_id: Optional[str] = None    # ⚠️添加
    active_route: Optional[str] = None  # ⚠️添加

@app.post("/chat", response_model=ChatResp)
def chat(req: ChatReq):
    payload = req.model_dump()
    text = payload.get("text") or payload.get("question") or ""

    # 1) get or create session id
    sid = payload.get("session_id") or f"sid-{uuid.uuid4().hex[:10]}"
    payload["session_id"] = sid

    # 2) load previous state from redis and merge
    prev_state = load_session(sid)
    if prev_state:
        merged = {**prev_state, **payload}
        merged["text"] = text
        payload = merged

    # 3) run router graph
    out = router_graph.invoke(payload)

    # 4) save new state to redis
    new_state = {**payload, **out}
    save_session(sid, new_state)

    return {
        "answer": out.get("answer"),
        "session_id": sid,
        "active_route": new_state.get("active_route"),
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8002, reload=True)