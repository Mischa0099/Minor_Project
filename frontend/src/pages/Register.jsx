import React, { useState } from 'react';
import api from '../api';
import { useNavigate } from 'react-router-dom';

const Register = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validation
    if (password.length < 6) {
      setMessage('Password must be at least 6 characters long');
      return;
    }
    
    if (password !== confirmPassword) {
      setMessage('Passwords do not match');
      return;
    }
    
    setIsLoading(true);
    setMessage('');
    
    try {
      await api.post('/api/auth/register', { email, password });
      setMessage('Registration successful! Redirecting to login...');
      setTimeout(() => {
        navigate('/login');
      }, 1500);
    } catch (error) {
      setMessage(error.friendlyMessage || error.response?.data?.message || 'Registration failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto bg-white p-8 rounded-lg shadow-xl animate-subtle-pop">
      <h2 className="text-3xl font-bold mb-6 text-center text-blue-600">Create Account</h2>
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
        <div className="mb-5">
          <label className="block text-gray-700 font-semibold mb-2" htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent transition duration-150"
            placeholder="At least 6 characters"
            minLength={6}
            required
          />
        </div>
        <div className="mb-6">
          <label className="block text-gray-700 font-semibold mb-2" htmlFor="confirmPassword">Confirm Password</label>
          <input
            type="password"
            id="confirmPassword"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent transition duration-150"
            placeholder="Re-enter password"
            required
          />
        </div>
        <button 
          type="submit" 
          disabled={isLoading}
          className="w-full btn btn-primary py-3 text-lg hover:shadow-md transition duration-200 disabled:opacity-50"
        >
          {isLoading ? 'Creating Account...' : 'Register'}
        </button>
      </form>
      {message && (
        <p className={`mt-4 text-center p-2 rounded ${
          message.includes('successful') ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
        }`}>{message}</p>
      )}
      <p className="mt-4 text-center text-sm text-gray-600">
        Already have an account? <a href="/login" className="text-blue-600 hover:underline">Login here</a>
      </p>
    </div>
  );
};

export default Register;
