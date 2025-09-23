import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { agentAssignmentApi, AgentAssignmentInfo, CommunicationRouting } from '../services/agentAssignmentApi';

export const useAgentAssignment = () => {
  const { user } = useAuth();
  const [agentInfo, setAgentInfo] = useState<AgentAssignmentInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAgentInfo = async () => {
    if (!user) return;

    setLoading(true);
    setError(null);
    
    try {
      const info = await agentAssignmentApi.getAgentAssignmentInfo();
      setAgentInfo(info);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch agent information');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user) {
      fetchAgentInfo();
    }
  }, [user]);

  const getMessageRouting = async (recipientId: number): Promise<CommunicationRouting | null> => {
    try {
      return await agentAssignmentApi.getMessageRouting(recipientId);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to get message routing');
      return null;
    }
  };

  const checkCommunicationPermission = async (userId: number) => {
    try {
      return await agentAssignmentApi.checkCommunicationPermission(userId);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to check communication permission');
      return null;
    }
  };

  const hasAssignedBuyerAgent = () => {
    return user?.user_role === 'buyer' && agentInfo?.assigned_buyer_agent_id;
  };

  const hasAssignedSellerAgent = () => {
    return user?.user_role === 'seller' && agentInfo?.assigned_seller_agent_id;
  };

  const getAssignedAgent = () => {
    if (user?.user_role === 'buyer') {
      return agentInfo?.assigned_buyer_agent;
    }
    if (user?.user_role === 'seller') {
      return agentInfo?.assigned_seller_agent;
    }
    return null;
  };

  const canContactDirectly = (targetUserRole: string) => {
    if (!user) return false;

    // Agents can contact anyone
    if (user.user_role === 'buyer_agent' || user.user_role === 'seller_agent') {
      return true;
    }

    // Buyers can contact seller agents directly
    if (user.user_role === 'buyer' && targetUserRole === 'seller_agent') {
      return true;
    }

    // Sellers cannot contact anyone directly
    if (user.user_role === 'seller') {
      return false;
    }

    return false;
  };

  const getCommunicationGuidelines = () => {
    if (!user) return [];

    switch (user.user_role) {
      case 'buyer':
        return [
          'You can browse properties and contact seller agents directly',
          'For negotiations and offers, work with your assigned buyer agent',
          'Direct communication with sellers is not allowed'
        ];
      case 'seller':
        return [
          'All communications with buyers must go through your assigned seller agent',
          'Your seller agent will handle inquiries and negotiations',
          'Direct communication with buyers is not allowed'
        ];
      case 'buyer_agent':
        return [
          'You can communicate with seller agents and your buyer clients',
          'Help your clients with property searches and negotiations',
          'Represent buyers in all communications'
        ];
      case 'seller_agent':
        return [
          'You can communicate with buyer agents and your seller clients',
          'Handle property inquiries and represent sellers',
          'Facilitate communication between buyers and sellers'
        ];
      default:
        return [];
    }
  };

  return {
    agentInfo,
    loading,
    error,
    fetchAgentInfo,
    getMessageRouting,
    checkCommunicationPermission,
    hasAssignedBuyerAgent,
    hasAssignedSellerAgent,
    getAssignedAgent,
    canContactDirectly,
    getCommunicationGuidelines,
  };
};