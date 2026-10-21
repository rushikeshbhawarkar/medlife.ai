import { useState } from 'react';
import { resetPassword } from '../../services/api.js';

export default function ResetPasswordPage({ onReturnToSignIn }) {
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);

  // The backend appends #token=... to the configured frontend URL.
  // With the hash router, the resulting URL is:
  // /#/reset-password#token=...
  // function readResetToken() {
  //   const hash = window.location.hash;
  //   const marker = '#token=';
  //   const index = hash.lastIndexOf(marker);

  //   if (index === -1) return '';

  //   try {
  //     return decodeURIComponent(hash.slice(index + marker.length).split('&')[0]);
  //   } catch {
  //     return '';
  //   }
  // }









function readResetToken() {
  const hash = window.location.hash;
  const search = new URLSearchParams(window.location.search);

  // 1. Support a normal query parameter: ?token=...
  const queryToken = search.get('token');
  if (queryToken) {
    return queryToken;
  }

  // 2. Support a normal hash token: #token=...
  const hashToken = hash.match(/(?:^#|&)token=([^&]*)/);

  if (hashToken) {
    try {
      return decodeURIComponent(hashToken[1]);
    } catch {
      return hashToken[1];
    }
  }

  // 3. Support the encoded format:
  // #/reset-password%23token=...
  let decodedHash;

  try {
    decodedHash = decodeURIComponent(hash);
  } catch {
    decodedHash = hash;
  }

  const marker = '#token=';
  const index = decodedHash.lastIndexOf(marker);

  if (index !== -1) {
    const token = decodedHash
      .slice(index + marker.length)
      .split('&')[0];

    return token;
  }

  // 4. Support a token after ? or & in the fragment.
  const fragmentQuery = decodedHash.match(/[?&]token=([^&]*)/);

  if (fragmentQuery) {
    try {
      return decodeURIComponent(fragmentQuery[1]);
    } catch {
      return fragmentQuery[1];
    }
  }

  // No token found.
  return '';
}










  

  async function submit(e) {
    e.preventDefault();
    setError('');
    setMessage('');

    const token = readResetToken();

    if (!token) {
      setError('The reset link is missing or invalid. Please request a new link.');
      return;
    }

    if (newPassword.length < 6) {
      setError('Password must contain at least 6 characters.');
      return;
    }

    if (newPassword !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setBusy(true);

    try {
      const result = await resetPassword(token, newPassword, confirmPassword);
      setMessage(
        result.detail || 'Password changed successfully. Please sign in again.'
      );
      setNewPassword('');
      setConfirmPassword('');

      // Remove the reset token from the address bar after success.
      window.history.replaceState(
        null,
        '',
        window.location.pathname + window.location.search + '#/reset-password'
      );
    } catch (err) {
      setError(err.message || 'Unable to reset your password.');
    } finally {
      setBusy(false);
    }
  }

  function handleReturn() {
    try {
      window.history.replaceState(null, '', '/#/signin');
    } catch {}
    window.location.hash = '#/signin';
    if (onReturnToSignIn) {
      onReturnToSignIn();
    }
  }

  return (
    <main className="reset-page">
      <h1>Reset your password</h1>
      <p>Enter your new password below and confirm it.</p>

      {message ? (
        <>
          <p role="status" className="reset-success">{message}</p>
          <button
            type="button"
            className="btn btn-primary"
            onClick={handleReturn}
          >
            Return to MedLife
          </button>
        </>
      ) : (
        <form onSubmit={submit}>
          <label htmlFor="new-password">New password</label>
          <input
            id="new-password"
            type="password"
            autoComplete="new-password"
            minLength={6}
            required
            value={newPassword}
            onChange={e => setNewPassword(e.target.value)}
            className="reset-input"
          />

          <label htmlFor="confirm-password">Confirm new password</label>
          <input
            id="confirm-password"
            type="password"
            autoComplete="new-password"
            minLength={6}
            required
            value={confirmPassword}
            onChange={e => setConfirmPassword(e.target.value)}
            className="reset-input"
          />

          {error && <p role="alert" className="reset-error">{error}</p>}

          <button type="submit" disabled={busy} className="btn btn-primary btn-lg btn-block">
            {busy ? 'Changing password…' : 'Change password'}
          </button>
        </form>
      )}
    </main>
  );
}