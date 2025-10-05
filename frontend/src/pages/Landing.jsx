import React, { useEffect } from "react";
import { motion } from "framer-motion";
import { loginWithGoogle, observeUser } from "../firebase";
import { useNavigate } from "react-router-dom";

export default function Landing() {
  const navigate = useNavigate();

  useEffect(() => {
    const unsub = observeUser((user) => {
      if (user) navigate("/home");
    });
    return () => unsub();
  }, [navigate]);

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        background: "linear-gradient(180deg, #0B0E14 0%, #0F1623 100%)",
        color: "#fff",
        fontFamily: "Inter, sans-serif",
        overflow: "hidden",
      }}
    >
      {/* Floating blobs background */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 0.2, scale: [1, 1.2, 1] }}
        transition={{ duration: 8, repeat: Infinity }}
        style={{
          position: "absolute",
          width: 400,
          height: 400,
          borderRadius: "50%",
          background: "rgba(0, 102, 255, 0.4)",
          filter: "blur(120px)",
          top: "20%",
          left: "15%",
          zIndex: 0,
        }}
      ></motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 0.15, scale: [1, 1.3, 1] }}
        transition={{ duration: 10, repeat: Infinity }}
        style={{
          position: "absolute",
          width: 450,
          height: 450,
          borderRadius: "50%",
          background: "rgba(0, 170, 255, 0.25)",
          filter: "blur(140px)",
          bottom: "15%",
          right: "10%",
          zIndex: 0,
        }}
      ></motion.div>

      {/* Main Content */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1 }}
        style={{
          textAlign: "center",
          zIndex: 2,
          padding: "0 20px",
        }}
      >
        <motion.h1
          initial={{ scale: 0.9 }}
          animate={{ scale: 1 }}
          transition={{ duration: 1 }}
          style={{
            fontSize: "3rem",
            fontWeight: "700",
            color: "#FFFFFF",
            marginBottom: "0.5rem",
            letterSpacing: "0.5px",
          }}
        >
          🩺 ClariMed
        </motion.h1>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5, duration: 1 }}
          style={{
            fontSize: "1.2rem",
            color: "#C7D0E0",
            marginBottom: "2rem",
          }}
        >
          Making medical documents clear, simple, and actionable.
        </motion.p>

        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={loginWithGoogle}
          style={{
            background: "linear-gradient(90deg, #1E90FF 0%, #007BFF 100%)",
            border: "none",
            color: "white",
            padding: "14px 38px",
            borderRadius: "12px",
            fontSize: "1.1rem",
            fontWeight: "600",
            cursor: "pointer",
            boxShadow: "0 0 20px rgba(30,144,255,0.4)",
          }}
        >
          Continue with Google
        </motion.button>
      </motion.div>

      {/* Footer text */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 0.6 }}
        transition={{ delay: 1.5, duration: 1 }}
        style={{
          position: "absolute",
          bottom: "20px",
          fontSize: "0.9rem",
          color: "#8FA3BF",
          zIndex: 2,
        }}
      >
        © 2025 ClariMed — Empowering Clarity in Healthcare
      </motion.div>
    </div>
  );
}
