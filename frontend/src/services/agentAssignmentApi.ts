import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with interceptors
const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

// Add token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface AgentInfo {
  id: number;
  name: string;
  company_name?: string;
  phone?: string;
  email: string;
}

export interface AgentAssignmentInfo {
  user_role: string;
  user_id: number;
  assigned_buyer_agent_id?: number;
  assigned_seller_agent_id?: number;
  assigned_buyer_agent?: AgentInfo;
  assigned_seller_agent?: AgentInfo;
  clients?: {
    id: number;
    name: string;
    role: string;
    email: string;
    phone?: string;
  }[];
}

export interface CommunicationRouting {
  can_communicate_directly: boolean;
  communication_path: number[];
  recipient: {
    id: number;
    name: string;
    role: string;
  };
  suggested_action?: {
    message: string;
    next_recipient: {
      id: number;
      name: string;
      role: string;
      is_agent: boolean;
    };
  };
}

class AgentAssignmentApiService {
  // Get available buyer agents
  async getAvailableBuyerAgents(locationArea?: string) {
    try {
      const response = await apiClient.get('/api/v1/auth/agents/buyer-agents', {
        params: locationArea ? { location_area: locationArea } : {}
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching buyer agents:', error);
      throw error;
    }
  }

  // Get available seller agents
  async getAvailableSellerAgents(locationArea?: string) {
    try {
      const response = await apiClient.get('/api/v1/auth/agents/seller-agents', {
        params: locationArea ? { location_area: locationArea } : {}
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching seller agents:', error);
      throw error;
    }
  }

  // Get current user's agent assignment information
  async getAgentAssignmentInfo(): Promise<AgentAssignmentInfo> {
    try {
      const response = await apiClient.get('/api/v1/messages/agent-info');
      return response.data;
    } catch (error) {
      console.error('Error fetching agent assignment info:', error);
      throw error;
    }
  }

  // Get communication routing information
  async getMessageRouting(recipientId: number): Promise<CommunicationRouting> {
    try {
      const response = await apiClient.post(`/api/v1/messages/route-message`, null, {
        params: { recipient_id: recipientId }
      });
      return response.data;
    } catch (error) {
      console.error('Error getting message routing:', error);
      throw error;
    }
  }

  // Check if communication is allowed
  async checkCommunicationPermission(userId: number) {
    try {
      const response = await apiClient.get(`/api/v1/auth/can-communicate/${userId}`);
      return response.data;
    } catch (error) {
      console.error('Error checking communication permission:', error);
      throw error;
    }
  }

  // Get clients for current agent
  async getMyClients() {
    try {
      const response = await apiClient.get('/api/v1/auth/my-clients');
      return response.data;
    } catch (error) {
      console.error('Error fetching clients:', error);
      throw error;
    }
  }

  // Assign buyer agent
  async assignBuyerAgent(buyerId: number, agentId?: number, locationArea?: string) {
    try {
      const response = await apiClient.post(`/api/v1/auth/assign-buyer-agent/${buyerId}`, {
        agent_id: agentId,
        location_area: locationArea
      });
      return response.data;
    } catch (error) {
      console.error('Error assigning buyer agent:', error);
      throw error;
    }
  }

  // Assign seller agent
  async assignSellerAgent(sellerId: number, agentId?: number, locationArea?: string) {
    try {
      const response = await apiClient.post(`/api/v1/auth/assign-seller-agent/${sellerId}`, {
        agent_id: agentId,
        location_area: locationArea
      });
      return response.data;
    } catch (error) {
      console.error('Error assigning seller agent:', error);
      throw error;
    }
  }

  // Get communication guidelines
  async getCommunicationGuidelines() {
    try {
      const response = await apiClient.get('/api/v1/messages/communication-guidelines');
      return response.data;
    } catch (error) {
      console.error('Error fetching communication guidelines:', error);
      throw error;
    }
  }
}

export const agentAssignmentApi = new AgentAssignmentApiService();