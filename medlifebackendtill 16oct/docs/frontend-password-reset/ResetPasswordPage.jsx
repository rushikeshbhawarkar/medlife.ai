// Drop-in page for the route that FRONTEND_PASSWORD_RESET_URL points to (e.g. /reset-password).
// React Router example:  <Route path="/reset-password" element={<ResetPasswordPage />} />
// The email link looks like  https://your-site/reset-password#token=XXXX  (token is in the URL fragment,
// so it is never sent to any server or written to access logs). The page moves it into memory and removes it
// from the address bar. Change "/login" below to your login route.
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

const API_BASE = import.meta.env.VITE_API_BASE; // e.g. http://127.0.0.1:8000/medlife

export default function ResetPasswordPage() {
  const [token, setToken] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [done, setDone] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const t = new URLSearchParams(window.location.hash.replace(/^#/, "")).get("token") || "";
    setToken(t);
    if (t) window.history.replaceState(null, "", window.location.pathname); // hide token from the address bar
  }, []);

  async function submit(e) {
    e.preventDefault();
    setError("");
    if (newPassword.length < 6) return setError("Password must be at least 6 characters.");
    if (newPassword !== confirmPassword) return setError("Passwords do not match.");
    setBusy(true);
    try {
      const res = await fetch(`${API_BASE}/password/reset`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, new_password: newPassword, confirm_password: confirmPassword }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.detail || "Could not reset the password.");
      setDone(data.detail);
      setNewPassword("");
      setConfirmPassword("");
      setToken("");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  if (done) {
    return (
      <div>
        <h2>Password changed</h2>
        <p>{done}</p>
        <Link to="/login">Go to login</Link>
      </div>
    );
  }
  if (!token) {
    return (
      <div>
        <h2>Reset link missing or already used</h2>
        <p>Please request a new link from the login page using "Forgot Password?".</p>
        <Link to="/login">Back to login</Link>
      </div>
    );
  }
  return (
    <form onSubmit={submit}>
      <h2>Reset your password</h2>
      <label>Enter New Password
        <input type="password" required minLength={6} autoComplete="new-password"
               value={newPassword} onChange={(e) => setNewPassword(e.target.value)} />
      </label>
      <label>Confirm New Password
        <input type="password" required minLength={6} autoComplete="new-password"
               value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} />
      </label>
      {error && <p role="alert">{error}</p>}
      <button type="submit" disabled={busy}>{busy ? "Saving..." : "Reset Password"}</button>
    </form>
  );
}
