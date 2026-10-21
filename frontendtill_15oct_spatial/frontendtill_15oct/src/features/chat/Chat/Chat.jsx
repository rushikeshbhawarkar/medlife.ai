/** Chat component.
 * Edit this file when changing this component behavior or markup.
 */
import { useCallback, useEffect, useState } from 'react';
import { TriangleAlert } from 'lucide-react';
import ChatHeader from '../ChatHeader/index.js';
import EmptyChat from '../EmptyChat/index.js';
import MessageList from '../MessageList/index.js';
import Composer from '../Composer/index.js';
import Spinner from '../../../components/Spinner/index.js';
import {
  fetchChat,
  saveChat,
  consumeToken,
  askMemberAI,
  getAIProviders,
  ApiError,
} from '../../../services/api.js';
import { buildQuery } from '../../../services/buildQuery.js';
import { downloadChat } from '../../../utils/downloadChat.js';
import './Chat.css';

export default function Chat({ email, memberName, member, onTokens }) {
  const [messages, setMessages] = useState([]);
  const [loadingChat, setLoadingChat] = useState(true);
  const [text, setText] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  // AI provider state
  const [providers, setProviders] = useState([]);
  const [selectedProvider, setSelectedProvider] = useState(
    () => localStorage.getItem('medlife_ai_provider') || ''
  );
  const [selectedModel, setSelectedModel] = useState(
    () => localStorage.getItem('medlife_ai_model') || ''
  );

  const used = member.tokens ?? 0;
  const limitReached = used >= 100;

  // Load configured AI providers from backend discovery endpoint
  useEffect(() => {
    let cancelled = false;
    getAIProviders()
      .then((data) => {
        if (cancelled) return;
        const list = Array.isArray(data?.providers) ? data.providers : [];
        setProviders(list);
        if (list.length > 0) {
          const currentValid = list.some((p) => p.id === selectedProvider);
          const activeProvId = currentValid ? selectedProvider : list[0].id;
          if (!currentValid) {
            setSelectedProvider(activeProvId);
            try {
              localStorage.setItem('medlife_ai_provider', activeProvId);
            } catch {}
          }
          const activeObj = list.find((p) => p.id === activeProvId);
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
        // Fallback gracefully if discovery endpoint is unavailable
        if (!cancelled) setProviders([]);
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
  };

  const handleSelectModel = (modelName) => {
    setSelectedModel(modelName);
    try {
      localStorage.setItem('medlife_ai_model', modelName);
    } catch {}
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
        setError(
          e instanceof ApiError && e.status === 400
            ? 'You have reached the question limit for this profile.'
            : e.message || 'Something went wrong. Please try again.'
        );
      } finally {
        setBusy(false);
      }
    },
    [text, busy, limitReached, email, memberName, member, messages, onTokens, selectedProvider, selectedModel]
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
      />
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
      />
    </section>
  );
}