from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


class TicketBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=150)
    description: str = Field(..., min_length=5)
    category: str = Field(default="Geral", max_length=50)
    priority: Literal["low", "medium", "high", "critical"] = "medium"


class TicketCreate(TicketBase):
    pass


class TicketUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=150)
    description: Optional[str] = Field(None, min_length=5)
    category: Optional[str] = Field(None, max_length=50)
    priority: Optional[Literal["low", "medium", "high", "critical"]] = None
    status: Optional[Literal["open", "in_progress", "resolved", "closed"]] = None


class TicketResponse(TicketBase):
    id: int
    status: str
    suggested_solution: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
