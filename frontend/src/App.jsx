// src/App.jsx
import React, { useState, useEffect } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import Home from "./pages/Home";
import Landing from "./pages/Landing";
import { observeUser, logout } from "./firebase";
import "./styles/global.css";

export default function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsub = observeUser((u) => {
      setUser(u);
      setLoading(false);
    });
    return () => unsub();
  }, []);

  if (loading)
    return (
      <div
        style={{
          color: "white",
          textAlign: "center",
          marginTop: "40vh",
          fontSize: "1.5rem",
        }}
      >
        Loading...
      </div>
    );

  return (
    <Router>
      <Routes>
        <Route
          path="/"
          element={user ? <Navigate to="/home" /> : <Landing />}
        />
        <Route
          path="/home"
          element={
            user ? <Home user={user} onLogout={logout} /> : <Navigate to="/" />
          }
        />
      </Routes>
    </Router>
  );
}
