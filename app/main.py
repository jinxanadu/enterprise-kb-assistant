from typing import Optional
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from app.router_graph import router_graph

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

@app.post("/chat", response_model=ChatResp)
def chat(req: ChatReq):
    payload = req.model_dump()
    sid = payload.get("session_id")
    if sid and sid in SESSIONS:
        prev = SESSIONS[sid]
        merged = {**prev, **payload}
        merged["text"] = payload.get("text")
        payload = merged

    out = router_graph.invoke(payload)

    if sid:
        SESSIONS[sid] = {**payload, **out}

    return {"answer": out["answer"]}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8002, reload=True)