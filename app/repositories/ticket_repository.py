from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate, TicketUpdate


def create_ticket(db: Session, ticket_data: TicketCreate, suggested_solution: Optional[str] = None) -> Ticket:
    db_ticket = Ticket(
        **ticket_data.model_dump(),
        suggested_solution=suggested_solution,
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


def get_ticket_by_id(db: Session, ticket_id: int) -> Optional[Ticket]:
    return db.query(Ticket).filter(Ticket.id == ticket_id).first()


def get_tickets(db: Session, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[Ticket]:
    query = db.query(Ticket)
    if status:
        query = query.filter(Ticket.status == status)
    return query.offset(skip).limit(limit).all()


def update_ticket(db: Session, db_ticket: Ticket, update_data: TicketUpdate) -> Ticket:
    data = update_data.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(db_ticket, key, value)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


def delete_ticket(db: Session, db_ticket: Ticket) -> None:
    db.delete(db_ticket)
    db.commit()
