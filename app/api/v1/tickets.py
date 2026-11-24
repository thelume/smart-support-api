from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.ticket import TicketCreate, TicketUpdate, TicketResponse
from app.services import ticket_service

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_support_ticket(ticket: TicketCreate, db: Session = Depends(get_db)):
    return ticket_service.open_ticket(db=db, ticket_data=ticket)


@router.get("/", response_model=List[TicketResponse])
def read_support_tickets(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return ticket_service.list_tickets(db=db, skip=skip, limit=limit, status_filter=status)


@router.get("/{ticket_id}", response_model=TicketResponse)
def read_support_ticket(ticket_id: int, db: Session = Depends(get_db)):
    return ticket_service.get_ticket(db=db, ticket_id=ticket_id)


@router.patch("/{ticket_id}", response_model=TicketResponse)
def update_support_ticket(ticket_id: int, ticket_update: TicketUpdate, db: Session = Depends(get_db)):
    return ticket_service.modify_ticket(db=db, ticket_id=ticket_id, update_data=ticket_update)


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_support_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket_service.remove_ticket(db=db, ticket_id=ticket_id)
