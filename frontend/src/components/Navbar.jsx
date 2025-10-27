// src/components/Navbar.jsx
import React, { useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

const Navbar = () => {
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="bg-blue-600 text-white p-4">
      <div className="container mx-auto flex justify-between items-center">
        <Link to="/" className="text-xl font-bold">GenAI Healthcare Assistant</Link>
        <div className="space-x-4">
          <Link to="/" className="hover:underline">Home</Link>
          {!user && (
            <>
              <Link to="/login" className="hover:underline">Login</Link>
              <Link to="/register" className="hover:underline">Register</Link>
            </>
          )}
          {/* Always show Chat; redirect to login if the user isn't authenticated */}
          {user ? (
            <>
              <Link to="/profile" className="hover:underline">Profile</Link>
              <Link to="/chat" className="hover:underline">Chat</Link>
              {/* REMOVED: Quiz & Puzzles Link */}
              <button onClick={handleLogout} className="ml-2 underline">Logout</button>
            </>
          ) : (
            <button
              onClick={() => navigate('/login?next=/chat')}
              className="hover:underline bg-transparent border-0 p-0"
            >
              Chat
            </button>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;