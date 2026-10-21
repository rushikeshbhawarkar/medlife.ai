import { useEffect, useRef, useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';
import {
  signUp,
  signIn,
  googleSignIn,
  verifyTotpSetup,
  verifyTotpLogin,
  restartTotpSetup,
  setAccessToken,
  forgotPassword,
  requestTotpRecovery,
} from '../../../services/api.js';
import Modal from '../../../components/Modal/index.js';
import Button from '../../../components/Button/index.js';
import Spinner from '../../../components/Spinner/index.js';
import Banner from '../../../components/Banner/index.js';
import '../../doctor/doctor.css';
import './SignInModal.css';

export default function SignInModal({ onClose, onSignIn, initialMode = 'signin' }) {
  const [mode, setMode] = useState(initialMode === 'doctor-apply' ? 'signin' : initialMode); // 'signin' | 'signup' | 'forgot' | 'totp-recovery'

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  // TOTP challenge state
  const [code, setCode] = useState('');
  const [challenge, setChallenge] = useState(null); // { kind: 'setup' | 'login', token, qr, key }

  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [busy, setBusy] = useState(false);

  const googleBtnRef = useRef(null);
  const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID || '';

  const verify = !!challenge;

  // Google sign-in initialization
  useEffect(() => {
    if (verify || mode === 'forgot' || mode === 'totp-recovery') {
      return;
    }
    if (!googleClientId) return;

    function initGoogle() {
      if (!window.google?.accounts?.id || !googleBtnRef.current) return;
      try {
        window.google.accounts.id.initialize({
          client_id: googleClientId,
          callback: async response => {
            if (!response.credential) return;
            setError('');
            setNotice('');
            setBusy(true);
            try {
              const r = await googleSignIn(response.credential);
              if (r.access_token) {
                setAccessToken(r.access_token);
                handleAuthSuccess(r.email || email.trim().toLowerCase());
              } else {
                throw new Error('Unexpected response from Google sign-in.');
              }
            } catch (err) {
              setError(err.message || 'Google sign-in failed.');
            } finally {
              setBusy(false);
            }
          },
        });
        window.google.accounts.id.renderButton(googleBtnRef.current, {
          theme: 'outline',
          size: 'large',
          width: googleBtnRef.current.offsetWidth || 280,
          text: 'continue_with',
          shape: 'pill',
        });
      } catch {}
    }

    if (window.google?.accounts?.id) {
      initGoogle();
    } else {
      const script = document.createElement('script');
      script.src = 'https://accounts.google.com/gsi/client';
      script.async = true;
      script.defer = true;
      script.onload = initGoogle;
      document.head.appendChild(script);
    }
  }, [mode, verify, googleClientId]);

  async function handleGoogleFallback() {
    if (!googleClientId) {
      setError('Google Sign-In is not configured. Add VITE_GOOGLE_CLIENT_ID to your frontend .env file.');
      return;
    }
    if (window.google?.accounts?.id) {
      window.google.accounts.id.prompt();
    }
  }

  // Handle successful login/signup authentication
  const handleAuthSuccess = (authedEmail) => {
    onSignIn(authedEmail);
  };

  // Click handler for "Apply to Become a Doctor" entry point
  const handleApplyAsDoctorClick = () => {
    onClose();
    window.location.hash = '#/apply-doctor';
  };

  // Form submission for sign in / sign up / totp / password reset / recovery
  async function submit(e) {
    e.preventDefault();
    setError('');
    setNotice('');
    setBusy(true);

    try {
      // 1. Password reset request
      if (mode === 'forgot') {
        const r = await forgotPassword(email.trim().toLowerCase());
        setNotice(r.detail || 'If an account exists, a reset link has been emailed.');
        return;
      }

      // 2. Authenticator recovery request
      if (mode === 'totp-recovery') {
        const r = await requestTotpRecovery(email.trim().toLowerCase());
        setNotice(
          r.detail ||
            'If an account exists with this email, an authenticator recovery link has been sent. Check your inbox.'
        );
        return;
      }

      // 3. TOTP Setup verification
      if (challenge?.kind === 'setup') {
        const r = await verifyTotpSetup(challenge.token, code);
        setAccessToken(r.access_token);
        handleAuthSuccess(r.email || email.trim().toLowerCase());
        return;
      }

      // 4. TOTP Login verification
      if (challenge?.kind === 'login') {
        const r = await verifyTotpLogin(challenge.token, code);
        setAccessToken(r.access_token);
        handleAuthSuccess(r.email || email.trim().toLowerCase());
        return;
      }

      // 5. Sign Up (Patient Account Only)
      if (mode === 'signup') {
        const r = await signUp(email.trim().toLowerCase(), password);
        setChallenge({
          kind: 'setup',
          token: r.setup_token,
          qr: r.qr_code,
          key: r.manual_key,
        });
        setNotice('Scan this QR code with an authenticator app (Google Authenticator, etc.), then enter the 6-digit code.');
        return;
      }

      // 6. Sign In (Password-based)
      try {
        const r = await signIn(email.trim().toLowerCase(), password);
        if (r.totp_setup_required) {
          setChallenge({
            kind: 'setup',
            token: r.setup_token,
            qr: r.qr_code,
            key: r.manual_key,
          });
          setNotice(r.detail || 'Scan this QR code with an authenticator app, then enter the 6-digit code.');
          return;
        }
        if (r.totp_required) {
          setChallenge({
            kind: 'login',
            token: r.challenge_token,
          });
          setNotice('Enter the current 6-digit code from your authenticator app.');
          return;
        }
        if (r.access_token) {
          setAccessToken(r.access_token);
          handleAuthSuccess(r.email || email.trim().toLowerCase());
          return;
        }
      } catch (signInErr) {
        const msg = signInErr.message || '';
        if (msg.toLowerCase().includes('totp') || msg.toLowerCase().includes('setup must be completed')) {
          const setupR = await restartTotpSetup(email.trim().toLowerCase(), password);
          setChallenge({
            kind: 'setup',
            token: setupR.setup_token,
            qr: setupR.qr_code,
            key: setupR.manual_key,
          });
          setNotice('Complete two-factor authentication setup: scan this QR code with an authenticator app, then enter the 6-digit code.');
          return;
        }
        throw signInErr;
      }
    } catch (err) {
      setError(err.message || 'Authentication failed.');
    } finally {
      setBusy(false);
    }
  }

  const modalTitle = verify
    ? challenge.kind === 'setup'
      ? 'Secure your account'
      : 'Two-step verification'
    : mode === 'totp-recovery'
    ? 'Recover your account'
    : mode === 'signup'
    ? 'Create your Medlife account'
    : mode === 'forgot'
    ? 'Reset password'
    : 'Welcome to medlife.ai';

  const modalSubtitle = verify
    ? 'Medlife uses authenticator-based two-factor security.'
    : mode === 'totp-recovery'
    ? 'Enter your registered email address to receive an authenticator recovery link.'
    : 'Sign in or create an account to securely access your family health profiles.';

  return (
    <Modal
      title={modalTitle}
      subtitle={modalSubtitle}
      onClose={onClose}
    >
      <form className="signin-form" onSubmit={submit}>
        {/* Normal Sign In / Sign Up / Forgot Password / Recovery Email input */}
        {!verify && (
          <>
            <label>Email address</label>
            <div className="email-input">
              <input
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="you@example.com"
              />
            </div>
            {mode !== 'forgot' && mode !== 'totp-recovery' && (
              <>
                <label>Password</label>
                <div className="email-input">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    autoComplete={mode === 'signup' ? 'new-password' : 'current-password'}
                    required
                    minLength={6}
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                    placeholder="••••••••"
                  />
                  <button
                    type="button"
                    className="password-toggle-btn"
                    onClick={() => setShowPassword(!showPassword)}
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                    tabIndex={-1}
                  >
                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
              </>
            )}
          </>
        )}

        {/* TOTP challenge input */}
        {verify && (
          <>
            {challenge.kind === 'setup' && challenge.qr && (
              <div className="totp-setup-container">
                <p className="totp-help-text">
                  Open your authenticator app and scan this barcode:
                </p>
                <div className="totp-qr-wrapper">
                  <img
                    src={`data:image/png;base64,${challenge.qr}`}
                    alt="Authenticator QR code"
                    className="totp-qr-img"
                  />
                </div>
                {challenge.key && (
                  <p className="totp-manual-key">
                    Can't scan? Enter key manually:{' '}
                    <code>{challenge.key}</code>
                  </p>
                )}
              </div>
            )}
            <label>6-digit authenticator code</label>
            <div className="email-input">
              <input
                type="text"
                inputMode="numeric"
                pattern="[0-9]*"
                maxLength={6}
                required
                autoFocus
                value={code}
                onChange={e => setCode(e.target.value.replace(/\D/g, ''))}
                placeholder="123456"
                className="totp-code-input"
              />
            </div>
          </>
        )}

        {error && <Banner variant="error">{error}</Banner>}
        {notice && <Banner variant="info">{notice}</Banner>}

        <Button type="submit" variant="primary" block disabled={busy}>
          {busy ? (
            <Spinner />
          ) : verify ? (
            'Verify code'
          ) : mode === 'forgot' ? (
            'Send reset link'
          ) : mode === 'totp-recovery' ? (
            'Send recovery link'
          ) : mode === 'signup' ? (
            'Create account'
          ) : (
            'Sign in'
          )}
        </Button>

        {/* Authenticator recovery link shown during TOTP login */}
        {verify && challenge.kind === 'login' && (
          <div className="totp-recovery-link-container">
            <button
              type="button"
              className="text-button"
              onClick={() => {
                setChallenge(null);
                setCode('');
                setError('');
                setNotice('');
                setMode('totp-recovery');
              }}
            >
              Lost access to your authenticator? Recover your account.
            </button>
          </div>
        )}

        {/* Google sign-in option */}
        {!verify && mode !== 'forgot' && mode !== 'totp-recovery' && (
          <>
            <div className="signin-divider"><span>or</span></div>
            {googleClientId ? (
              <div className="google-signin-container">
                <div ref={googleBtnRef} className="google-btn-wrapper" />
              </div>
            ) : (
              <button
                type="button"
                className="google-signin-btn"
                onClick={handleGoogleFallback}
              >
                <svg width="18" height="18" viewBox="0 0 18 18">
                  <path fill="#4285F4" d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.874 2.684-6.616z" />
                  <path fill="#34A853" d="M9 18c2.43 0 4.467-.806 5.956-2.184l-2.908-2.258c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 0 0 9 18z" />
                  <path fill="#FBBC05" d="M3.964 10.707c-.18-.54-.282-1.117-.282-1.707 0-.59.102-1.167.282-1.707V4.961H.957A8.996 8.996 0 0 0 0 9c0 1.452.348 2.827.957 4.039l3.007-2.332z" />
                  <path fill="#EA4335" d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 0 0 .957 4.961L3.964 7.293C4.672 5.166 6.656 3.58 9 3.58z" />
                </svg>
                Continue with Google
              </button>
            )}
          </>
        )}

        {/* Mode switching links */}
        {!verify && (
          <p className="signin-links">
            {mode !== 'signin' && (
              <button
                type="button"
                className="text-button"
                onClick={() => {
                  setMode('signin');
                  setNotice('');
                  setError('');
                }}
              >
                Sign in
              </button>
            )}
            {mode !== 'signup' && (
              <button
                type="button"
                className="text-button"
                onClick={() => {
                  setMode('signup');
                  setNotice('');
                  setError('');
                }}
              >
                Create account
              </button>
            )}
            <button
              type="button"
              className="text-button doctor-apply-link"
              onClick={handleApplyAsDoctorClick}
              title="Apply to Become a Verified MedLife Healthcare Practitioner"
            >
              Apply to Become a Doctor
            </button>
            {mode !== 'forgot' && (
              <button
                type="button"
                className="text-button"
                onClick={() => {
                  setMode('forgot');
                  setNotice('');
                  setError('');
                }}
              >
                Forgot password?
              </button>
            )}
          </p>
        )}

        {verify && (
          <button
            type="button"
            className="text-button"
            onClick={() => {
              setChallenge(null);
              setCode('');
              setNotice('');
              setError('');
            }}
          >
            Back
          </button>
        )}
      </form>
    </Modal>
  );
}
