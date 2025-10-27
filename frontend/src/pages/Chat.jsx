import React, { useState, useRef, useEffect } from 'react';
import api from '../api';

const Chat = () => {
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [isSending, setIsSending] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);

  const getSentimentStyle = (label) => {
    switch (label.toLowerCase()) {
      case 'positive':
        return { color: 'green', fontWeight: 'bold' };
      case 'negative':
        return { color: 'red', fontWeight: 'bold' };
      case 'neutral':
        return { color: 'orange', fontWeight: 'bold' };
      default:
        return {};
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!message.trim()) return;
    setIsSending(true);

    try {
      const response = await api.post('/api/chat/', { message });
      const { ai_response, created_at } = response.data;
      setChatHistory((h) => [...h, { user: message, ai: ai_response, created_at }]);
      setMessage('');
    } catch (error) {
      console.error(error);
      alert(error.response?.data?.message || 'Failed to send message');
    }
    setIsSending(false);
  };

  const messagesRef = useRef(null);
  useEffect(() => {
    // load recent history on mount
    (async () => {
      try {
        const res = await api.get('/api/chat/history?limit=50');
        const items = Array.isArray(res.data) ? res.data : [];
        setChatHistory(items.map((it) => ({ user: it.user, ai: it.ai, created_at: it.created_at })));
      } catch (e) {
        console.warn('Failed to load chat history', e.friendlyMessage || e.message);
      } finally {
        setIsLoadingHistory(false);
      }
    })();
  }, []);

  useEffect(() => {
    if (messagesRef.current) messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
  }, [chatHistory]);

  return (
    <div className="max-w-2xl mx-auto bg-white p-6 rounded shadow">
      <h2 className="text-2xl font-bold mb-4">Chat with AI Assistant</h2>
      <div ref={messagesRef} className="mb-4 h-64 overflow-y-auto border p-4">
        {isLoadingHistory && (
          <div className="text-sm text-gray-500 animate-pulse">Loading your recent messages…</div>
        )}
        {chatHistory.map((chat, index) => (
          <div key={index} className="mb-3">
            <div className="flex justify-end">
              <div className="max-w-[80%] rounded-lg px-3 py-2 bg-blue-600 text-white shadow transition-transform transform hover:scale-[1.01]">
                {chat.user}
              </div>
            </div>
            <div className="mt-1 flex justify-start items-start gap-2">
              <div className="w-6 h-6 rounded-full bg-gray-300 flex items-center justify-center text-xs">AI</div>
              <div className="max-w-[80%] rounded-lg px-3 py-2 bg-gray-100 text-gray-900 shadow">
                {chat.ai}
                {chat.created_at && (
                  <div className="mt-1 text-xs text-gray-500">{new Date(chat.created_at).toLocaleString()}</div>
                )}
              </div>
            </div>
          </div>
        ))}
        {isSending && (
          <div className="mt-2 flex justify-start items-center gap-2">
            <div className="w-6 h-6 rounded-full bg-gray-300 flex items-center justify-center text-xs">AI</div>
            <div className="px-3 py-2 bg-gray-100 rounded-lg text-gray-600 text-sm">
              <span className="inline-block animate-pulse">Typing…</span>
            </div>
          </div>
        )}
      </div>
      <form onSubmit={handleSubmit}>
        <div className="flex">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            className="flex-1 p-2 border rounded-l"
            placeholder="Type your message..."
          />
          <button type="submit" disabled={isSending} className="btn btn-primary rounded-r">{isSending ? 'Sending...' : 'Send'}</button>
        </div>
      </form>
    </div>
  );
};

export default Chat;
