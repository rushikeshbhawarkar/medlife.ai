import { useState, useEffect } from 'react';
import Logo from '../../components/Logo/index.js';
import Button from '../../components/Button/index.js';
import Banner from '../../components/Banner/index.js';
import Spinner from '../../components/Spinner/index.js';
import { activateDoctorAccount } from '../../services/api.js';
import { Stethoscope, CheckCircle2, ShieldAlert, KeyRound, Eye, EyeOff } from 'lucide-react';
import './doctor.css';

function readActivationToken() {
  const hash = window.location.hash || '';
  const search = new URLSearchParams(window.location.search);

  // 1. Direct query parameter ?token=...
  const queryToken = search.get('token');
  if (queryToken) return queryToken;

  // 2. Direct regex match on token= in hash
  const hashToken = hash.match(/(?:^#|&|\?|#\/doctor-activate#)token=([^&]*)/);
  if (hashToken) {
    try {
      return decodeURIComponent(hashToken[1]);
    } catch {
      return hashToken[1];
    }
  }

  // 3. Fallback: split on #token= in decoded hash
  try {
    const decoded = decodeURIComponent(hash);
    const marker = '#token=';
    const idx = decoded.lastIndexOf(marker);
    if (idx !== -1) {
      return decoded.slice(idx + marker.length).split('&')[0];
    }
    const paramMarker = 'token=';
    const paramIdx = decoded.indexOf(paramMarker);
    if (paramIdx !== -1) {
      return decoded.slice(paramIdx + paramMarker.length).split('&')[0];
    }
  } catch {}

  return '';
}

export default function DoctorActivationPage({ onReturnToSignIn }) {
  const [token, setToken] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    const parsed = readActivationToken();
    setToken(parsed);
    if (!parsed) {
      setError('Activation link is missing a valid token. Please check the link sent to your email or contact MedLife support.');
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMessage('');

    if (!token) {
      setError('This activation link is invalid or missing a security token.');
      return;
    }

    if (password.length < 8 || password.length > 128) {
      setError('Password must be between 8 and 128 characters in length.');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match. Please ensure both fields are identical.');
      return;
    }

    setSubmitting(true);
    try {
      const res = await activateDoctorAccount({
        token,
        password,
        confirm_password: confirmPassword,
      });

      setSuccessMessage(
        res.message || 'Doctor account activated successfully. You can now sign in with your email and password.'
      );
      setPassword('');
      setConfirmPassword('');

      // Strip token from browser address bar for security
      try {
        window.history.replaceState(null, '', window.location.pathname + '#/doctor-activate');
      } catch {}
    } catch (err) {
      setError(err.message || 'Unable to activate doctor account. The link may have expired or already been used.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleGoToSignIn = () => {
    try {
      window.history.replaceState(null, '', '/#/signin');
    } catch {}
    window.location.hash = '#/signin';
    if (onReturnToSignIn) {
      onReturnToSignIn();
    }
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        background: 'var(--bg-primary)',
        color: 'var(--text-primary)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '2rem 1rem',
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: '520px',
          background: 'var(--bg-card)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '16px',
          padding: '2.5rem 2rem',
          boxShadow: 'var(--shadow-lg)',
          display: 'flex',
          flexDirection: 'column',
          gap: '1.5rem',
        }}
      >
        <div style={{ textAlign: 'center' }}>
          <Logo toHome={false} />
          <h2 style={{ marginTop: '1.25rem', color: 'var(--text-primary)', fontSize: '1.4rem', fontWeight: 700 }}>
            Doctor Account Activation
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: '0.35rem 0 0 0' }}>
            Set your secure password to complete your practitioner registration
          </p>
        </div>

        {error && <Banner variant="error">{error}</Banner>}

        {successMessage ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', textAlign: 'center', alignItems: 'center' }}>
            <div
              style={{
                width: '56px',
                height: '56px',
                borderRadius: '50%',
                background: 'rgba(16, 185, 129, 0.12)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--emerald, #10b981)',
              }}
            >
              <CheckCircle2 size={32} />
            </div>

            <div style={{ fontSize: '0.95rem', color: 'var(--text-primary)', lineHeight: '1.5' }}>
              {successMessage}
            </div>

            <Button
              type="button"
              variant="primary"
              size="lg"
              block
              onClick={handleGoToSignIn}
            >
              Sign In to MedLife
            </Button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div className="doctor-form-group">
              <label htmlFor="doc-new-password">New Password *</label>
              <div style={{ position: 'relative' }}>
                <input
                  id="doc-new-password"
                  type={showPassword ? 'text' : 'password'}
                  className="doctor-form-input"
                  style={{ paddingRight: '2.5rem' }}
                  placeholder="At least 8 characters"
                  required
                  minLength={8}
                  maxLength={128}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={submitting || !token}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{
                    position: 'absolute',
                    right: '10px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    background: 'none',
                    border: 'none',
                    color: 'var(--text-muted)',
                    cursor: 'pointer',
                    padding: '4px',
                    display: 'flex',
                  }}
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              <small style={{ color: 'var(--text-muted)' }}>Must be between 8 and 128 characters</small>
            </div>

            <div className="doctor-form-group">
              <label htmlFor="doc-confirm-password">Confirm Password *</label>
              <input
                id="doc-confirm-password"
                type={showPassword ? 'text' : 'password'}
                className="doctor-form-input"
                placeholder="Re-enter your new password"
                required
                minLength={8}
                maxLength={128}
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                disabled={submitting || !token}
              />
            </div>

            <div
              style={{
                background: 'var(--bg-secondary)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '8px',
                padding: '0.75rem 1rem',
                fontSize: '0.8rem',
                color: 'var(--text-secondary)',
                display: 'flex',
                gap: '0.5rem',
                alignItems: 'center',
              }}
            >
              <KeyRound size={16} color="var(--red-primary)" style={{ flexShrink: 0 }} />
              <span>This activation link is single-use and will be permanently invalidated once your password is set.</span>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              block
              disabled={submitting || !token || !password || !confirmPassword}
            >
              {submitting ? 'Activating Account...' : 'Set Password & Activate Account'}
            </Button>
          </form>
        )}
      </div>
    </div>
  );
}
