import { useEffect, useState } from 'react';
import { setupTotpRecovery, verifyTotpRecovery } from '../../services/api.js';
import './SignInModal/SignInModal.css';
import '../../components/Button/Button.css';

function readRecoveryToken() {
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

  // 3. Support encoded format
  let decodedHash;
  try {
    decodedHash = decodeURIComponent(hash);
  } catch {
    decodedHash = hash;
  }

  const marker = '#token=';
  const index = decodedHash.lastIndexOf(marker);
  if (index !== -1) {
    return decodedHash.slice(index + marker.length).split('&')[0];
  }

  // 4. Support a token after ? or & in the fragment
  const fragmentQuery = decodedHash.match(/[?&]token=([^&]*)/);
  if (fragmentQuery) {
    try {
      return decodeURIComponent(fragmentQuery[1]);
    } catch {
      return fragmentQuery[1];
    }
  }

  return '';
}

export default function RecoverTotpPage({ onReturnToSignIn }) {
  const [token, setToken] = useState('');
  const [setupData, setSetupData] = useState(null);
  const [setupLoading, setSetupLoading] = useState(true);
  const [setupError, setSetupError] = useState('');

  const [code, setCode] = useState('');
  const [verifyBusy, setVerifyBusy] = useState(false);
  const [verifyError, setVerifyError] = useState('');
  const [verifySuccess, setVerifySuccess] = useState('');

  useEffect(() => {
    const rawToken = readRecoveryToken();
    if (!rawToken) {
      setSetupError('The authenticator recovery link is missing or invalid. Please request a new recovery link.');
      setSetupLoading(false);
      return;
    }

    setToken(rawToken);

    let active = true;
    setupTotpRecovery(rawToken)
      .then(res => {
        if (!active) return;
        setSetupData(res);
        setSetupLoading(false);
      })
      .catch(err => {
        if (!active) return;
        setSetupError(err.message || 'Unable to load authenticator recovery. The link may have expired.');
        setSetupLoading(false);
      });

    return () => {
      active = false;
    };
  }, []);

  async function handleVerify(e) {
    e.preventDefault();
    if (!token) return;

    if (code.length !== 6) {
      setVerifyError('Please enter the 6-digit code from your authenticator app.');
      return;
    }

    setVerifyError('');
    setVerifyBusy(true);

    try {
      const res = await verifyTotpRecovery(token, code);
      setVerifySuccess(
        res.detail || 'Authenticator updated successfully. Please sign in with your new code.'
      );
      // Remove the recovery token from the URL bar while preserving the page view
      window.history.replaceState(
        null,
        '',
        window.location.pathname + window.location.search + '#/recover-totp'
      );
    } catch (err) {
      setVerifyError(err.message || 'Verification failed. Please check the code and try again.');
    } finally {
      setVerifyBusy(false);
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
      <h1>Recover Authenticator</h1>

      {setupLoading && <p>Verifying recovery link and generating your new authenticator key…</p>}

      {setupError && !setupLoading && (
        <>
          <p role="alert" className="reset-error">{setupError}</p>
          <button
            type="button"
            className="btn btn-primary"
            onClick={handleReturn}
          >
            Return to MedLife
          </button>
        </>
      )}

      {verifySuccess && (
        <>
          <p role="status" className="reset-success">{verifySuccess}</p>
          <button
            type="button"
            className="btn btn-primary"
            onClick={handleReturn}
          >
            Sign In with New Authenticator
          </button>
        </>
      )}

      {!setupLoading && !setupError && !verifySuccess && setupData && (
        <>
          <p>
            Scan this new QR code with your authenticator app (Google Authenticator, Authy, etc.), or enter the manual key below.
          </p>

          {setupData.email && (
            <p style={{ fontSize: '0.88rem', opacity: 0.85, margin: '4px 0 12px' }}>
              Account: <strong>{setupData.email}</strong>
            </p>
          )}

          {setupData.qr_code && (
            <img
              src={setupData.qr_code}
              alt="New Authenticator QR code"
              className="qr-plate"
            />
          )}

          {setupData.manual_key && (
            <p style={{ textAlign: 'center', fontSize: '0.88rem', margin: '8px 0 16px' }}>
              Manual setup key: <code style={{ userSelect: 'all' }}>{setupData.manual_key}</code>
            </p>
          )}

          <form onSubmit={handleVerify}>
            <label htmlFor="recovery-code">Enter 6-digit Authenticator Code</label>
            <input
              id="recovery-code"
              inputMode="numeric"
              autoComplete="one-time-code"
              pattern="[0-9]{6}"
              maxLength={6}
              required
              value={code}
              onChange={e => setCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
              placeholder="123456"
              className="reset-input"
            />

            {verifyError && <p role="alert" className="reset-error">{verifyError}</p>}

            <button
              type="submit"
              disabled={verifyBusy || code.length !== 6}
              className="btn btn-primary btn-lg btn-block"
            >
              {verifyBusy ? 'Activating authenticator…' : 'Activate & Complete Recovery'}
            </button>

            <div style={{ marginTop: '16px', textAlign: 'center' }}>
              <button
                type="button"
                className="text-button"
                onClick={handleReturn}
              >
                Cancel and return to sign in
              </button>
            </div>
          </form>
        </>
      )}
    </main>
  );
}
