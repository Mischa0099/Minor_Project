import React, { useContext } from 'react';
import { Navigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

const ProtectedRoute = ({ children }) => {
  const { user } = useContext(AuthContext);
  
  if (!user) {
    // Redirect to login with return URL
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

export default ProtectedRoute;

