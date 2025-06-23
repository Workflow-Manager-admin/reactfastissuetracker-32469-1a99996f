import React, { useState } from "react";
import { submitTicket } from "./api";

/**
 * TicketForm - Form for submitting new tickets.
 * @param {Object} props
 * @param {Function} props.onTicketCreated Function to call after successful ticket creation.
 */
function TicketForm({ onTicketCreated }) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // PUBLIC_INTERFACE
  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    if (!title.trim() || !description.trim()) {
      setError("Please fill in both title and description.");
      return;
    }
    setLoading(true);
    try {
      await submitTicket({ title, description });
      setTitle("");
      setDescription("");
      if (onTicketCreated) onTicketCreated();
    } catch (err) {
      setError("Failed to submit ticket.");
    }
    setLoading(false);
  }

  return (
    <form className="ticket-form" onSubmit={handleSubmit}>
      <h2>Submit a Ticket</h2>
      {error && <div className="ticket-form-error">{error}</div>}
      <div className="ticket-form-group">
        <label>Title</label>
        <input
          type="text"
          value={title}
          onChange={e => setTitle(e.target.value)}
          maxLength={80}
          placeholder="Short summary"
        />
      </div>
      <div className="ticket-form-group">
        <label>Description</label>
        <textarea
          value={description}
          onChange={e => setDescription(e.target.value)}
          rows={4}
          maxLength={500}
          placeholder="Describe the issue or request..."
        />
      </div>
      <button className="btn btn-large" type="submit" disabled={loading}>
        {loading ? "Submitting..." : "Submit Ticket"}
      </button>
    </form>
  );
}

export default TicketForm;
