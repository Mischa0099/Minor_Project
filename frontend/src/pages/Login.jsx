// src/pages/Login.jsx
import React, { useState } from 'react';
import api from '../api';
import { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { useNavigate, useLocation } from 'react-router-dom';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const navigate = useNavigate();
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const next = params.get('next') || '/profile';
  const { login } = useContext(AuthContext);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
  const response = await api.post('/api/auth/login', { email, password });
  login(response.data.token);
  setMessage('Login successful!');
  navigate(next);
    } catch (error) {
      setMessage(error.friendlyMessage || error.response?.data?.message || 'Login failed');
    }
  };

  return (
    <div className="max-w-md mx-auto bg-white p-8 rounded-lg shadow-xl animate-subtle-pop">
      <h2 className="text-3xl font-bold mb-6 text-center text-blue-600">Login to Your Account</h2>
      <form onSubmit={handleSubmit}>
        <div className="mb-5">
          <label className="block text-gray-700 font-semibold mb-2" htmlFor="email">Email</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent transition duration-150"
            placeholder="your@email.com"
            required
          />
        </div>
        <div className="mb-6">
          <label className="block text-gray-700 font-semibold mb-2" htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent transition duration-150"
            placeholder="Enter your password"
            required
          />
        </div>
        <button type="submit" className="w-full btn btn-primary py-3 text-lg hover:shadow-md transition duration-200">
          Sign In
        </button>
      </form>
      {message && <p className={`mt-4 text-center p-2 rounded ${
        message.includes('successful') ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
      }`}>{message}</p>}
      <p className="mt-4 text-center text-sm text-gray-600">
        Don't have an account? <a href="/register" className="text-blue-600 hover:underline">Register here</a>
      </p>
    </div>
  );
};

export default Login;