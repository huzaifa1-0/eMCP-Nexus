import { useState, useRef, useEffect } from 'react';
import { API_BASE_URL } from '../api/config';

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { text: 'Hello! I can help you find the perfect tool. What do you need?', sender: 'bot' },
  ]);
  const [input, setInput] = useState('');
  const messagesRef = useRef(null);

  useEffect(() => {
    if (messagesRef.current) {
      messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
    }
  }, [messages]);

  const sendMessage = async () => {
    const text = input.trim();
    if (!text) return;

    setMessages(prev => [...prev, { text, sender: 'user' }]);
    setInput('');

    setMessages(prev => [...prev, { text: 'Thinking...', sender: 'bot', id: 'loading' }]);

    try {
      const res = await fetch(`${API_BASE_URL}/chat/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      });
      const data = await res.json();
      const reply = data.response || data.reply || "I didn't get a response.";

      setMessages(prev => [
        ...prev.filter(m => m.id !== 'loading'),
        { text: reply, sender: 'bot' },
      ]);
    } catch {
      setMessages(prev =>
        prev.map(m => m.id === 'loading' ? { ...m, text: 'Error connecting to NexusAI.' } : m)
      );
    }
  };

  return (
    <div className="chat-widget">
      {isOpen && (
        <div className="chat-window">
          <div className="chat-header">
            <span>⚡ NexusAI Assistant</span>
            <button className="chat-close" onClick={() => setIsOpen(false)}>&times;</button>
          </div>

          <div className="chat-messages" ref={messagesRef}>
            {messages.map((m, i) => (
              <div key={i} className={`chat-bubble ${m.sender}`}>
                {m.text.split('\n').map((line, j) => (
                  <span key={j}>{line}{j < m.text.split('\n').length - 1 && <br />}</span>
                ))}
              </div>
            ))}
          </div>

          <div className="chat-input-area">
            <input
              className="chat-input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Ask me anything..."
            />
            <button className="chat-send" onClick={sendMessage}>
              <i className="fas fa-paper-plane"></i>
            </button>
          </div>
        </div>
      )}

      <button className="chat-toggle" onClick={() => setIsOpen(!isOpen)}>
        <i className="fas fa-robot"></i>
      </button>
    </div>
  );
}
