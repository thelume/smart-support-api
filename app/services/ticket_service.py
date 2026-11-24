from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate, TicketUpdate
from app.repositories import ticket_repository
from app.services import rag_service


def open_ticket(db: Session, ticket_data: TicketCreate) -> Ticket:
    suggested_solution = rag_service.generate_suggested_solution(
        db=db,
        title=ticket_data.title,
        description=ticket_data.description,
    )
    return ticket_repository.create_ticket(
        db=db,
        ticket_data=ticket_data,
        suggested_solution=suggested_solution,
    )


def list_tickets(db: Session, skip: int = 0, limit: int = 100, status_filter: Optional[str] = None) -> List[Ticket]:
    return ticket_repository.get_tickets(db, skip=skip, limit=limit, status=status_filter)


def get_ticket(db: Session, ticket_id: int) -> Ticket:
    ticket = ticket_repository.get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket com ID {ticket_id} não encontrado.",
        )
    return ticket


def modify_ticket(db: Session, ticket_id: int, update_data: TicketUpdate) -> Ticket:
    db_ticket = get_ticket(db, ticket_id)
    return ticket_repository.update_ticket(db, db_ticket, update_data)


def remove_ticket(db: Session, ticket_id: int) -> None:
    db_ticket = get_ticket(db, ticket_id)
    ticket_repository.delete_ticket(db, db_ticket)
