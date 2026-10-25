import { useState, useEffect } from 'react';
import Logo from '../../components/Logo/index.js';
import Button from '../../components/Button/index.js';
import Banner from '../../components/Banner/index.js';
import Spinner from '../../components/Spinner/index.js';
import { activateDoctorAccount } from '../../services/api.js';
import { Stethoscope, CheckCircle2, ShieldAlert, KeyRound, Eye, EyeOff, QrCode, ShieldCheck } from 'lucide-react';
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

export default function DoctorActivationPage({ initialToken = '', onReturnToSignIn }) {
  const [stage, setStage] = useState('password'); // 'password' | 'totp' | 'done'
  const [token, setToken] = useState(initialToken);
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  // TOTP stage state from backend
  const [totpQr, setTotpQr] = useState('');
  const [totpEmail, setTotpEmail] = useState('');
  const [totpCode, setTotpCode] = useState('');

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [createdDoctorId, setCreatedDoctorId] = useState('');

  useEffect(() => {
    if (!token) {
      const parsed = readActivationToken();
      if (parsed) {
        setToken(parsed);
      } else {
        setError('Activation link is missing a valid token. Please check the link sent to your email or contact MedLife support.');
      }
    }
  }, [token]);

  // Stage 1: Submit Password Setup
  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    setError('');

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
        action: 'setup',
        password,
        confirm_password: confirmPassword,
      });

      if (res.action === 'verify_totp' && res.token) {
        setToken(res.token); // next_token for Stage 2
        setTotpQr(res.qr_code || '');
        setTotpEmail(res.email || '');
        setStage('totp');
      } else {
        // Fallback if completed in one stage
        setSuccessMessage(res.message || 'Doctor account activated successfully.');
        setCreatedDoctorId(res.doctor_id || '');
        setStage('done');
      }
    } catch (err) {
      setError(err.message || 'Unable to start doctor account activation. The link may have expired or already been used.');
    } finally {
      setSubmitting(false);
    }
  };

  // Stage 2: Submit TOTP Verification Code
  const handleTotpSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const cleanCode = totpCode.trim().replace(/\s+/g, '');
    if (!cleanCode || cleanCode.length < 6) {
      setError('Enter the 6-digit code displayed in your authenticator app.');
      return;
    }

    setSubmitting(true);
    try {
      const res = await activateDoctorAccount({
        token,
        action: 'complete',
        code: cleanCode,
      });

      setSuccessMessage(
        res.message || 'Doctor account created successfully. You can now sign in with your email and password.'
      );
      setCreatedDoctorId(res.doctor_id || '');
      setStage('done');

      // Strip token from browser address bar for security
      try {
        window.history.replaceState(null, '', window.location.pathname + '#/doctor-activate');
      } catch {}
    } catch (err) {
      setError(err.message || 'Invalid or expired authenticator code. Please check your authenticator app and try again.');
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
            {stage === 'password' && 'Set your secure password to initiate doctor registration'}
            {stage === 'totp' && 'Set up two-factor authenticator to complete account creation'}
            {stage === 'done' && 'Your clinical practitioner account is ready'}
          </p>
        </div>

        {error && <Banner variant="error">{error}</Banner>}

        {/* STAGE: SUCCESS / DONE */}
        {stage === 'done' && (
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
              {createdDoctorId && (
                <div style={{ marginTop: '0.5rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                  Doctor ID: <span style={{ color: 'var(--emerald, #10b981)' }}>{createdDoctorId}</span>
                </div>
              )}
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
        )}

        {/* STAGE 1: SET PASSWORD */}
        {stage === 'password' && (
          <form onSubmit={handlePasswordSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
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
              <span>Step 1 of 2: Set your password, then scan the authenticator QR code to complete registration.</span>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              block
              disabled={submitting || !token || !password || !confirmPassword}
            >
              {submitting ? 'Setting Password...' : 'Save Password & Continue to 2FA Setup'}
            </Button>
          </form>
        )}

        {/* STAGE 2: MANDATORY TOTP AUTHENTICATOR ENROLLMENT */}
        {stage === 'totp' && (
          <form onSubmit={handleTotpSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div
              style={{
                background: 'var(--bg-secondary)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '8px',
                padding: '0.85rem 1rem',
                fontSize: '0.85rem',
                color: 'var(--text-secondary)',
                display: 'flex',
                gap: '0.5rem',
                alignItems: 'center',
              }}
            >
              <ShieldCheck size={18} color="var(--emerald, #10b981)" style={{ flexShrink: 0 }} />
              <span>Password saved! Scan the QR code below with your authenticator app (Google Authenticator, Authy, etc.).</span>
            </div>

            {totpQr && (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.75rem', margin: '0.5rem 0' }}>
                <div
                  style={{
                    background: '#fff',
                    padding: '12px',
                    borderRadius: '12px',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                    display: 'inline-flex',
                  }}
                >
                  <img
                    src={totpQr}
                    alt="Authenticator QR Code"
                    style={{ width: '180px', height: '180px', display: 'block' }}
                  />
                </div>
                {totpEmail && (
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    Account: {totpEmail}
                  </span>
                )}
              </div>
            )}

            <div className="doctor-form-group">
              <label htmlFor="doc-totp-code">6-Digit Verification Code *</label>
              <input
                id="doc-totp-code"
                type="text"
                inputMode="numeric"
                pattern="[0-9]*"
                maxLength={8}
                className="doctor-form-input"
                style={{ textAlign: 'center', letterSpacing: '0.25em', fontSize: '1.25rem', fontWeight: 600 }}
                placeholder="123456"
                required
                value={totpCode}
                onChange={(e) => setTotpCode(e.target.value)}
                disabled={submitting}
                autoFocus
              />
              <small style={{ color: 'var(--text-muted)', textAlign: 'center', display: 'block' }}>
                Enter the current code generated by your authenticator app
              </small>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              block
              disabled={submitting || !totpCode.trim()}
            >
              {submitting ? 'Verifying & Creating Account...' : 'Verify Code & Create Doctor Account'}
            </Button>
          </form>
        )}
      </div>
    </div>
  );
}
