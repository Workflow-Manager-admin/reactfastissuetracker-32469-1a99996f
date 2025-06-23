import React, { useState, useEffect } from "react";
import { fetchAdminTickets, updateTicketStatus } from "./api";

/**
 * AdminDashboard - Lists all tickets with ability to update ticket status/response.
 */
function AdminDashboard() {
  const [tickets, setTickets] = useState([]);
  const [selected, setSelected] = useState(null);
  const [response, setResponse] = useState("");
  const [status, setStatus] = useState("");
  const [updateError, setUpdateError] = useState("");
  const [saving, setSaving] = useState(false);
  const [loadError, setLoadError] = useState("");

  // PUBLIC_INTERFACE
  async function load() {
    try {
      setLoadError("");
      setTickets(await fetchAdminTickets());
    } catch (e) {
      setLoadError("Failed to load tickets.");
      setTickets([]);
    }
  }

  useEffect(() => {
    load();
  }, []);

  function prepSelected(ticket) {
    setSelected(ticket);
    setStatus(ticket.status);
    setResponse(ticket.response || "");
  }

  // PUBLIC_INTERFACE
  async function handleUpdateStatus(e) {
    e.preventDefault();
    setSaving(true);
    setUpdateError("");
    try {
      await updateTicketStatus(selected.id, { status, response });
      await load();
      // Refresh selected ticket from latest tickets array
      let updated = (await fetchAdminTickets()).find(t => t.id === selected.id);
      prepSelected(updated || selected);
    } catch (err) {
      setUpdateError("Failed to update ticket.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="admin-dashboard">
      <h2>Admin Dashboard</h2>
      <div className="admin-dashboard-layout">
        <aside className="admin-sidebar">
          <div className="admin-sidebar-header">All Tickets</div>
          <div className="admin-ticket-list">
            {tickets.map(t => (
              <div
                key={t.id}
                className={`admin-ticket-item ${
                  selected && t.id === selected.id ? "active" : ""
                }`}
                onClick={() => prepSelected(t)}
              >
                <span className="ticket-status" data-status={t.status}>
                  {t.status}
                </span>
                <div>
                  <strong>{t.title}</strong>
                  <div className="admin-ticket-date">
                    {new Date(t.created_at).toLocaleString()}
                  </div>
                </div>
              </div>
            ))}
            {tickets.length === 0 && (
              <div className="admin-ticket-empty">No tickets found.</div>
            )}
          </div>
        </aside>
        <main className="admin-main">
          {selected ? (
            <div className="admin-ticket-details">
              <h3>{selected.title}</h3>
              <div>
                <b>Status:</b>{" "}
                <span className="ticket-status" data-status={selected.status}>
                  {selected.status}
                </span>
              </div>
              <div>
                <b>Description:</b>
                <p>{selected.description}</p>
              </div>
              <form onSubmit={handleUpdateStatus} className="admin-status-form">
                <label>Status:</label>
                <select
                  value={status}
                  onChange={e => setStatus(e.target.value)}
                  required
                >
                  <option value="open">Open</option>
                  <option value="in_progress">In Progress</option>
                  <option value="closed">Closed</option>
                </select>
                <label>Admin Response:</label>
                <textarea
                  value={response}
                  onChange={e => setResponse(e.target.value)}
                  placeholder="Write a response or internal note"
                  rows={3}
                />
                {updateError && (
                  <div className="ticket-form-error">{updateError}</div>
                )}
                <button className="btn" type="submit" disabled={saving}>
                  {saving ? "Updating..." : "Update Status"}
                </button>
              </form>
            </div>
          ) : (
            <div className="admin-ticket-placeholder">
              Select a ticket to view and edit its details.
            </div>
          )}
        </main>
      </div>
      {loadError && <div className="ticket-form-error">{loadError}</div>}
    </div>
  );
}

export default AdminDashboard;
