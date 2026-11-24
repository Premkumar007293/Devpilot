import React, { useEffect } from 'react';
import { Navigate, useSearchParams } from 'react-router-dom';
import { setStoredAuthToken } from '../services/api';

export const AuthCallbackPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');

  useEffect(() => {
    if (token) {
      setStoredAuthToken(token);
    }
  }, [token]);

  if (!token) {
    return <Navigate to="/" replace />;
  }

  return <Navigate to="/repositories" replace />;
};
