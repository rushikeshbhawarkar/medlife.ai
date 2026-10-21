import { useEffect, useState, useRef, useCallback } from 'react';
import Modal from '../../components/Modal/index.js';
import Button from '../../components/Button/index.js';
import Spinner from '../../components/Spinner/index.js';
import Banner from '../../components/Banner/index.js';
import { getChatMessages, sendChatMessage } from '../../services/api.js';
import { Send, RefreshCw } from 'lucide-react';

export default function DoctorChatModal({ chatRequest, myEmail, onClose }) {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [text, setText] = useState('');
  const [sending, setSending] = useState(false);
  const scrollRef = useRef(null);

  const loadMessages = useCallback(async () => {
    try {
      const data = await getChatMessages(chatRequest.id);
      setMessages(data?.messages || []);
      setError('');
    } catch (e) {
      setError(e.message || 'Unable to load consultation messages.');
    } finally {
      setLoading(false);
    }
  }, [chatRequest.id]);

  useEffect(() => {
    loadMessages();
    const interval = setInterval(loadMessages, 5000);
    return () => clearInterval(interval);
  }, [loadMessages]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!text.trim() || sending) return;
    setSending(true);
    setError('');
    try {
      await sendChatMessage(chatRequest.id, text.trim());
      setText('');
      await loadMessages();
    } catch (e) {
      setError(e.message || 'Unable to send message.');
    } finally {
      setSending(false);
    }
  };

  const isAccepted = chatRequest.status === 'accepted';

  return (
    <Modal
      title={`Consultation Chat #${chatRequest.id}`}
      subtitle={`Patient: ${chatRequest.member_name || 'Member'} | Status: ${chatRequest.status}`}
      onClose={onClose}
      wide={true}
    >
      <div className="consultation-chat-body">
        {error && <Banner variant="error">{error}</Banner>}

        {!isAccepted && (
          <Banner variant="info">
            Messaging is available only after the consultation request is accepted by the doctor and record consent is active.
          </Banner>
        )}

        <div className="consultation-messages-list" ref={scrollRef}>
          {loading ? (
            <Spinner />
          ) : messages.length === 0 ? (
            <div className="doctor-empty-state">
              <p>No messages yet. Send a message to begin consultation.</p>
            </div>
          ) : (
            messages.map((m) => {
              const isMine =
                m.sender_email &&
                myEmail &&
                m.sender_email.toLowerCase() === myEmail.toLowerCase();
              return (
                <div
                  key={m.id}
                  className={`consultation-message-bubble ${
                    isMine ? 'message-mine' : 'message-theirs'
                  }`}
                >
                  <div>{m.text}</div>
                  <div className="message-meta">
                    <span>{isMine ? 'You' : m.sender_email}</span>
                    <span>
                      {new Date(m.created_at).toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </span>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {isAccepted && (
          <form className="consultation-chat-input-bar" onSubmit={handleSend}>
            <input
              type="text"
              className="doctor-form-input"
              placeholder="Type your consultation message..."
              value={text}
              onChange={(e) => setText(e.target.value)}
              disabled={sending}
              maxLength={20000}
            />
            <Button
              type="submit"
              variant="primary"
              size="md"
              disabled={!text.trim() || sending}
            >
              {sending ? <Spinner size={16} /> : <Send size={16} />}
            </Button>
            <Button
              type="button"
              variant="secondary"
              size="md"
              onClick={loadMessages}
              title="Refresh messages"
            >
              <RefreshCw size={16} />
            </Button>
          </form>
        )}
      </div>
    </Modal>
  );
}
