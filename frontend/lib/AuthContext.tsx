import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, login as apiLogin, register as apiRegister, getCurrentUser, logout as apiLogout, setAuthToken, LoginCredentials, RegisterData } from '@/lib/api';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Check if user is already logged in on mount
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('authToken');
      if (token) {
        try {
          const currentUser = await getCurrentUser();
          setUser(currentUser);
        } catch (error) {
          // Token is invalid, clear it
          localStorage.removeItem('authToken');
          setAuthToken(null);
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (credentials: LoginCredentials) => {
    try {
      const tokenResponse = await apiLogin(credentials);
      setAuthToken(tokenResponse.access_token);
      
      // Fetch user data
      const currentUser = await getCurrentUser();
      setUser(currentUser);
    } catch (error) {
      throw error;
    }
  };

  const register = async (data: RegisterData) => {
    try {
      await apiRegister(data);
      // After registration, automatically log in
      await login({ email: data.email, password: data.password });
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    apiLogout();
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        register,
        logout,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
