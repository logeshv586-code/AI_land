import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import EnhancedBuyerDashboard from './EnhancedBuyerDashboard';
import EnhancedSellerDashboard from './EnhancedSellerDashboard';
import EnhancedBuyerAgentDashboard from './EnhancedBuyerAgentDashboard';
import EnhancedSellerAgentDashboard from './EnhancedSellerAgentDashboard';
import LoadingSpinner from '../components/Common/LoadingSpinner';

const DashboardPage: React.FC = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return <LoadingSpinner message="Loading dashboard..." />;
  }

  if (!user) {
    return <LoadingSpinner message="Loading user data..." />;
  }

  // Route to appropriate dashboard based on user role
  switch (user.user_role) {
    case 'buyer':
      return <EnhancedBuyerDashboard />;
    case 'seller':
      return <EnhancedSellerDashboard />;
    case 'buyer_agent':
      return <EnhancedBuyerAgentDashboard />;
    case 'seller_agent':
      return <EnhancedSellerAgentDashboard />;
    default:
      return <EnhancedBuyerDashboard />; // Default fallback
  }
};

export default DashboardPage;