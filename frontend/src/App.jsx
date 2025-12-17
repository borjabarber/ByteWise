import { useState, useRef, useEffect } from 'react';
import './App.css';

const API_URL = 'http://localhost:8000';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [showSidebar, setShowSidebar] = useState(true);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      const response = await fetch(`${API_URL}/sessions`);
      const data = await response.json();
      setSessions(data.sessions || []);
    } catch (error) {
      console.error('Error loading sessions:', error);
    }
  };

  const loadSession = async (id) => {
    try {
      const response = await fetch(`${API_URL}/sessions/${id}`);
      const data = await response.json();
      setSessionId(id);
      setMessages(data.messages.map((msg, index) => ({
        id: index,
        role: msg.role,
        content: msg.content
      })));
    } catch (error) {
      console.error('Error loading session:', error);
    }
  };

  const startNewSession = () => {
    setSessionId(null);
    setMessages([]);
    inputRef.current?.focus();
  };

  const deleteSession = async (id, e) => {
    e.stopPropagation();
    try {
      await fetch(`${API_URL}/sessions/${id}`, { method: 'DELETE' });
      loadSessions();
      if (sessionId === id) {
        startNewSession();
      }
    } catch (error) {
      console.error('Error deleting session:', error);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue.trim();
    setInputValue('');

    const newUserMessage = {
      id: messages.length,
      role: 'user',
      content: userMessage
    };
    setMessages(prev => [...prev, newUserMessage]);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          session_id: sessionId
        })
      });

      const data = await response.json();

      if (data.session_id && !sessionId) {
        setSessionId(data.session_id);
        loadSessions();
      }

      const assistantMessage = {
        id: messages.length + 1,
        role: 'assistant',
        content: data.message
      };
      setMessages(prev => [...prev, assistantMessage]);

    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        id: messages.length + 1,
        role: 'assistant',
        content: 'Error al conectar con el servidor. Verifica que el backend esté corriendo.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatMessage = (content) => {
    return content.split('\n').map((line, i) => (
      <span key={i}>
        {line}
        {i < content.split('\n').length - 1 && <br />}
      </span>
    ));
  };

  return (
    <div className="app">

      {/* Sidebar */}
      <aside className={`sidebar ${showSidebar ? 'open' : ''}`}>
        <div className="sidebar-header">
          <div className="logo">
            <div className="logo-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
              </svg>
            </div>
            <span className="logo-text">ByteWise</span>
          </div>
          <button className="new-chat-btn" onClick={startNewSession}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 5v14M5 12h14" />
            </svg>
            Nueva Entrevista
          </button>
        </div>

        <div className="sessions-list">
          <h3 className="sessions-title">Historial</h3>
          {sessions.length === 0 ? (
            <p className="no-sessions">No hay sesiones previas</p>
          ) : (
            sessions.map((session) => (
              <div
                key={session.id}
                className={`session-item ${sessionId === session.id ? 'active' : ''}`}
                onClick={() => loadSession(session.id)}
              >
                <div className="session-info">
                  <span className="session-name">
                    {session.candidate_name || 'Entrevista'}
                  </span>
                  <span className="session-date">
                    {new Date(session.created_at).toLocaleDateString()}
                  </span>
                </div>
                <button
                  className="delete-btn"
                  onClick={(e) => deleteSession(session.id, e)}
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M18 6L6 18M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ))
          )}
        </div>

        <div className="sidebar-footer">
          <p className="version">v1.0.0 • Data Science Interview</p>
        </div>
      </aside>

      {/* Toggle sidebar button */}
      <button
        className="sidebar-toggle"
        onClick={() => setShowSidebar(!showSidebar)}
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          {showSidebar ? <path d="M15 18l-6-6 6-6" /> : <path d="M9 18l6-6-6-6" />}
        </svg>
      </button>

      {/* Main chat area */}
      <main className="chat-container">
        <div className="messages-area">
          {messages.length === 0 ? (
            <div className="welcome-screen">
              <div className="welcome-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M12 2l9 5v10l-9 5-9-5V7l9-5z" />
                  <circle cx="12" cy="12" r="3" />
                </svg>
              </div>
              <h1>Bienvenido a ByteWise</h1>
              <p className="welcome-subtitle">Tu entrevistador técnico de Data Science con IA</p>
              <div className="welcome-features">
                <div className="feature">
                  <div className="feature-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
                    </svg>
                  </div>
                  <span>Machine Learning</span>
                </div>
                <div className="feature">
                  <div className="feature-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z" />
                    </svg>
                  </div>
                  <span>Deep Learning</span>
                </div>
                <div className="feature">
                  <div className="feature-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <ellipse cx="12" cy="5" rx="9" ry="3" />
                      <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
                      <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
                    </svg>
                  </div>
                  <span>Data Engineering</span>
                </div>
                <div className="feature">
                  <div className="feature-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M18 20V10M12 20V4M6 20v-6" />
                    </svg>
                  </div>
                  <span>Estadística</span>
                </div>
              </div>
              <p className="welcome-hint">Preséntate para comenzar la entrevista</p>
            </div>
          ) : (
            <div className="messages-list">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`message ${message.role}`}
                >
                  <div className="message-avatar">
                    {message.role === 'user' ? (
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" />
                        <circle cx="12" cy="7" r="4" />
                      </svg>
                    ) : (
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
                      </svg>
                    )}
                  </div>
                  <div className="message-content">
                    <div className="message-header">
                      {message.role === 'user' ? 'Tú' : 'ByteWise'}
                    </div>
                    <div className="message-text">
                      {formatMessage(message.content)}
                    </div>
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="message assistant">
                  <div className="message-avatar">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
                    </svg>
                  </div>
                  <div className="message-content">
                    <div className="message-header">ByteWise</div>
                    <div className="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input area */}
        <form className="input-area" onSubmit={sendMessage}>
          <div className="input-wrapper">
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder={messages.length === 0 ? "Hola, me llamo..." : "Escribe tu respuesta..."}
              disabled={isLoading}
              autoFocus
            />
            <button
              type="submit"
              disabled={!inputValue.trim() || isLoading}
              className="send-btn"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M22 2L11 13M22 2L15 22L11 13M22 2L2 9L11 13" />
              </svg>
            </button>
          </div>
          <p className="input-hint">
            Presiona Enter para enviar
          </p>
        </form>
      </main>
    </div>
  );
}

export default App;
