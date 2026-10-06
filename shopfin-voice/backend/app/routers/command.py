from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_business
from app.database.database import get_db
from app.models.business import Business
from app.models.conversation import Conversation
from app.schemas.command import CommandRequest, CommandResponse
from app.services.command_service import run_command

router = APIRouter()


@router.post("/", response_model=CommandResponse)
def send_command(
    request: CommandRequest,
    business: Business = Depends(get_current_business),
    db: Session = Depends(get_db),
):
    """Run a typed/dictated command such as 'today I saved 500' and save the result."""
    return run_command(db, business, request.text)


@router.get("/history")
def command_history(
    business: Business = Depends(get_current_business),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(Conversation)
        .filter(Conversation.business_id == business.id)
        .order_by(Conversation.id.desc())
        .limit(20)
        .all()
    )
    return [
        {"id": r.id, "text": r.user_message, "reply": r.assistant_response,
         "intent": r.intent, "ok": r.success, "at": r.created_at}
        for r in rows
    ]
