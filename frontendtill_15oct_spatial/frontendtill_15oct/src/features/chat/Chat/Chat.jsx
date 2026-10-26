/** Chat component.
 * Integrates family-member AI chat with explicit Cloud AI consent gating.
 */
import { useCallback, useEffect, useState } from 'react';
import { TriangleAlert } from 'lucide-react';
import ChatHeader from '../ChatHeader/index.js';
import EmptyChat from '../EmptyChat/index.js';
import MessageList from '../MessageList/index.js';
import Composer from '../Composer/index.js';
import CloudAiConsent from '../CloudAiConsent/index.js';
import Spinner from '../../../components/Spinner/index.js';
import {
  fetchChat,
  saveChat,
  consumeToken,
  askMemberAI,
  getAIProviders,
  getCloudAiConsent,
  setCloudAiConsent,
  isCloudAiProvider,
  ApiError,
} from '../../../services/api.js';
import { buildQuery } from '../../../services/buildQuery.js';
import { downloadChat } from '../../../utils/downloadChat.js';
import './Chat.css';

// Master list of supported AI providers in MedLife (clean names: Gemini, ChatGPT, Claude, Local model)
const CATALOG_PROVIDERS = [
  {
    id: 'local',
    label: 'Local model (Ollama)',
    defaultModels: ['llama3.1:8b'],
    isCloud: false,
    envKey: 'OLLAMA_MODELS',
  },
  {
    id: 'gemini',
    label: 'Gemini',
    defaultModels: ['gemini-2.0-flash'],
    isCloud: true,
    envKey: 'GEMINI_API_KEY',
  },
  {
    id: 'openai',
    label: 'ChatGPT',
    defaultModels: ['gpt-4o-mini'],
    isCloud: true,
    envKey: 'OPENAI_API_KEY',
  },
  {
    id: 'claude',
    label: 'Claude',
    defaultModels: ['claude-3-5-haiku-20241022'],
    isCloud: true,
    envKey: 'ANTHROPIC_API_KEY',
  },
];

function mergeProviders(backendProviders = []) {
  const map = new Map();
  if (Array.isArray(backendProviders)) {
    backendProviders.forEach((bp) => {
      if (bp && bp.id) map.set(bp.id, bp);
    });
  }

  return CATALOG_PROVIDERS.map((cat) => {
    const backendMatch = map.get(cat.id);
    if (backendMatch) {
      return {
        ...cat,
        configured: true,
        models:
          Array.isArray(backendMatch.models) && backendMatch.models.length > 0
            ? backendMatch.models
            : cat.defaultModels,
      };
    }
    return {
      id: cat.id,
      label: cat.label,
      configured: false,
      models: cat.defaultModels,
      isCloud: cat.isCloud,
      envKey: cat.envKey,
    };
  });
}

