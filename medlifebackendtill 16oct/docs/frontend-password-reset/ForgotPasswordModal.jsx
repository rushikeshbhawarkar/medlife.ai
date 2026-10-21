// Drop-in for your existing React (Vite) login screen. Style it with your own CSS classes.
// Usage inside the login page:
//   const [showForgot, setShowForgot] = useState(false);
//   <button type="button" onClick={() => setShowForgot(true)}>Forgot Password?</button>
//   {showForgot && <ForgotPasswordModal onClose={() => setShowForgot(false)} />}
import { useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE; // e.g. http://127.0.0.1:8000/medlife

export default function ForgotPasswordModal({ onClose }) {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setError("");
    setMessage("");
    if (!/^\S+@\S+\.\S+$/.test(email.trim())) {
      setError("Enter a valid email address.");
      return;
    }
    setBusy(true);
    try {
      const res = await fetch(`${API_BASE}/password/forgot`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim() }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.detail || "Something went wrong. Please try again.");
      setMessage(data.detail); // same text whether or not the email is registered
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div role="dialog" aria-modal="true" aria-label="Forgot password">
      <form onSubmit={submit}>
        <h2>Forgot Password?</h2>
        <p>Enter your registered email address and we will send you a reset link.</p>
        <input type="email" required autoComplete="email" value={email}
               onChange={(e) => setEmail(e.target.value)} placeholder="Email address" />
        {error && <p role="alert">{error}</p>}
        {message && <p role="status">{message}</p>}
        <button type="submit" disabled={busy}>{busy ? "Sending..." : "Send reset link"}</button>
        <button type="button" onClick={onClose}>Close</button>
      </form>
    </div>
  );
}
