from typing import Any
from pydantic import BaseModel, Field


class CommandRequest(BaseModel):
    text: str = Field(min_length=1, max_length=500)


class CommandResponse(BaseModel):
    ok: bool
    intent: str
    message: str
    # What changed, so the UI knows which pages to refresh and can show details.
    data: dict[str, Any] | None = None
    warning: str | None = None