export default function Chat({ email, memberName, member, onTokens }) {
  const [messages, setMessages] = useState([]);
  const [loadingChat, setLoadingChat] = useState(true);
  const [text, setText] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  // AI provider state: initialized with full catalog so all options are always visible
  const [providers, setProviders] = useState(() => mergeProviders([]));
  const [selectedProvider, setSelectedProvider] = useState(
    () => localStorage.getItem('medlife_ai_provider') || 'local'
  );
  const [selectedModel, setSelectedModel] = useState(
    () => localStorage.getItem('medlife_ai_model') || ''
  );

  // Cloud AI Consent state
  const [consentState, setConsentState] = useState({
    status: 'loading', // 'loading' | 'granted' | 'not_granted' | 'revoked' | 'error'
    consent: false,
    consentAt: null,
    error: null,
  });
  const [savingConsent, setSavingConsent] = useState(false);
  const [showConsentDetails, setShowConsentDetails] = useState(false);

  const used = member.tokens ?? 0;
  const limitReached = used >= 100;

  // Determine active provider ID and whether it is a cloud provider
  const activeProvId = selectedProvider || (providers[0]?.id || 'local');
  const isCloud = isCloudAiProvider(activeProvId);
  const cloudConsentRequired = isCloud && !consentState.consent;
  const currentProviderObj = providers.find((p) => p.id === activeProvId);

  // Fetch Cloud AI consent status from backend
  useEffect(() => {
    let cancelled = false;
    getCloudAiConsent()
      .then((data) => {
        if (cancelled) return;
        setConsentState({
          status: data.consent ? 'granted' : 'not_granted',
          consent: Boolean(data.consent),
          consentAt: data.consentAt || null,
          error: null,
        });
      })
      .catch((err) => {
        if (cancelled) return;
        setConsentState({
          status: 'error',
          consent: false,
          consentAt: null,
          error: err.message || 'Unable to load Cloud AI consent status.',
        });
      });

    return () => {
      cancelled = true;
    };
  }, []);

  // Load configured AI providers from backend discovery endpoint
  useEffect(() => {
    let cancelled = false;
    getAIProviders()
      .then((data) => {
        if (cancelled) return;
        const list = mergeProviders(data?.providers);
        setProviders(list);
        if (list.length > 0) {
          const currentValid = list.some((p) => p.id === selectedProvider);
          const activeId = currentValid ? selectedProvider : list[0].id;
          if (!currentValid) {
            setSelectedProvider(activeId);
            try {
              localStorage.setItem('medlife_ai_provider', activeId);
            } catch {}
          }
          const activeObj = list.find((p) => p.id === activeId);
          if (activeObj?.models?.length) {
            if (!activeObj.models.includes(selectedModel)) {
              setSelectedModel(activeObj.models[0]);
              try {
                localStorage.setItem('medlife_ai_model', activeObj.models[0]);
              } catch {}
            }
          }
        }
      })
      .catch(() => {
        if (!cancelled) setProviders(mergeProviders([]));
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const handleSelectProvider = (id) => {
    setSelectedProvider(id);
    try {
      localStorage.setItem('medlife_ai_provider', id);
    } catch {}
    const provObj = providers.find((p) => p.id === id);
    if (provObj?.models?.length) {
      setSelectedModel(provObj.models[0]);
      try {
        localStorage.setItem('medlife_ai_model', provObj.models[0]);
      } catch {}
    } else {
      setSelectedModel('');
    }

    // If switching to a cloud provider without consent, ensure disclosure is visible
    if (isCloudAiProvider(id) && !consentState.consent) {
      setShowConsentDetails(true);
    }
  };

  const handleSelectModel = (modelName) => {
    setSelectedModel(modelName);
    try {
      localStorage.setItem('medlife_ai_model', modelName);
    } catch {}
  };

  const handleGrantConsent = async () => {
    if (savingConsent) return;
    setSavingConsent(true);
    setError('');
    try {
      const data = await setCloudAiConsent(true);
      setConsentState({
        status: 'granted',
        consent: true,
        consentAt: data.consentAt || new Date().toISOString(),
        error: null,
      });
    } catch (err) {
      setError(err.message || 'Failed to update Cloud AI consent. Please try again.');
      setConsentState((prev) => ({
        ...prev,
        status: 'error',
        error: err.message || 'Failed to update consent.',
      }));
    } finally {
      setSavingConsent(false);
    }
  };

  const handleRevokeConsent = async () => {
    if (savingConsent) return;
    setSavingConsent(true);
    setError('');
    try {
      const data = await setCloudAiConsent(false);
      setConsentState({
        status: 'revoked',
        consent: false,
        consentAt: null,
        error: null,
      });
      setShowConsentDetails(true);
    } catch (err) {
      setError(err.message || 'Failed to revoke Cloud AI consent. Please try again.');
    } finally {
      setSavingConsent(false);
    }
  };

  const handleRetryConsent = async () => {
    if (savingConsent) return;
    setSavingConsent(true);
    setError('');
    setConsentState((prev) => ({ ...prev, status: 'loading' }));
    try {
      const data = await getCloudAiConsent({ force: true });
      setConsentState({
        status: data.consent ? 'granted' : 'not_granted',
        consent: Boolean(data.consent),
        consentAt: data.consentAt || null,
        error: null,
      });
    } catch (err) {
      setConsentState({
        status: 'error',
        consent: false,
        consentAt: null,
        error: err.message || 'Unable to verify consent status.',
      });
    } finally {
      setSavingConsent(false);
    }
  };

  useEffect(() => {
    let cancelled = false;
    setLoadingChat(true);
    setMessages([]);
    setError('');
    setText('');
    fetchChat(email, memberName)
      .then((m) => {
        if (!cancelled) setMessages(Array.isArray(m) ? m : []);
      })
      .catch(() => {
        if (!cancelled) setMessages([]);
      })
      .finally(() => {
        if (!cancelled) setLoadingChat(false);
      });
    return () => {
      cancelled = true;
    };
  }, [email, memberName]);

  const send = useCallback(
    async (question = text) => {
      const q = question.trim();
      if (!q || busy || limitReached) return;

      // Gate cloud providers: do not submit to server if consent is not granted
      if (isCloud && !consentState.consent) {
        setShowConsentDetails(true);
        setError(
          'Cloud AI consent is required before sending questions to external providers. Please review the disclosure and grant consent.'
        );
        return;
      }

      // Check if provider is configured on server
      if (currentProviderObj && currentProviderObj.configured === false) {
        setError(
          `${currentProviderObj.label} is not configured on the server. Please add ${currentProviderObj.envKey || 'the API key'} to medlifebackendtill 16oct/.env to ask questions with this provider.`
        );
        return;
      }

      setText('');
      setError('');
      const userMessage = { role: 'user', text: q, ts: Date.now() };
      setMessages((prev) => [...prev, userMessage]);
      setBusy(true);
      try {
        const count = await consumeToken(email, memberName);
        onTokens(memberName, count);
        const result = await askMemberAI(
          memberName,
          buildQuery(member, q),
          selectedProvider || undefined,
          selectedModel || undefined
        );
        const reply = result?.answer || 'I could not generate a response.';
        const next = [...messages, userMessage, { role: 'ai', text: reply, ts: Date.now() }];
        setMessages(next);
        try {
          await saveChat(email, memberName, next);
        } catch {}
      } catch (e) {
        setMessages((prev) => prev.filter((m) => m !== userMessage));
        setText(q);

        const isConsentErr =
          e instanceof ApiError &&
          e.status === 403 &&
          (e.message?.toLowerCase().includes('consent') ||
            e.message?.toLowerCase().includes('cloud_ai_consent'));

        if (isConsentErr) {
          // Re-validate consent status from authoritative backend state
          getCloudAiConsent({ force: true })
            .then((data) => {
              setConsentState({
                status: data.consent ? 'granted' : 'not_granted',
                consent: Boolean(data.consent),
                consentAt: data.consentAt || null,
                error: null,
              });
            })
            .catch(() => {});
          setShowConsentDetails(true);
          setError(
            'Cloud AI consent is required. Please review the disclosure and grant consent to continue.'
          );
        } else {
          setError(
            e instanceof ApiError && e.status === 400
              ? 'You have reached the question limit for this profile.'
              : e.message || 'Something went wrong. Please try again.'
          );
        }
      } finally {
        setBusy(false);
      }
    },
    [
      text,
      busy,
      limitReached,
      email,
      memberName,
      member,
      messages,
      onTokens,
      selectedProvider,
      selectedModel,
      isCloud,
      consentState.consent,
      currentProviderObj,
    ]
  );

  return (
    <section className="chat-card">
      <ChatHeader
        member={member}
        used={used}
        hasMessages={messages.length > 0}
        onDownload={() => downloadChat(member, messages)}
        providers={providers}
        selectedProvider={selectedProvider}
        onSelectProvider={handleSelectProvider}
        selectedModel={selectedModel}
        onSelectModel={handleSelectModel}
        isCloud={isCloud}
        consentState={consentState}
        onToggleConsentDetails={() => setShowConsentDetails((prev) => !prev)}
      />

      {isCloud && (
        <CloudAiConsent
          providerLabel={currentProviderObj?.label || selectedProvider}
          consentState={consentState}
          onGrantConsent={handleGrantConsent}
          onRevokeConsent={handleRevokeConsent}
          onRetry={handleRetryConsent}
          saving={savingConsent}
          expanded={showConsentDetails || !consentState.consent}
          onToggleExpanded={() => setShowConsentDetails((prev) => !prev)}
        />
      )}

      {error && (
        <div className="chat-error" role="alert">
          <TriangleAlert size={17} />
          {error}
        </div>
      )}

      {loadingChat ? (
        <Spinner />
      ) : messages.length === 0 && !busy ? (
        <EmptyChat onSuggestion={(q) => send(q)} />
      ) : (
        <MessageList messages={messages} busy={busy} />
      )}

      <Composer
        text={text}
        setText={setText}
        onSend={() => send()}
        busy={busy}
        limitReached={limitReached}
        cloudConsentRequired={cloudConsentRequired}
        onReviewConsent={() => setShowConsentDetails(true)}
        providerConfigured={currentProviderObj?.configured !== false}
        providerLabel={currentProviderObj?.label || activeProvId}
        providerEnvKey={currentProviderObj?.envKey || ''}
      />
    </section>
  );
}