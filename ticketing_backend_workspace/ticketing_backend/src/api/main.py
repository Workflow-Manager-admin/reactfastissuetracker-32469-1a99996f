from fastapi import FastAPI, HTTPException, Path, Body, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from uuid import uuid4
from datetime import datetime

from sqlalchemy import (
    create_engine,
    Column,
    String,
    Enum as SAEnum,
    DateTime,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, scoped_session


# --- Ticket data model definitions ---


class TicketStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    closed = "closed"


# SQLAlchemy setup (SQLite DB)
DATABASE_URL = "sqlite:///./tickets.db"

Base = declarative_base()


class TicketORM(Base):
    __tablename__ = "tickets"
    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(SAEnum(TicketStatus), nullable=False, default=TicketStatus.open)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    response = Column(Text, nullable=True)


# DB engine + session
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))


def create_db_and_tables():
    """Create tables if they do not exist (automatic migration for this use-case)."""
    Base.metadata.create_all(bind=engine)


# Dependency for getting DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# PUBLIC_INTERFACE
class Ticket(BaseModel):
    """
    Represents a support ticket.
    """

    id: str = Field(
        ...,
        description="Unique ticket identifier"
    )
    title: str = Field(
        ...,
        description="Short title describing the issue"
    )
    description: str = Field(
        ...,
        description="Detailed description of the issue or request"
    )
    status: TicketStatus = Field(
        ...,
        description="Current status of the ticket"
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp of ticket creation"
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp of last ticket update"
    )
    response: Optional[str] = Field(
        None,
        description="Optional admin/internal response to the ticket"
    )

    @staticmethod
    def from_orm_obj(obj: 'TicketORM'):
        return Ticket(
            id=obj.id,
            title=obj.title,
            description=obj.description,
            status=obj.status,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            response=obj.response
        )


# PUBLIC_INTERFACE
class NewTicketRequest(BaseModel):
    """
    Payload for submitting a new ticket.
    """

    title: str = Field(
        ...,
        description="Short title describing the issue"
    )
    description: str = Field(
        ...,
        description="Detailed description of the issue or request"
    )


# PUBLIC_INTERFACE
class TicketStatusUpdateRequest(BaseModel):
    """
    Payload for updating a ticket's status.
    """

    status: TicketStatus = Field(
        ...,
        description="New status for the ticket"
    )
    response: Optional[str] = Field(
        None,
        description="Optional response or comment from admin"
    )


# PUBLIC_INTERFACE
class TicketListResponse(BaseModel):
    tickets: List[Ticket] = Field(
        ...,
        description="List of tickets"
    )


# ----------------- FastAPI App Setup -----------------

app = FastAPI(
    title="Anonymous Ticketing System Backend",
    version="1.0.0",
    description=(
        "RESTful backend for anonymous ticket submission, listing, status "
        "management, and admin overview.\n"
        "No authentication required. Data is persistent (SQLite via SQLAlchemy).\n"
    ),
    openapi_tags=[
        {
            "name": "public",
            "description": "Anonymous ticket submission and public ticket listing"
        },
        {
            "name": "admin",
            "description": (
                "Ticket status updates and dashboard (no authentication required)"
            )
        },
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Run the function at startup
@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# ----------- Public Endpoints (No Auth) -----------


@app.get("/", summary="Health check", tags=["public"])
def health_check():
    """Service health check endpoint (anonymous)"""
    return {"message": "Healthy"}


# PUBLIC_INTERFACE
@app.post(
    "/tickets",
    status_code=status.HTTP_201_CREATED,
    response_model=Ticket,
    summary="Submit a new ticket",
    tags=["public"],
    description=(
        "Allows anyone to submit a new support/issue ticket. "
        "Returns created ticket details."
    ),
)
def submit_ticket(payload: NewTicketRequest, db: Session = Depends(get_db)):
    """
    Submit a new ticket.

    - **title**: short description for the ticket
    - **description**: details of the issue or request

    Returns the created ticket object.
    """
    ticket_id = str(uuid4())
    now = datetime.utcnow()
    ticket_obj = TicketORM(
        id=ticket_id,
        title=payload.title,
        description=payload.description,
        status=TicketStatus.open,
        created_at=now,
        updated_at=now,
        response=None,
    )
    db.add(ticket_obj)
    db.commit()
    db.refresh(ticket_obj)
    return Ticket.from_orm_obj(ticket_obj)


# PUBLIC_INTERFACE
@app.get(
    "/tickets",
    response_model=TicketListResponse,
    summary="List all tickets",
    tags=["public"],
    description="Returns a list of all tickets (no authentication)."
)
def list_tickets(db: Session = Depends(get_db)):
    """
    List all tickets.

    Returns a list of all tickets currently in the system.
    """
    q = db.query(TicketORM).order_by(TicketORM.created_at.desc()).all()
    return TicketListResponse(tickets=[Ticket.from_orm_obj(x) for x in q])


# PUBLIC_INTERFACE
@app.get(
    "/tickets/{ticket_id}",
    response_model=Ticket,
    summary="Get a single ticket by ID",
    tags=["public"],
    description="Retrieve ticket details for a specific ticket ID."
)
def get_ticket(ticket_id: str = Path(..., description="Ticket ID"), db: Session = Depends(get_db)):
    """
    Get a single ticket by its ID.
    """
    ticket = db.query(TicketORM).filter(TicketORM.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return Ticket.from_orm_obj(ticket)


# ----------- Admin Functionality (No Auth) -----------


# PUBLIC_INTERFACE
@app.patch(
    "/tickets/{ticket_id}/status",
    response_model=Ticket,
    summary="Update ticket status",
    tags=["admin"],
    description=(
        "Update the status (and optionally response) of a ticket (no authentication)."
    ),
)
def update_ticket_status(
    ticket_id: str = Path(..., description="Ticket ID"),
    payload: TicketStatusUpdateRequest = Body(...),
    db: Session = Depends(get_db),
):
    """
    Update ticket status and/or admin response.

    - **status**: open, in_progress, or closed
    - **response**: optional message/comment

    Returns the updated ticket object.
    """
    ticket = db.query(TicketORM).filter(TicketORM.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    ticket.status = payload.status
    ticket.updated_at = datetime.utcnow()
    if payload.response is not None:
        ticket.response = payload.response
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return Ticket.from_orm_obj(ticket)


# PUBLIC_INTERFACE
@app.get(
    "/admin/dashboard",
    response_model=TicketListResponse,
    summary="Admin dashboard - list all tickets",
    tags=["admin"],
    description=(
        "Basic admin dashboard endpoint that lists all tickets "
        "(no authentication required)."
    ),
)
def admin_dashboard(db: Session = Depends(get_db)):
    """
    Admin dashboard listing all tickets.
    """
    q = db.query(TicketORM).order_by(TicketORM.created_at.desc()).all()
    return TicketListResponse(tickets=[Ticket.from_orm_obj(x) for x in q])


# ---------------- OpenAPI Documentation Note (WebSocket info not required here) ----------------
