// src/pages/Home.jsx
import React, { useEffect, useState, useCallback } from 'react';
import api from '../api';

const Home = () => {
  const [adminMode, setAdminMode] = useState(false);
  const [adminKey, setAdminKey] = useState('');
  const [adminMsg, setAdminMsg] = useState('');
  const [loading, setLoading] = useState(false);
  const [chats, setChats] = useState([]);
  const [alerts, setAlerts] = useState([]);
  
  const reloadChats = useCallback(async () => {
    if (!adminMode) return;
    setLoading(true);
    try {
      const res = await api.get('/api/admin/recent_chats?limit=25', { headers: { 'X-ADMIN-KEY': adminKey } });
      setChats(res.data || []);
      const resAlerts = await api.get('/api/admin/alerts?limit=25', { headers: { 'X-ADMIN-KEY': adminKey } });
      setAlerts(resAlerts.data || []);
    } catch (err) {
      setAdminMsg(err.friendlyMessage || 'Failed to refresh.');
    }
    setLoading(false);
  }, [adminMode, adminKey]); // Dependencies added

  const tryUnlock = async (e) => {
    e.preventDefault();
    setLoading(true);
    setAdminMsg('');
    try {
      const res = await api.get('/api/admin/recent_chats?limit=25', { headers: { 'X-ADMIN-KEY': adminKey } });
      setChats(res.data || []);
      setAdminMode(true);
      setAdminMsg('');
    } catch (err) {
      setAdminMode(false);
      setAdminMsg(err.friendlyMessage || 'Unauthorized or failed to load.');
    }
    setLoading(false);
  };

  useEffect(() => {
    // optional: auto-refresh every 30s while unlocked
    if (!adminMode) return;
    // Call reloadChats here
    reloadChats();
    const t = setInterval(reloadChats, 30000);
    return () => clearInterval(t);
  }, [adminMode, adminKey, reloadChats]); // Dependency added

  return (
    <div className="text-center">
// ... (rest of the file remains the same)
      <h1 className="text-4xl font-bold mb-4">Welcome to GenAI Healthcare Assistant</h1>
      <p className="text-lg mb-6">
        This is a prototype healthcare web application using AI-powered sentiment analysis for well-being.
      </p>
      <p className="text-md text-gray-700 mb-8">
        Use the navigation bar to register, login, create your profile, and chat with the AI assistant.
      </p>

      <div className="max-w-4xl mx-auto text-left bg-white p-4 rounded shadow">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-xl font-semibold">Admin Panel (password protected)</h2>
          {adminMode ? (
            <button className="btn btn-secondary" onClick={() => { setAdminMode(false); setChats([]); }}>Lock</button>
          ) : null}
        </div>

        {!adminMode && (
          <form onSubmit={tryUnlock} className="mb-3">
            <label className="block mb-1">Enter Admin Password</label>
            <input
              type="password"
              className="w-full p-2 border rounded mb-2"
              placeholder="Password (default 123)"
              value={adminKey}
              onChange={(e) => setAdminKey(e.target.value)}
            />
            <button type="submit" className="btn btn-primary" disabled={loading}>{loading ? 'Checking…' : 'Unlock'}</button>
            {adminMsg && <div className="mt-2 text-sm text-red-600">{adminMsg}</div>}
          </form>
        )}

        {adminMode && (
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="text-sm text-gray-600">Showing last 25 chats with timestamps and sentiment</div>
              <button className="btn btn-secondary" onClick={reloadChats} disabled={loading}>{loading ? 'Refreshing…' : 'Refresh'}</button>
            </div>
            <div className="max-h-96 overflow-y-auto border p-2">
              {chats.length === 0 && (
                <div className="text-sm text-gray-600">No chats yet.</div>
              )}
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

            <div className="mt-6">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm text-gray-600">Recent Alerts</div>
              </div>
              <div className="max-h-64 overflow-y-auto border p-2">
                {alerts.length === 0 && (
                  <div className="text-sm text-gray-600">No alerts yet.</div>
                )}
                {alerts.map((a) => (
                  <div key={a.id} className="mb-3">
                    <div><strong>Type:</strong> {a.alert_type}</div>
                    <div className="text-xs text-gray-600 mt-1">
                      <div>User ID: {a.user_id}</div>
                      <div>Time: {a.created_at}</div>
                      <div>Message: {a.message}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Home;