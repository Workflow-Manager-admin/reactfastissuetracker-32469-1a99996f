import axios from "axios";

/**
 * Base API client for the ticketing system backend.
 * Adjust the baseURL to match your backend server URL/port if needed.
 */
const api = axios.create({
  baseURL: "https://vscode-internal-620-qa.qa01.cloud.kavia.ai:3001",
  headers: {
    "Content-Type": "application/json",
  },
});

// PUBLIC_INTERFACE
export async function submitTicket({ title, description }) {
  /**
   * Submits a new ticket to the backend.
   * @param {object} param0 { title: string, description: string }
   * @returns {Promise<object>} The created ticket.
   */
  const resp = await api.post("/tickets", { title, description });
  return resp.data;
}

// PUBLIC_INTERFACE
export async function fetchTickets() {
  /**
   * Fetches all tickets (user view).
   * @returns {Promise<object[]>} Array of ticket objects.
   */
  const resp = await api.get("/tickets");
  return resp.data.tickets;
}

// PUBLIC_INTERFACE
export async function fetchTicket(ticketId) {
  /**
   * Fetches details for a single ticket by its ID.
   * @param {string} ticketId
   * @returns {Promise<object>} Ticket object.
   */
  const resp = await api.get(`/tickets/${ticketId}`);
  return resp.data;
}

// PUBLIC_INTERFACE
export async function updateTicketStatus(ticketId, { status, response }) {
  /**
   * Updates the status (and optional response) of a ticket (admin view).
   * @param {string} ticketId
   * @param {object} body { status: 'open'|'in_progress'|'closed', response?: string }
   * @returns {Promise<object>} Updated ticket object.
   */
  const resp = await api.patch(`/tickets/${ticketId}/status`, { status, response });
  return resp.data;
}

// PUBLIC_INTERFACE
export async function fetchAdminTickets() {
  /**
   * Fetches all tickets for the admin dashboard.
   * @returns {Promise<object[]>} Array of ticket objects.
   */
  const resp = await api.get("/admin/dashboard");
  return resp.data.tickets;
}
