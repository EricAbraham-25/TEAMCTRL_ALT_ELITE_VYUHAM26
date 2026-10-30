
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.models.company import User
from app.core.dependencies import get_current_user
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.claude_agent import run_agent

router = APIRouter(prefix="/api/chat", tags=["AI Agent"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=ChatResponse)
def chat_with_agent(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        answer = run_agent(db, request.question, current_user)
        return ChatResponse(answer=answer)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="AI agent encountered an error. Check backend logs."
        )