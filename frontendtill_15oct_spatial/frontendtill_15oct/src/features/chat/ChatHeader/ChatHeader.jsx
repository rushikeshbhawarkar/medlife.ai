/** ChatHeader component.
 * Edit this file when changing this component behavior or markup.
 */
import { HeartPulse, Download, Cpu } from 'lucide-react';
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
}) {
  const currentProviderObj = providers.find((p) => p.id === selectedProvider);
  const models = currentProviderObj?.models || [];

  return (
    <header className="chat-header">
      <span className="chat-head-icon">
        <HeartPulse />
      </span>
      <div className="chat-head-title">
        <h2>Ask medlife.ai</h2>
        <p>
          Answers tailored to <b>{fullName(member)}</b>
        </p>
      </div>

      {providers.length > 0 && (
        <div className="ai-selector-wrap" title="Select AI Provider">
          <Cpu size={14} className="ai-selector-icon" />
          <select
            className="ai-provider-select"
            value={selectedProvider}
            onChange={(e) => onSelectProvider?.(e.target.value)}
            aria-label="Select AI Provider"
          >
            {providers.map((p) => (
              <option key={p.id} value={p.id}>
                {p.label}
              </option>
            ))}
          </select>

          {models.length > 1 && (
            <select
              className="ai-model-select"
              value={selectedModel}
              onChange={(e) => onSelectModel?.(e.target.value)}
              aria-label="Select Model"
            >
              {models.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
          )}
        </div>
      )}

      <QuestionMeter used={used} />
      <Button variant="ghost" size="sm" disabled={!hasMessages} onClick={onDownload}>
        <Download size={16} /> Download
      </Button>
    </header>
  );
}