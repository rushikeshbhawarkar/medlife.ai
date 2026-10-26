/** ChatHeader component.
 * Header layout with profile info, download button, AI provider & model selectors, and consent status.
 */
import { HeartPulse, Download, Cpu, ShieldCheck, ShieldAlert, Loader2, AlertCircle } from 'lucide-react';
import Button from '../../../components/Button/index.js';
import QuestionMeter from '../QuestionMeter/index.js';
import { fullName } from '../../../utils/person.js';
import './ChatHeader.css';

export default function ChatHeader({
  member,
  used,
  onDownload,
  hasMessages,
  providers = [],
  selectedProvider = '',
  onSelectProvider,
  selectedModel = '',
  onSelectModel,
  isCloud = false,
  consentState = {},
  onToggleConsentDetails,
}) {
  const currentProviderObj = providers.find((p) => p.id === selectedProvider);
  const models = currentProviderObj?.models || [];

  return (
    <header className="chat-header">
      <div className="chat-header-top">
        <span className="chat-head-icon">
          <HeartPulse />
        </span>
        <div className="chat-head-title">
          <h2>Ask medlife.ai</h2>
          <p>
            Answers tailored to <b>{fullName(member)}</b>
          </p>
        </div>
        <div className="chat-header-actions">
          <QuestionMeter used={used} />
          <Button variant="ghost" size="sm" disabled={!hasMessages} onClick={onDownload}>
            <Download size={16} /> Download
          </Button>
        </div>
      </div>

      {providers.length > 0 && (
        <div className="ai-selector-bar">
          <div className="ai-selector-wrap" title="Select AI Provider & Model">
            <Cpu size={14} className="ai-selector-icon" />
            <select
              className="ai-provider-select"
              value={selectedProvider}
              onChange={(e) => onSelectProvider?.(e.target.value)}
              aria-label="Select AI Provider"
            >
              {providers.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.label}{p.configured === false ? ' (Not Configured)' : ''}
                </option>
              ))}
            </select>
          </div>

          <div className="ai-badges-wrap">
            {isCloud ? (
              <button
                type="button"
                className={`ai-consent-pill ${
                  consentState.consent
                    ? 'pill-granted'
                    : consentState.status === 'error'
                    ? 'pill-error'
                    : 'pill-required'
                }`}
                onClick={onToggleConsentDetails}
                title={
                  consentState.consent
                    ? 'Cloud AI consent granted. Click to review or manage.'
                    : 'Cloud AI consent required. Click to review disclosure.'
                }
                aria-label="Cloud AI consent status"
              >
                {consentState.status === 'loading' ? (
                  <>
                    <Loader2 size={11} className="spin" /> Checking
                  </>
                ) : consentState.consent ? (
                  <>
                    <ShieldCheck size={11} /> Consent Active
                  </>
                ) : (
                  <>
                    <ShieldAlert size={11} /> Consent Required
                  </>
                )}
              </button>
            ) : (
              <span
                className="ai-consent-pill pill-local"
                title="Local model processing on your MedLife server (no cloud transfer)"
              >
                <ShieldCheck size={11} /> Local AI
              </span>
            )}

            {currentProviderObj?.configured === false && (
              <span
                className="ai-consent-pill pill-unconfigured"
                title={`Missing ${currentProviderObj?.envKey || 'API key'} in backend .env`}
              >
                <AlertCircle size={11} /> Not Configured on Server
              </span>
            )}
          </div>
        </div>
      )}
    </header>
  );
}