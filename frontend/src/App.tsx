import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box } from '@mui/material';

import { useAuth } from './contexts/AuthContext';
import Layout from './components/Layout/Layout';
import LoadingSpinner from './components/Common/LoadingSpinner';

// Pages
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import RoleSelectionPage from './pages/RoleSelectionPage';
import BuyerLoginPage from './pages/BuyerLoginPage';
import SellerLoginPage from './pages/SellerLoginPage';
import BuyerAgentLoginPage from './pages/BuyerAgentLoginPage';
import SellerAgentLoginPage from './pages/SellerAgentLoginPage';
import AnalysisPage from './pages/AnalysisPage';
import HistoryPage from './pages/HistoryPage';
import ComparePage from './pages/ComparePage';
import SettingsPage from './pages/SettingsPage';
import AdminPage from './pages/AdminPage';

// Automation Pages
import AutomationHubPage from './pages/AutomationHubPage';
import PropertyValuationPage from './pages/PropertyValuationPage';
import BeneficiaryScoringPage from './pages/BeneficiaryScoringPage';
import PropertyRecommendationsPage from './pages/PropertyRecommendationsPage';
import ComprehensiveAnalysisPage from './pages/ComprehensiveAnalysisPage';

// Property Pages
import PropertiesPage from './pages/PropertiesPage';
import PropertyDetailsPage from './pages/PropertyDetailsPage';

// Pricing and Messaging Pages
import SubscriptionPlansPage from './pages/SubscriptionPlansPage';
import MessagesPage from './pages/MessagesPage';

// Protected Route Component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <LoadingSpinner />;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

// Admin Route Component
const AdminRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <LoadingSpinner />;
  }

  if (!user || !user.is_admin) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
};

// Public Route Component (redirect to dashboard if logged in)
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <LoadingSpinner />;
  }

  if (user) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
};

function App() {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Routes>
        {/* Public Routes */}
        <Route
          path="/"
          element={
            <PublicRoute>
              <HomePage />
            </PublicRoute>
          }
        />
        <Route
          path="/login"
          element={
            <PublicRoute>
              <LoginPage />
            </PublicRoute>
          }
        />
        <Route
          path="/register"
          element={
            <PublicRoute>
              <RegisterPage />
            </PublicRoute>
          }
        />
        <Route
          path="/role-selection"
          element={
            <PublicRoute>
              <RoleSelectionPage />
            </PublicRoute>
          }
        />
        <Route
          path="/login/buyer"
          element={
            <PublicRoute>
              <BuyerLoginPage />
            </PublicRoute>
          }
        />
        <Route
          path="/login/seller"
          element={
            <PublicRoute>
              <SellerLoginPage />
            </PublicRoute>
          }
        />
        <Route
          path="/login/buyer-agent"
          element={
            <PublicRoute>
              <BuyerAgentLoginPage />
            </PublicRoute>
          }
        />
        <Route
          path="/login/seller-agent"
          element={
            <PublicRoute>
              <SellerAgentLoginPage />
            </PublicRoute>
          }
        />

        {/* Protected Routes */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Layout>
                <DashboardPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/analysis"
          element={
            <ProtectedRoute>
              <Layout>
                <AnalysisPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/analysis/:id"
          element={
            <ProtectedRoute>
              <Layout>
                <AnalysisPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/history"
          element={
            <ProtectedRoute>
              <Layout>
                <HistoryPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/compare"
          element={
            <ProtectedRoute>
              <Layout>
                <ComparePage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <Layout>
                <SettingsPage />
              </Layout>
            </ProtectedRoute>
          }
        />

        {/* Automation Routes */}
        <Route
          path="/automation"
          element={
            <ProtectedRoute>
              <Layout>
                <AutomationHubPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/automation/comprehensive"
          element={
            <ProtectedRoute>
              <Layout>
                <ComprehensiveAnalysisPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/automation/valuation"
          element={
            <ProtectedRoute>
              <Layout>
                <PropertyValuationPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/automation/scoring"
          element={
            <ProtectedRoute>
              <Layout>
                <BeneficiaryScoringPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/automation/recommendations"
          element={
            <ProtectedRoute>
              <Layout>
                <PropertyRecommendationsPage />
              </Layout>
            </ProtectedRoute>
          }
        />

        {/* Property Routes */}
        <Route
          path="/properties"
          element={
            <Layout>
              <PropertiesPage />
            </Layout>
          }
        />
        <Route
          path="/properties/:id"
          element={
            <Layout>
              <PropertyDetailsPage />
            </Layout>
          }
        />

        {/* Pricing Routes */}
        <Route
          path="/subscription"
          element={
            <SubscriptionPlansPage />
          }
        />
        <Route
          path="/pricing"
          element={
            <SubscriptionPlansPage />
          }
        />

        {/* Messaging Routes */}
        <Route
          path="/messages"
          element={
            <ProtectedRoute>
              <Layout>
                <MessagesPage />
              </Layout>
            </ProtectedRoute>
          }
        />

        {/* Admin Routes */}
        <Route
          path="/admin"
          element={
            <AdminRoute>
              <Layout>
                <AdminPage />
              </Layout>
            </AdminRoute>
          }
        />

        {/* Catch all route */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Box>
  );
}

export default App;