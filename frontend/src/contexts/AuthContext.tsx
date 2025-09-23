import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { toast } from 'react-toastify';
import { authAPI } from '../services/api';

interface User {
  id: number;
  email: string;
  username: string;
  user_role: 'buyer' | 'seller' | 'buyer_agent' | 'seller_agent';
  first_name?: string;
  last_name?: string;
  phone?: string;
  company_name?: string;
  license_number?: string;
  bio?: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
  subscription_plan: 'free' | 'basic' | 'pro' | 'premium';
  subscription_expires_at?: string;
  profile_image_url?: string;
  commission_rate?: number;
  years_experience?: number;
  specializations?: string[];
  service_areas?: string[];
  subscription_status: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<boolean>;
  register: (registrationData: {
    email: string;
    username: string;
    password: string;
    user_role?: 'buyer' | 'seller' | 'buyer_agent' | 'seller_agent';
    first_name?: string;
    last_name?: string;
    company_name?: string;
    license_number?: string;
  }) => Promise<boolean>;
  logout: () => void;
  updateUser: (userData: Partial<User>) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Check if user is logged in on app start
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const userData = await authAPI.getCurrentUser();
          setUser(userData);
        } catch (error) {
          // Token is invalid, remove it
          localStorage.removeItem('access_token');
          console.error('Auth check failed:', error);
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, []);

  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      setLoading(true);
      const response = await authAPI.login(username, password);
      
      // Store token
      localStorage.setItem('access_token', response.access_token);
      
      // Get user data
      const userData = await authAPI.getCurrentUser();
      setUser(userData);
      
      toast.success('Login successful!');
      return true;
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Login failed';
      toast.error(message);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const register = async (registrationData: {
    email: string;
    username: string;
    password: string;
    user_role?: 'buyer' | 'seller' | 'buyer_agent' | 'seller_agent';
    first_name?: string;
    last_name?: string;
    company_name?: string;
    license_number?: string;
  }): Promise<boolean> => {
    try {
      setLoading(true);
      await authAPI.register(registrationData);

      // Auto-login after registration
      const loginSuccess = await login(registrationData.username, registrationData.password);

      if (loginSuccess) {
        toast.success('Registration successful! Welcome!');
      }

      return loginSuccess;
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Registration failed';
      toast.error(message);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    setUser(null);
    toast.info('Logged out successfully');
  };

  const updateUser = (userData: Partial<User>) => {
    if (user) {
      setUser({ ...user, ...userData });
    }
  };

  const value: AuthContextType = {
    user,
    loading,
    login,
    register,
    logout,
    updateUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};