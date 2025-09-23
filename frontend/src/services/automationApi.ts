import axios from 'axios';

// Base API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const automationApi = axios.create({
  baseURL: `${API_BASE_URL}/api/v1/automation`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests if available
automationApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
automationApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Types
export interface PropertyDetails {
  address: string;
  latitude?: number;
  longitude?: number;
  property_type: string;
  beds: number;
  baths: number;
  sqft: number;
  year_built: number;
  lot_size?: number;
}

export interface CustomWeights {
  value: number;
  school: number;
  crime_inv: number;
  env_inv: number;
  employer_proximity: number;
}

export interface PropertyValuationRequest {
  property_details: PropertyDetails;
}

export interface PropertyValuationResponse {
  id: number;
  predicted_value: number;
  value_uncertainty: number;
  price_per_sqft: number;
  comparable_sales_count: number;
  days_on_market_avg: number;
  valuation_date: string;
  confidence_score: number;
  explanation?: {
    base_value: number;
    prediction_value: number;
    top_positive_features: Array<{
      feature_name: string;
      attribution_value: number;
      feature_value: number;
      impact_description: string;
    }>;
    top_negative_features: Array<{
      feature_name: string;
      attribution_value: number;
      feature_value: number;
      impact_description: string;
    }>;
  };
}

export interface BeneficiaryScoringRequest {
  location_id?: number;
  property_valuation_id?: number;
  address: string;
  latitude?: number;
  longitude?: number;
  custom_weights: CustomWeights;
}

export interface BeneficiaryScoringResponse {
  id: number;
  overall_score: number;
  value_score: number;
  school_score: number;
  safety_score: number;
  environmental_score: number;
  accessibility_score: number;
  scoring_weights: CustomWeights;
  score_components: {
    value: number;
    school: number;
    crime: number;
    env: number;
    employer: number;
  };
  calculated_at: string;
  model_version: string;
  explanation?: {
    overall_score: number;
    component_explanations: Array<{
      component: string;
      raw_score: number;
      weight: number;
      weighted_contribution: number;
      description: string;
    }>;
  };
}

export interface PropertyRecommendationRequest {
  search_type: 'location' | 'property';
  property_id?: number;
  location?: {
    lat: number;
    lon: number;
  };
  address?: string;
  radius_km?: number;
  max_recommendations: number;
  recommendation_type: 'content_based' | 'collaborative' | 'hybrid';
  user_preferences?: {
    min_beds?: number;
    max_beds?: number;
    min_baths?: number;
    max_baths?: number;
    min_price?: number;
    max_price?: number;
    property_type?: string;
    min_sqft?: number;
    max_sqft?: number;
  };
}

export interface PropertyRecommendationResponse {
  id: number;
  recommended_property: {
    id: number;
    predicted_value: number;
    beds: number;
    baths: number;
    sqft: number;
    year_built: number;
    address: string;
    property_type: string;
  };
  recommendation_type: string;
  similarity_score: number;
  confidence_score: number;
  rank_position: number;
  recommendation_reason: string;
  created_at: string;
}

export interface ComprehensiveAnalysisRequest {
  property_details: PropertyDetails;
  custom_weights?: CustomWeights;
  max_recommendations?: number;
  recommendation_type?: 'content_based' | 'collaborative' | 'hybrid';
}

export interface ComprehensiveAnalysisResponse {
  property_valuation: PropertyValuationResponse;
  beneficiary_score: BeneficiaryScoringResponse;
  recommendations: PropertyRecommendationResponse[];
  risk_assessment: {
    risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
    risk_factors: string[];
    opportunities: string[];
    confidence_score: number;
  };
  analysis_summary: {
    total_processing_time: number;
    model_versions: {
      avm: string;
      scoring: string;
      recommendations: string;
    };
    data_sources_used: string[];
  };
}

// API Service Functions
export const automationApiService = {
  // Property Valuation
  async getPropertyValuation(request: PropertyValuationRequest): Promise<PropertyValuationResponse> {
    const response = await automationApi.post('/property-valuation', request);
    return response.data;
  },

  // Beneficiary Scoring
  async getBeneficiaryScore(request: BeneficiaryScoringRequest): Promise<BeneficiaryScoringResponse> {
    const response = await automationApi.post('/beneficiary-score', request);
    return response.data;
  },

  // Property Recommendations
  async getPropertyRecommendations(request: PropertyRecommendationRequest): Promise<PropertyRecommendationResponse[]> {
    const response = await automationApi.post('/recommendations', request);
    return response.data;
  },

  // Comprehensive Analysis
  async getComprehensiveAnalysis(request: ComprehensiveAnalysisRequest): Promise<ComprehensiveAnalysisResponse> {
    const response = await automationApi.post('/comprehensive-analysis', request);
    return response.data;
  },

  // Get SHAP Explanation
  async getShapExplanation(analysisType: string, analysisId: number): Promise<any> {
    const response = await automationApi.get(`/shap-explanation/${analysisType}/${analysisId}`);
    return response.data;
  },

  // Health Check
  async healthCheck(): Promise<{ status: string; service: string }> {
    const response = await automationApi.get('/health');
    return response.data;
  },

  // Get Analysis History
  async getAnalysisHistory(userId?: number, limit: number = 50): Promise<any[]> {
    const params = new URLSearchParams();
    if (userId) params.append('user_id', userId.toString());
    params.append('limit', limit.toString());
    
    const response = await automationApi.get(`/history?${params.toString()}`);
    return response.data;
  },

  // Log User Interaction
  async logUserInteraction(interactionData: {
    user_id?: number;
    property_id?: number;
    interaction_type: string;
    interaction_data: any;
  }): Promise<void> {
    await automationApi.post('/log-interaction', interactionData);
  },
};

export default automationApiService;
