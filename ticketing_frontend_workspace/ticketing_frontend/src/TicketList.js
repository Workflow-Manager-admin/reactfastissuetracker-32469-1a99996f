import React, { useState, useEffect } from "react";
import { fetchTickets, fetchTicket } from "./api";

/**
 * TicketList - Lists tickets for regular users (no editing).
 */
function TicketList() {
  const [tickets, setTickets] = useState([]);
  const [selected, setSelected] = useState(null);
  const [details, setDetails] = useState(null);
  const [loading, setLoading] = useState(false);

  // PUBLIC_INTERFACE
  async function loadTickets() {
    setLoading(true);
    try {
      setTickets(await fetchTickets());
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadTickets();
  }, []);

  // PUBLIC_INTERFACE
  async function selectTicket(ticket) {
    setSelected(ticket.id);
    setDetails(null);
    try {
      setDetails(await fetchTicket(ticket.id));
    } catch (_) {
      setDetails(null);
    }
  }

  return (
    <div className="ticket-list-section">
      <h2>Open Tickets</h2>
      {loading && <div>Loading tickets...</div>}
      <div className="ticket-list">
        {tickets.length === 0 && !loading && (
          <div className="ticket-empty">No tickets found.</div>
        )}
        {tickets.map(ticket => (
          <div
            key={ticket.id}
            className={`ticket-list-item ${
              selected === ticket.id ? "active" : ""
            }`}
            onClick={() => selectTicket(ticket)}
            style={{ cursor: "pointer" }}
          >
            <div>
              <span className="ticket-status" data-status={ticket.status}>
                {ticket.status}
              </span>
              <strong>{ticket.title}</strong>
            </div>
            <div className="ticket-date">
              {new Date(ticket.created_at).toLocaleString()}
            </div>
          </div>
        ))}
      </div>

      {details && (
        <div className="ticket-details">
          <h3>{details.title}</h3>
          <p>{details.description}</p>
          <div className="ticket-details-status">
            Status: <b>{details.status}</b>
            {details.response && (
              <div>
                <span className="ticket-details-response">
                  Admin: {details.response}
                </span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default TicketList;
