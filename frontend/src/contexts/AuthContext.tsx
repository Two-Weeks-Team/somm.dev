"use client";

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  ReactNode,
} from "react";

interface User {
  id: string;
  github_id: string;
  username: string;
  email?: string;
  avatar_url?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
  error: string | null;
  showReAuthModal: boolean;
  onAuthError: () => void;
  closeReAuthModal: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const TOKEN_KEY = "somm_auth_token";

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showReAuthModal, setShowReAuthModal] = useState(false);

  const isAuthenticated = !!user && !!token;

  const onAuthError = useCallback(() => {
    logout();
    setShowReAuthModal(true);
  }, []);

  const closeReAuthModal = useCallback(() => {
    setShowReAuthModal(false);
  }, []);

  const validateToken = useCallback(async (authToken: string): Promise<User | null> => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/me`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          return null;
        }
        throw new Error("Failed to validate token");
      }

      const userData = await response.json();
      return userData as User;
    } catch (err) {
      console.error("Token validation error:", err);
      return null;
    }
  }, []);

  const loadToken = useCallback(async () => {
    try {
      const storedToken = localStorage.getItem(TOKEN_KEY);
      if (storedToken) {
        const userData = await validateToken(storedToken);
        if (userData) {
          setToken(storedToken);
          setUser(userData);
        } else {
          localStorage.removeItem(TOKEN_KEY);
        }
      }
    } catch (err) {
      console.error("Error loading token:", err);
    } finally {
      setIsLoading(false);
    }
  }, [validateToken]);

  useEffect(() => {
    loadToken();
  }, [loadToken]);

  const login = async (newToken: string) => {
    try {
      setError(null);
      const userData = await validateToken(newToken);

      if (!userData) {
        throw new Error("Invalid token");
      }

      localStorage.setItem(TOKEN_KEY, newToken);
      setToken(newToken);
      setUser(userData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
      throw err;
    }
  };

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setUser(null);
    setError(null);
    setShowReAuthModal(false);
  }, []);

  const refreshToken = async () => {
    try {
      if (!token) {
        throw new Error("No token to refresh");
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/refresh`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to refresh token");
      }

      const data = await response.json();
      const newToken = data.access_token;

      localStorage.setItem(TOKEN_KEY, newToken);
      setToken(newToken);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Token refresh failed");
      logout();
      throw err;
    }
  };

  const value: AuthContextType = {
    user,
    token,
    isAuthenticated,
    isLoading,
    login,
    logout,
    refreshToken,
    error,
    showReAuthModal,
    onAuthError,
    closeReAuthModal,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
