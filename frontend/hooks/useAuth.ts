import { useCallback, useEffect, useState } from 'react';
import { api } from '@/lib/api';

interface User {
  username: string;
  [key: string]: any;
}

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  // Fetch current user
  const fetchUser = useCallback(async () => {
    try {
      setLoading(true);
      const userData = await api.getCurrentUser();
      setUser(userData);
      setError(null);
    } catch (err) {
      setUser(null);
      setError(err instanceof Error ? err : new Error('Failed to fetch user'));
    } finally {
      setLoading(false);
    }
  }, []);

  // Login
  const login = useCallback(async (username: string, password: string) => {
    try {
      setLoading(true);
      await api.login(username, password);
      await fetchUser();
      return true;
    } catch (err) {
      setUser(null);
      setError(err instanceof Error ? err : new Error('Login failed'));
      return false;
    } finally {
      setLoading(false);
    }
  }, [fetchUser]);

  // Logout
  const logout = useCallback(() => {
    api.logout();
    setUser(null);
  }, []);

  // Check if user is authenticated on mount
  useEffect(() => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    
    if (token) {
      fetchUser();
    } else {
      setLoading(false);
    }
  }, [fetchUser]);

  return {
    user,
    loading,
    error,
    login,
    logout,
    isAuthenticated: !!user,
  };
} 