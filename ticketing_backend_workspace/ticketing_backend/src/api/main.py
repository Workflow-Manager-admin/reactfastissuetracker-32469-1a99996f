from fastapi import FastAPI, HTTPException, Path, Body, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum
from uuid import uuid4
from datetime import datetime


# --- Ticket data model definitions ---


class TicketStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    closed = "closed"


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


# ----------------- In-memory store -----------------
tickets_db: Dict[str, Ticket] = {}


# ----------------- FastAPI App Setup -----------------
app = FastAPI(
    title="Anonymous Ticketing System Backend",
    version="1.0.0",
    description=(
        "RESTful backend for anonymous ticket submission, listing, status "
        "management, and admin overview.\n"
        "No authentication required. Data is not persistent (in-memory only).\n"
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
def submit_ticket(payload: NewTicketRequest):
    """
    Submit a new ticket.

    - **title**: short description for the ticket
    - **description**: details of the issue or request

    Returns the created ticket object.
    """
    ticket_id = str(uuid4())
    now = datetime.utcnow()
    ticket = Ticket(
        id=ticket_id,
        title=payload.title,
        description=payload.description,
        status=TicketStatus.open,
        created_at=now,
        updated_at=now,
        response=None,
    )
    tickets_db[ticket_id] = ticket
    return ticket


# PUBLIC_INTERFACE
@app.get(
    "/tickets",
    response_model=TicketListResponse,
    summary="List all tickets",
    tags=["public"],
    description="Returns a list of all tickets (no authentication)."
)
def list_tickets():
    """
    List all tickets.

    Returns a list of all tickets currently in the system.
    """
    return TicketListResponse(tickets=list(tickets_db.values()))


# PUBLIC_INTERFACE
@app.get(
    "/tickets/{ticket_id}",
    response_model=Ticket,
    summary="Get a single ticket by ID",
    tags=["public"],
    description="Retrieve ticket details for a specific ticket ID."
)
def get_ticket(ticket_id: str = Path(..., description="Ticket ID")):
    """
    Get a single ticket by its ID.
    """
    ticket = tickets_db.get(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


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
):
    """
    Update ticket status and/or admin response.

    - **status**: open, in_progress, or closed
    - **response**: optional message/comment

    Returns the updated ticket object.
    """
    ticket = tickets_db.get(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    ticket.status = payload.status
    ticket.updated_at = datetime.utcnow()
    if payload.response:
        ticket.response = payload.response
    tickets_db[ticket_id] = ticket
    return ticket


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
def admin_dashboard():
    """
    Admin dashboard listing all tickets.
    """
    # Same as public listing but included here for future admin features/extensions.
    return TicketListResponse(tickets=list(tickets_db.values()))


# ---------------- OpenAPI Documentation Note (WebSocket info not required here) ----------------
