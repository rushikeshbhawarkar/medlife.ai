/** Composer component.
 * Input box and send control for health questions.
 */
import { useRef, useEffect } from 'react';
import { Send, ShieldAlert, AlertCircle } from 'lucide-react';
import './Composer.css';

export default function Composer({
  text,
  setText,
  onSend,
  busy,
  limitReached,
  cloudConsentRequired = false,
  onReviewConsent,
  providerConfigured = true,
  providerLabel = '',
  providerEnvKey = '',
}) {
  const ref = useRef(null);

  useEffect(() => {
    if (!busy && !limitReached && !cloudConsentRequired && providerConfigured) {
      ref.current?.focus();
    }
  }, [busy, limitReached, cloudConsentRequired, providerConfigured]);

  function key(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  }

  const placeholderText = !providerConfigured
    ? `${providerLabel} is not configured on the server (missing API key in .env)`
    : limitReached
    ? 'Question limit reached for this profile'
    : cloudConsentRequired
    ? 'Cloud AI consent required to send question to this provider...'
    : 'Type your health question...';

  return (
    <div className="composer-wrap">
      {!providerConfigured ? (
        <div className="composer-unconfigured-notice" role="alert">
          <AlertCircle size={14} />
          <span>
            <strong>{providerLabel}</strong> is not configured on the server. Add{' '}
            <code>{providerEnvKey || 'API_KEY'}</code> to backend <code>.env</code> to send questions.
          </span>
        </div>
      ) : cloudConsentRequired ? (
        <div className="composer-consent-notice" role="alert">
          <ShieldAlert size={14} />
          <span>Cloud AI consent required for this provider.</span>
          {onReviewConsent && (
            <button type="button" className="composer-consent-link" onClick={onReviewConsent}>
              Review &amp; Grant Consent
            </button>
          )}
        </div>
      ) : null}

      <div className="composer">
        <textarea
          ref={ref}
          rows="1"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={key}
          disabled={busy || limitReached || !providerConfigured}
          placeholder={placeholderText}
          aria-label="Type your health question"
        />
        <button
          aria-label="Send message"
          disabled={!text.trim() || busy || limitReached || !providerConfigured}
          onClick={onSend}
        >
          <Send size={19} />
        </button>
      </div>
      <p>medlife.ai shares general health information and is not a substitute for professional medical advice.</p>
    </div>
  );
}