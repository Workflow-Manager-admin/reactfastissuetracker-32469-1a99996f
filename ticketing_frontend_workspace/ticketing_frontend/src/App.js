import React, { useState } from "react";
import "./App.css";
import TicketForm from "./TicketForm";
import TicketList from "./TicketList";
import AdminDashboard from "./AdminDashboard";

const BRAND = {
  logo: (
    <>
      <span className="logo-symbol" style={{ color: "#ff9800" }}>
        *
      </span>
      <span>KAVIA Ticketing</span>
    </>
  ),
  version: "v1.0",
};

function App() {
  // Allow toggling between "User" and "Admin" mode
  const [isAdmin, setIsAdmin] = useState(false);
  const [reload, setReload] = useState(0);

  return (
    <div className="app ticketing-app">
      <nav className="navbar">
        <div className="container">
          <div style={{ display: "flex", alignItems: "center", width: "100%", justifyContent: "space-between" }}>
            <div className="logo">{BRAND.logo}</div>
            <div>
              <button
                className="btn"
                onClick={() => setIsAdmin((prev) => !prev)}
                style={{ marginRight: 8, background: isAdmin ? "#ff9800" : "#1d72b8" }}
              >
                {isAdmin ? "Switch to User" : "Go to Admin"}
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main>
        <div className="container" style={{ paddingTop: 96 }}>
          {!isAdmin ? (
            <>
              <div className="ticketing-user-view">
                <TicketForm onTicketCreated={() => setReload((c) => c + 1)} />
                <TicketList key={reload} />
              </div>
            </>
          ) : (
            <AdminDashboard />
          )}
        </div>
      </main>
      <footer className="footer">
        <div className="container">
          <span className="footer-brand">
            &copy; {new Date().getFullYear()} Kavia. Anonymous Ticketing System.
          </span>
        </div>
      </footer>
    </div>
  );
}

export default App;