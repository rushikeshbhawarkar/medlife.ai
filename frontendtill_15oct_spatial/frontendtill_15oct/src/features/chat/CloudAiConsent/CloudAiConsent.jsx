/** Cloud AI Explicit Consent and Privacy Disclosure component.
 * Displays data handling terms, exclusions, and consent actions for cloud AI providers.
 */
import { ShieldAlert, ShieldCheck, Info, ChevronDown, ChevronUp, Loader2, RefreshCw } from 'lucide-react';
import Button from '../../../components/Button/index.js';
import './CloudAiConsent.css';

function formatDate(isoString) {
  if (!isoString) return '';
  try {
    const d = new Date(isoString);
    return d.toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return isoString;
  }
}

export default function CloudAiConsent({
  providerLabel = 'Cloud AI',
  consentState = {},
  onGrantConsent,
  onRevokeConsent,
  onRetry,
  saving = false,
  expanded = false,
  onToggleExpanded,
}) {
  const { status, consent, consentAt, error } = consentState;
  const isGranted = Boolean(consent);
  const isRevoked = status === 'revoked';
  const isError = status === 'error';
  const isLoading = status === 'loading';

  return (
    <div
      className={`cloud-ai-consent-panel ${
        isGranted ? 'consent-panel-granted' : isError ? 'consent-panel-error' : 'consent-panel-required'
      }`}
      role="region"
      aria-label="Cloud AI privacy disclosure and consent"
    >
      <div className="consent-panel-header">
        <div className="consent-status-badge-wrap">
          {isLoading ? (
            <span className="consent-badge badge-loading">
              <Loader2 size={13} className="spin" /> Checking consent...
            </span>
          ) : isGranted ? (
            <span className="consent-badge badge-granted">
              <ShieldCheck size={13} /> Cloud AI Consent: Granted
            </span>
          ) : isRevoked ? (
            <span className="consent-badge badge-revoked">
              <ShieldAlert size={13} /> Cloud AI Consent: Revoked
            </span>
          ) : isError ? (
            <span className="consent-badge badge-error">
              <ShieldAlert size={13} /> Consent Check Failed
            </span>
          ) : (
            <span className="consent-badge badge-required">
              <ShieldAlert size={13} /> Explicit Consent Required
            </span>
          )}

          {isGranted && consentAt && (
            <span className="consent-timestamp">Granted {formatDate(consentAt)}</span>
          )}
        </div>

        <button
          type="button"
          className="consent-toggle-btn"
          onClick={onToggleExpanded}
          aria-expanded={expanded}
          aria-label={expanded ? 'Hide privacy disclosure details' : 'Show privacy disclosure details'}
        >
          {expanded ? (
            <>
              Hide details <ChevronUp size={14} />
            </>
          ) : (
            <>
              {isGranted ? 'View disclosure' : 'Review disclosure'} <ChevronDown size={14} />
            </>
          )}
        </button>
      </div>

      {/* Main explanation & actions */}
      {expanded ? (
        <div className="consent-disclosure-content">
          <div className="consent-summary-row">
            <Info size={16} className="consent-info-icon" />
            <div className="consent-text-block">
              <p className="consent-primary-text">
                Using <strong>{providerLabel}</strong> transmits your health question and relevant health-profile
                information (such as height, weight, blood pressure, medications, and reported conditions) to that
                external provider for processing.
              </p>
              <p className="consent-subtext">
                <strong>Privacy protection:</strong> MedLife&apos;s server excludes the family member&apos;s name and
                date of birth from the profile context sent to the provider.
              </p>
              <p className="consent-subtext">
                External cloud providers process data according to their own terms. Your explicit consent is
                required before any question can be sent to external cloud AI. Revoking consent stops future cloud
                AI requests from your account, but does not delete data previously submitted to the provider.
              </p>
            </div>
          </div>

          {isError && (
            <div className="consent-error-box" role="alert">
              <span>{error || 'Unable to load or verify consent status from the MedLife server.'}</span>
              {onRetry && (
                <Button size="sm" variant="ghost" onClick={onRetry} disabled={saving}>
                  <RefreshCw size={13} /> Retry
                </Button>
              )}
            </div>
          )}

          <div className="consent-actions-bar">
            {!isGranted ? (
              <div className="consent-action-group">
                <Button
                  size="sm"
                  variant="primary"
                  onClick={onGrantConsent}
                  disabled={saving || isLoading}
                >
                  {saving ? (
                    <>
                      <Loader2 size={14} className="spin" /> Updating consent...
                    </>
                  ) : (
                    <>
                      <ShieldCheck size={14} /> Grant Cloud AI Consent
                    </>
                  )}
                </Button>
                <span className="consent-action-note">
                  Questions will not be sent to external providers until you explicitly grant consent.
                </span>
              </div>
            ) : (
              <div className="consent-action-group">
                <Button
                  size="sm"
                  variant="ghost"
                  className="consent-revoke-btn"
                  onClick={onRevokeConsent}
                  disabled={saving}
                >
                  {saving ? (
                    <>
                      <Loader2 size={14} className="spin" /> Updating...
                    </>
                  ) : (
                    <>
                      <ShieldAlert size={14} /> Revoke Consent
                    </>
                  )}
                </Button>
                <span className="consent-action-note">
                  Revoking consent prevents future questions from being sent to cloud AI providers.
                </span>
              </div>
            )}
          </div>
        </div>
      ) : !isGranted ? (
        /* Collapsed notice for users without consent */
        <div className="consent-collapsed-prompt">
          <p>
            Cloud AI ({providerLabel}) requires your explicit consent to transmit your question and health profile
            (excluding name and date of birth) to the external provider.
          </p>
          <div className="consent-collapsed-actions">
            <Button size="sm" variant="primary" onClick={onGrantConsent} disabled={saving || isLoading}>
              {saving ? <Loader2 size={13} className="spin" /> : <ShieldCheck size={13} />}
              Grant Consent
            </Button>
            <Button size="sm" variant="ghost" onClick={onToggleExpanded}>
              Review Disclosure
            </Button>
          </div>
        </div>
      ) : null}
    </div>
  );
}
