import axios, { AxiosResponse } from 'axios';

// Create axios instance
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Types
export interface User {
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

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface AnalysisRequest {
  address?: string;
  latitude?: number;
  longitude?: number;
  property_type?: string;
  investment_budget?: number;
  investment_timeline?: string;
  risk_tolerance?: string;
}

export interface AnalysisResponse {
  id: number;
  location: {
    id: number;
    address: string;
    city: string;
    state: string;
    country: string;
    latitude: number;
    longitude: number;
  };
  overall_score: number;
  recommendation: 'buy' | 'hold' | 'avoid';
  confidence_level: number;
  scores: {
    facility_score: number;
    safety_score: number;
    disaster_risk_score: number;
    market_potential_score: number;
    accessibility_score: number;
  };
  predictions: {
    predicted_value_change_1y: number;
    predicted_value_change_3y: number;
    predicted_value_change_5y: number;
  };
  risk_factors: Array<{
    factor: string;
    severity: string;
    description: string;
    impact_score: number;
  }>;
  opportunities: Array<{
    opportunity: string;
    potential_impact: string;
    description: string;
    confidence: number;
  }>;
  nearby_facilities: Array<{
    type: string;
    name: string;
    distance: number;
    rating?: number;
    impact_on_score: number;
  }>;
  avg_price_per_sqft?: number;
  price_trend_6m?: number;
  price_trend_1y?: number;
  created_at: string;
  model_version: string;
}

export interface QuickAnalysisResponse {
  overall_score: number;
  recommendation: 'buy' | 'hold' | 'avoid';
  confidence_level: number;
  key_factors: string[];
  summary: string;
}

export interface DataUpdateStatus {
  data_type: string;
  last_update: string | null;
  next_update: string;
  status: string;
  records_count: number;
}

// Auth API
export const authAPI = {
  login: async (username: string, password: string): Promise<LoginResponse> => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    const response: AxiosResponse<LoginResponse> = await api.post('/auth/token', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  register: async (registrationData: {
    email: string;
    username: string;
    password: string;
    user_role?: 'buyer' | 'seller' | 'buyer_agent' | 'seller_agent';
    first_name?: string;
    last_name?: string;
    company_name?: string;
    license_number?: string;
  }): Promise<User> => {
    const response: AxiosResponse<User> = await api.post('/auth/register', {
      email: registrationData.email,
      username: registrationData.username,
      password: registrationData.password,
      user_role: registrationData.user_role || 'buyer',
      first_name: registrationData.first_name,
      last_name: registrationData.last_name,
      company_name: registrationData.company_name,
      license_number: registrationData.license_number,
    });
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response: AxiosResponse<User> = await api.get('/auth/me');
    return response.data;
  },

  updateProfile: async (email: string): Promise<User> => {
    const response: AxiosResponse<User> = await api.put('/auth/me', { email });
    return response.data;
  },

  changePassword: async (currentPassword: string, newPassword: string): Promise<void> => {
    await api.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
  },
};

// Analysis API
export const analysisAPI = {
  analyze: async (request: AnalysisRequest): Promise<AnalysisResponse> => {
    const response: AxiosResponse<AnalysisResponse> = await api.post('/analysis/analyze', request);
    return response.data;
  },

  quickAnalyze: async (request: AnalysisRequest): Promise<QuickAnalysisResponse> => {
    const response: AxiosResponse<QuickAnalysisResponse> = await api.post('/analysis/quick-analyze', request);
    return response.data;
  },

  getHistory: async (skip = 0, limit = 20): Promise<AnalysisResponse[]> => {
    const response: AxiosResponse<AnalysisResponse[]> = await api.get('/analysis/history', {
      params: { skip, limit },
    });
    return response.data;
  },

  getAnalysis: async (id: number): Promise<AnalysisResponse> => {
    const response: AxiosResponse<AnalysisResponse> = await api.get(`/analysis/analysis/${id}`);
    return response.data;
  },

  deleteAnalysis: async (id: number): Promise<void> => {
    await api.delete(`/analysis/analysis/${id}`);
  },

  compareLocations: async (locationIds: number[]): Promise<any> => {
    const response = await api.get('/analysis/compare', {
      params: { location_ids: locationIds },
    });
    return response.data;
  },

  getRecommendations: async (params: {
    budget_min?: number;
    budget_max?: number;
    property_type?: string;
    min_score?: number;
  }): Promise<any[]> => {
    const response = await api.get('/analysis/recommendations', { params });
    return response.data;
  },
};

// Data Collection API
export const dataAPI = {
  getDataStatus: async (): Promise<DataUpdateStatus[]> => {
    const response: AxiosResponse<DataUpdateStatus[]> = await api.get('/data/status');
    return response.data;
  },

  triggerUpdate: async (dataType: string): Promise<void> => {
    await api.post(`/data/update-${dataType}`);
  },

  triggerFullUpdate: async (): Promise<void> => {
    await api.post('/data/update-all');
  },

  getUpdateLogs: async (dataType?: string, limit = 50): Promise<any[]> => {
    const response = await api.get('/data/logs', {
      params: { data_type: dataType, limit },
    });
    return response.data;
  },

  validateAPIs: async (): Promise<Record<string, boolean>> => {
    const response = await api.post('/data/validate-apis');
    return response.data;
  },

  getStatistics: async (): Promise<any> => {
    const response = await api.get('/data/statistics');
    return response.data;
  },

  refreshLocationData: async (locationId: number): Promise<void> => {
    await api.post(`/data/location/${locationId}/refresh`);
  },
};

// Utility functions
export const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
};

export const formatPercentage = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'percent',
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  }).format(value);
};

export const formatDate = (dateString: string): string => {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(dateString));
};

export const getScoreColor = (score: number): string => {
  if (score >= 80) return '#4caf50'; // Green
  if (score >= 60) return '#ff9800'; // Orange
  if (score >= 40) return '#f44336'; // Red
  return '#9e9e9e'; // Gray
};

export const getRecommendationColor = (recommendation: string): string => {
  switch (recommendation.toLowerCase()) {
    case 'buy':
      return '#4caf50';
    case 'hold':
      return '#ff9800';
    case 'avoid':
      return '#f44336';
    default:
      return '#9e9e9e';
  }
};

export default api;