import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  Avatar,
  LinearProgress,
  Alert,
  Divider,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  AutoAwesome,
  TrendingUp,
  Assessment,
  Recommend,
  Speed,
  Psychology,
  Security,
  Analytics,
  LocationOn,
  Home,
  AttachMoney,
  School,
  LocalPolice,
  Park,
  DirectionsCar,
  PlayArrow,
  Info,
  Timeline,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

const AutomationHubPage: React.FC = () => {
  const navigate = useNavigate();
  const [selectedFeature, setSelectedFeature] = useState<string | null>(null);

  const automationFeatures = [
    {
      id: 'comprehensive',
      title: 'Comprehensive Analysis',
      description: 'Complete property analysis combining AVM, beneficiary scoring, and recommendations',
      icon: <AutoAwesome sx={{ fontSize: 40 }} />,
      color: '#2563eb',
      route: '/automation/comprehensive',
      features: ['Property Valuation', 'Investment Scoring', 'Risk Assessment', 'AI Explanations'],
      processingTime: '< 2 seconds',
      accuracy: '85%+',
    },
    {
      id: 'valuation',
      title: 'Property Valuation (AVM)',
      description: 'AI-powered automated valuation model with uncertainty estimation',
      icon: <AttachMoney sx={{ fontSize: 40 }} />,
      color: '#10b981',
      route: '/automation/valuation',
      features: ['RandomForest ML', 'Uncertainty Estimation', 'Market Comparables', 'Price Trends'],
      processingTime: '< 1 second',
      accuracy: '90%+',
    },
    {
      id: 'scoring',
      title: 'Beneficiary Scoring',
      description: 'Multi-factor investment attractiveness scoring with custom weights',
      icon: <Assessment sx={{ fontSize: 40 }} />,
      color: '#f59e0b',
      route: '/automation/scoring',
      features: ['Custom Weights', 'Component Breakdown', 'Risk Factors', 'Opportunities'],
      processingTime: '< 1 second',
      accuracy: '88%+',
    },
    {
      id: 'recommendations',
      title: 'Property Recommendations',
      description: 'Hybrid ML-powered property recommendations and similarity analysis',
      icon: <Recommend sx={{ fontSize: 40 }} />,
      color: '#8b5cf6',
      route: '/automation/recommendations',
      features: ['Content-Based', 'Collaborative Filtering', 'Similarity Scoring', 'Personalized'],
      processingTime: '< 3 seconds',
      accuracy: '82%+',
    },
  ];

  const systemStats = [
    { label: 'Properties Analyzed', value: '12,847', icon: <Home /> },
    { label: 'Avg Processing Time', value: '1.8s', icon: <Speed /> },
    { label: 'Model Accuracy', value: '87.3%', icon: <Psychology /> },
    { label: 'Active Users', value: '1,234', icon: <Security /> },
  ];

  const recentAnalyses = [
    {
      id: 1,
      address: '123 Main St, Chicago, IL',
      value: '$275,000',
      score: 78.5,
      recommendation: 'BUY',
      timestamp: '2 minutes ago',
    },
    {
      id: 2,
      address: '456 Oak Ave, Austin, TX',
      value: '$420,000',
      score: 65.2,
      recommendation: 'HOLD',
      timestamp: '15 minutes ago',
    },
    {
      id: 3,
      address: '789 Pine St, Denver, CO',
      value: '$350,000',
      score: 82.1,
      recommendation: 'BUY',
      timestamp: '1 hour ago',
    },
  ];

  const getRecommendationColor = (recommendation: string) => {
    switch (recommendation) {
      case 'BUY': return '#10b981';
      case 'HOLD': return '#f59e0b';
      case 'AVOID': return '#ef4444';
      default: return '#6b7280';
    }
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Box sx={{ mb: 4 }}>
          <Typography variant="h3" component="h1" gutterBottom sx={{ fontWeight: 700, color: '#1e293b' }}>
            🤖 Land Area Automation Hub
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
            AI-powered real estate analysis and investment intelligence
          </Typography>
          <Alert severity="info" sx={{ mb: 3 }}>
            <strong>New:</strong> SHAP-based explainable AI now available for all models! 
            Understand exactly why the AI made its recommendations.
          </Alert>
        </Box>
      </motion.div>

      {/* System Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {systemStats.map((stat, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card sx={{ height: '100%', textAlign: 'center' }}>
                <CardContent>
                  <Avatar sx={{ bgcolor: '#2563eb', mx: 'auto', mb: 2 }}>
                    {stat.icon}
                  </Avatar>
                  <Typography variant="h4" component="div" sx={{ fontWeight: 700, color: '#1e293b' }}>
                    {stat.value}
                  </Typography>
                  <Typography color="text.secondary">
                    {stat.label}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </motion.div>

      <Grid container spacing={4}>
        {/* Automation Features */}
        <Grid item xs={12} lg={8}>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <Typography variant="h4" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
              🚀 Automation Features
            </Typography>
            <Grid container spacing={3}>
              {automationFeatures.map((feature, index) => (
                <Grid item xs={12} md={6} key={feature.id}>
                  <motion.div
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Card 
                      sx={{ 
                        height: '100%', 
                        cursor: 'pointer',
                        border: selectedFeature === feature.id ? `2px solid ${feature.color}` : '1px solid #e2e8f0',
                        transition: 'all 0.2s ease-in-out',
                        '&:hover': {
                          boxShadow: '0 10px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
                        }
                      }}
                      onClick={() => setSelectedFeature(feature.id)}
                    >
                      <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                          <Avatar sx={{ bgcolor: feature.color, mr: 2 }}>
                            {feature.icon}
                          </Avatar>
                          <Box>
                            <Typography variant="h6" component="div" sx={{ fontWeight: 600 }}>
                              {feature.title}
                            </Typography>
                            <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                              <Chip 
                                label={feature.processingTime} 
                                size="small" 
                                color="primary" 
                                variant="outlined" 
                              />
                              <Chip 
                                label={feature.accuracy} 
                                size="small" 
                                color="success" 
                                variant="outlined" 
                              />
                            </Box>
                          </Box>
                        </Box>
                        
                        <Typography color="text.secondary" sx={{ mb: 2 }}>
                          {feature.description}
                        </Typography>
                        
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                            Key Features:
                          </Typography>
                          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                            {feature.features.map((feat, idx) => (
                              <Chip 
                                key={idx}
                                label={feat} 
                                size="small" 
                                variant="outlined"
                                sx={{ fontSize: '0.75rem' }}
                              />
                            ))}
                          </Box>
                        </Box>
                      </CardContent>
                      
                      <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2 }}>
                        <Button
                          variant="contained"
                          startIcon={<PlayArrow />}
                          onClick={(e) => {
                            e.stopPropagation();
                            navigate(feature.route);
                          }}
                          sx={{ 
                            bgcolor: feature.color,
                            '&:hover': { bgcolor: feature.color, opacity: 0.9 }
                          }}
                        >
                          Launch
                        </Button>
                        <Tooltip title="Learn more about this feature">
                          <IconButton size="small">
                            <Info />
                          </IconButton>
                        </Tooltip>
                      </CardActions>
                    </Card>
                  </motion.div>
                </Grid>
              ))}
            </Grid>
          </motion.div>
        </Grid>

        {/* Recent Analyses & Quick Actions */}
        <Grid item xs={12} lg={4}>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            {/* Recent Analyses */}
            <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, display: 'flex', alignItems: 'center' }}>
                <Timeline sx={{ mr: 1 }} />
                Recent Analyses
              </Typography>
              <List dense>
                {recentAnalyses.map((analysis) => (
                  <ListItem key={analysis.id} sx={{ px: 0 }}>
                    <ListItemIcon>
                      <LocationOn color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Typography variant="body2" sx={{ fontWeight: 600 }}>
                            {analysis.address}
                          </Typography>
                          <Chip
                            label={analysis.recommendation}
                            size="small"
                            sx={{
                              bgcolor: getRecommendationColor(analysis.recommendation),
                              color: 'white',
                              fontWeight: 600,
                              fontSize: '0.7rem',
                            }}
                          />
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            {analysis.value} • Score: {analysis.score}/100
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {analysis.timestamp}
                          </Typography>
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </Paper>

            {/* Quick Actions */}
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                🎯 Quick Actions
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<AutoAwesome />}
                  onClick={() => navigate('/automation/comprehensive')}
                >
                  New Comprehensive Analysis
                </Button>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<AttachMoney />}
                  onClick={() => navigate('/automation/valuation')}
                >
                  Quick Property Valuation
                </Button>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<Assessment />}
                  onClick={() => navigate('/automation/scoring')}
                >
                  Investment Scoring
                </Button>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<Analytics />}
                  onClick={() => navigate('/history')}
                >
                  View Analysis History
                </Button>
              </Box>
            </Paper>
          </motion.div>
        </Grid>
      </Grid>
    </Container>
  );
};

export default AutomationHubPage;
