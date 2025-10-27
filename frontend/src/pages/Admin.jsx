// src/pages/Admin.jsx
import React, { useEffect, useState, useCallback } from 'react';
import api from '../api';

const Admin = () => {
  const [templates, setTemplates] = useState({});
  const [chats, setChats] = useState([]);
  const [message, setMessage] = useState('');
  const [userFilter, setUserFilter] = useState('');
  const [adminKey, setAdminKey] = useState(localStorage.getItem('adminKey') || '');

  const loadTemplates = useCallback(async () => {
    try {
      const res = await api.get('/api/admin/templates', { headers: adminKey ? { 'X-ADMIN-KEY': adminKey } : {} });
      setTemplates(res.data);
    } catch (e) {
      setMessage(e.friendlyMessage || 'Failed to load templates');
    }
  }, [adminKey]);

  const saveTemplates = async () => {
    try {
      await api.put('/api/admin/templates', templates, { headers: adminKey ? { 'X-ADMIN-KEY': adminKey } : {} });
      setMessage('Templates saved');
    } catch (e) {
      setMessage(e.friendlyMessage || 'Failed to save templates');
    }
  };

  const loadChats = useCallback(async () => {
    try {
      const q = new URLSearchParams();
      q.set('limit', '50');
      if (userFilter) q.set('user_id', userFilter);
      const res = await api.get(`/api/admin/recent_chats?${q.toString()}`, { headers: adminKey ? { 'X-ADMIN-KEY': adminKey } : {} });
      setChats(res.data);
    } catch (e) {
      setMessage(e.friendlyMessage || 'Failed to load chats');
    }
  }, [adminKey, userFilter]);

  useEffect(() => {
    loadTemplates();
    loadChats();
  }, [loadTemplates, loadChats]); // Dependencies added

  return (
// ... (rest of the file remains the same)
    <div className="max-w-4xl mx-auto bg-white p-6 rounded shadow">
      <h2 className="text-2xl font-bold mb-4">Admin</h2>
      <div className="mb-4">
        <label className="block text-gray-700">Admin Key (for protected endpoints)</label>
        <input
          type="text"
          className="w-full p-2 border rounded mb-2"
          value={adminKey}
          onChange={(e) => setAdminKey(e.target.value)}
          placeholder="Paste ADMIN_KEY here"
        />
        <label className="block text-gray-700">Filter by User ID (optional)</label>
        <input
          type="text"
          className="w-full p-2 border rounded mb-2"
          value={userFilter}
          onChange={(e) => setUserFilter(e.target.value)}
          placeholder="Enter user id"
        />
        <div>
          <button
            className="bg-gray-600 text-white p-2 rounded mr-2"
            onClick={() => { localStorage.setItem('adminKey', adminKey); setMessage('Admin key saved locally'); }}
          >
            Save Key
          </button>
          <button
            className="bg-gray-400 text-black p-2 rounded"
            onClick={() => { localStorage.removeItem('adminKey'); setAdminKey(''); setMessage('Admin key cleared'); }}
          >
            Clear Key
          </button>
          <button
            className="bg-blue-600 text-white p-2 rounded ml-2"
            onClick={loadChats}
          >
            Load Chats
          </button>
        </div>
      </div>
      {message && <p className="mb-4">{message}</p>}
      <section className="mb-6">
        <h3 className="text-xl font-semibold mb-2">Response Templates</h3>
        <textarea
          rows={10}
          className="w-full p-2 border rounded"
          value={JSON.stringify(templates, null, 2)}
          onChange={(e) => {
            try {
              setTemplates(JSON.parse(e.target.value));
            } catch (ex) {
              setMessage('Invalid JSON');
            }
          }}
        />
        <div className="mt-2">
          <button onClick={saveTemplates} className="bg-blue-600 text-white p-2 rounded">Save Templates</button>
        </div>
      </section>

      <section>
        <h3 className="text-xl font-semibold mb-2">Recent Chats</h3>
        <div className="max-h-96 overflow-y-auto border p-2">
          {chats.map((c) => (
            <div key={c.id || c._id} className="mb-4">
              <div><strong>User:</strong> {c.user_message}</div>
              <div><strong>AI:</strong> {c.ai_response}</div>
              <div className="text-xs text-gray-600 mt-1">
                <div>Time: {c.created_at}</div>
                <div>Sentiment: {c.sentiment_label} ({Math.round(Number(c.sentiment_score || 0))}%)</div>
                <div>User ID: {c.user_id}</div>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default Admin;