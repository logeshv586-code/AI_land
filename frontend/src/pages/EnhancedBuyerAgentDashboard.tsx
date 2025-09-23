import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Avatar,
  List,
  ListItem,
  ListItemText,
  Chip,
  Alert,
  CircularProgress,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Badge,
} from '@mui/material';
import {
  People,
  TrendingUp,
  AttachMoney,
  CalendarToday,
  Notifications,
  Refresh,
  Star,
  ContactMail,
  Assessment,
  Schedule,
  Phone,
  Email,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { nvapiService, LeadScore, MarketTrend } from '../services/nvapiService';

const EnhancedBuyerAgentDashboard: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  
  // State for real-time data
  const [leadScores, setLeadScores] = useState<LeadScore[]>([]);
  const [marketTrends, setMarketTrends] = useState<MarketTrend[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  
  // Buyer Agent specific state
  const [activeClients, setActiveClients] = useState([
    {
      id: 1,
      name: 'John Smith',
      email: 'john@email.com',
      phone: '(555) 123-4567',
      budget: 450000,
      preferredLocation: 'Naperville, IL',
      status: 'actively_searching',
      lastContact: '2024-01-15',
      viewingsScheduled: 2,
      offersSubmitted: 0
    },
    {
      id: 2,
      name: 'Sarah Johnson',
      email: 'sarah@email.com',
      phone: '(555) 987-6543',
      budget: 350000,
      preferredLocation: 'Chicago, IL',
      status: 'pre_approved',
      lastContact: '2024-01-14',
      viewingsScheduled: 1,
      offersSubmitted: 1
    }
  ]);
  
  const [upcomingViewings, setUpcomingViewings] = useState([
    { id: 1, client: 'John Smith', property: '123 Oak St, Naperville', time: '2024-01-16 10:00 AM' },
    { id: 2, client: 'Sarah Johnson', property: '456 Pine Ave, Chicago', time: '2024-01-16 2:00 PM' },
    { id: 3, client: 'Mike Davis', property: '789 Elm St, Schaumburg', time: '2024-01-17 11:00 AM' }
  ]);
  
  const [recentActivity, setRecentActivity] = useState([
    { id: 1, type: 'new_lead', description: 'New lead: Emma Wilson', time: '2 hours ago' },
    { id: 2, type: 'viewing_completed', description: 'Viewing completed with John Smith', time: '4 hours ago' },
    { id: 3, type: 'offer_submitted', description: 'Offer submitted for Sarah Johnson', time: '1 day ago' }
  ]);
  
  const [totalCommission, setTotalCommission] = useState(45000);
  const [closedDeals, setClosedDeals] = useState(8);
  const [unreadMessages, setUnreadMessages] = useState(6);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Score leads using AI
      const leadData = activeClients.map(client => ({
        id: client.id.toString(),
        budget: client.budget,
        location: client.preferredLocation,
        propertyType: 'single_family',
        urgency: client.status === 'actively_searching' ? 'high' : 'medium',
        contactHistory: 5 // Mock contact frequency
      }));
      
      const scores = await nvapiService.scoreLeads(leadData);
      setLeadScores(scores);
      
      // Load market trends for client locations
      const locationSet = new Set(activeClients.map(c => c.preferredLocation));
      const uniqueLocations = Array.from(locationSet);
      const trendsPromises = uniqueLocations.map(location =>
        nvapiService.getMarketTrends(location)
      );
      const trends = await Promise.all(trendsPromises);
      setMarketTrends(trends);
      
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const refreshData = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(price);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'actively_searching': return 'success';
      case 'pre_approved': return 'primary';
      case 'offer_pending': return 'warning';
      case 'closed': return 'info';
      default: return 'default';
    }
  };

  const getLeadScoreColor = (score: number) => {
    if (score >= 80) return 'success.main';
    if (score >= 60) return 'warning.main';
    return 'error.main';
  };

  const StatCard: React.FC<{
    title: string;
    value: string | number;
    icon: React.ReactNode;
    color: string;
    subtitle?: string;
    trend?: number;
  }> = ({ title, value, icon, color, subtitle, trend }) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4" component="h2" sx={{ color }}>
              {value}
            </Typography>
            {subtitle && (
              <Typography variant="body2" color="textSecondary">
                {subtitle}
              </Typography>
            )}
            {trend !== undefined && (
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                <TrendingUp 
                  fontSize="small" 
                  sx={{ 
                    color: trend > 0 ? 'success.main' : 'error.main',
                    transform: trend < 0 ? 'rotate(180deg)' : 'none'
                  }} 
                />
                <Typography 
                  variant="body2" 
                  sx={{ 
                    color: trend > 0 ? 'success.main' : 'error.main',
                    ml: 0.5
                  }}
                >
                  {trend > 0 ? '+' : ''}{trend}%
                </Typography>
              </Box>
            )}
          </Box>
          <Avatar sx={{ bgcolor: color, width: 56, height: 56 }}>
            {icon}
          </Avatar>
        </Box>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
          <CircularProgress />
          <Typography sx={{ ml: 2 }}>Loading your buyer agent dashboard...</Typography>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
            Welcome back, Agent {user?.first_name || user?.username}!
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            Manage your buyer clients with AI-powered insights and real-time market data.
          </Typography>
        </Box>
        <IconButton onClick={refreshData} disabled={refreshing}>
          <Refresh sx={{ animation: refreshing ? 'spin 1s linear infinite' : 'none' }} />
        </IconButton>
      </Box>

      {/* Agent Role Notice */}
      <Alert severity="success" sx={{ mb: 4 }}>
        <Typography variant="body2">
          <strong>Buyer Agent Dashboard:</strong> You represent buyers in their property search. 
          You can communicate with seller agents on behalf of your clients and help them find the perfect home.
        </Typography>
      </Alert>

      {/* Performance Stats */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Clients"
            value={activeClients.length}
            icon={<People />}
            color="primary.main"
            subtitle="Currently serving"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Closed Deals"
            value={closedDeals}
            icon={<Star />}
            color="success.main"
            subtitle="This year"
            trend={15}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Commission"
            value={formatPrice(totalCommission)}
            icon={<AttachMoney />}
            color="secondary.main"
            subtitle="Year to date"
            trend={22}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Unread Messages"
            value={unreadMessages}
            icon={<Notifications />}
            color="warning.main"
            subtitle="From clients & agents"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Left Column */}
        <Grid item xs={12} md={8}>
          {/* Active Clients with AI Lead Scoring */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Active Clients (AI Lead Scoring)
                </Typography>
                <Button variant="outlined" size="small">
                  Add New Client
                </Button>
              </Box>
              <TableContainer component={Paper} variant="outlined">
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Client</TableCell>
                      <TableCell>Budget</TableCell>
                      <TableCell>Location</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>AI Score</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {activeClients.map((client, index) => {
                      const leadScore = leadScores.find(score => score.leadId === client.id.toString());
                      return (
                        <TableRow key={client.id}>
                          <TableCell>
                            <Box>
                              <Typography variant="subtitle2">{client.name}</Typography>
                              <Typography variant="body2" color="textSecondary">
                                {client.email}
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell>{formatPrice(client.budget)}</TableCell>
                          <TableCell>{client.preferredLocation}</TableCell>
                          <TableCell>
                            <Chip 
                              label={client.status.replace('_', ' ').toUpperCase()} 
                              color={getStatusColor(client.status) as any}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            {leadScore && (
                              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                <Typography 
                                  variant="h6" 
                                  sx={{ color: getLeadScoreColor(leadScore.score), mr: 1 }}
                                >
                                  {leadScore.score}
                                </Typography>
                                <Typography variant="body2" color="textSecondary">
                                  /100
                                </Typography>
                              </Box>
                            )}
                          </TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', gap: 1 }}>
                              <IconButton size="small" onClick={() => window.open(`tel:${client.phone}`)}>
                                <Phone fontSize="small" />
                              </IconButton>
                              <IconButton size="small" onClick={() => window.open(`mailto:${client.email}`)}>
                                <Email fontSize="small" />
                              </IconButton>
                              <Button size="small" onClick={() => navigate(`/clients/${client.id}`)}>
                                View
                              </Button>
                            </Box>
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>

          {/* Market Insights for Client Areas */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Market Insights - Client Areas
              </Typography>
              <Grid container spacing={2}>
                {marketTrends.map((trend, index) => (
                  <Grid item xs={12} sm={6} key={index}>
                    <Box sx={{ p: 2, backgroundColor: 'primary.light', borderRadius: 1, color: 'primary.contrastText' }}>
                      <Typography variant="h6">{trend.location}</Typography>
                      <Typography variant="body2">Avg Price: {formatPrice(trend.averagePrice)}</Typography>
                      <Typography variant="body2">Days on Market: {trend.daysOnMarket}</Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                        <TrendingUp fontSize="small" />
                        <Typography variant="body2" sx={{ ml: 0.5 }}>
                          {trend.priceChangePercent > 0 ? '+' : ''}{trend.priceChangePercent}%
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Right Column */}
        <Grid item xs={12} md={4}>
          {/* Upcoming Viewings */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <Badge badgeContent={upcomingViewings.length} color="primary">
                  Upcoming Viewings
                </Badge>
              </Typography>
              <List>
                {upcomingViewings.map((viewing, index) => (
                  <ListItem key={viewing.id} divider={index < upcomingViewings.length - 1}>
                    <ListItemText
                      primary={viewing.client}
                      secondary={
                        <Box>
                          <Typography variant="body2">{viewing.property}</Typography>
                          <Typography variant="caption" color="primary">
                            {viewing.time}
                          </Typography>
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
              <Button
                fullWidth
                variant="outlined"
                sx={{ mt: 2 }}
                startIcon={<Schedule />}
                onClick={() => navigate('/calendar')}
              >
                View Calendar
              </Button>
            </CardContent>
          </Card>

          {/* Recent Activity */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Activity
              </Typography>
              <List>
                {recentActivity.map((activity, index) => (
                  <ListItem key={activity.id} divider={index < recentActivity.length - 1}>
                    <ListItemText
                      primary={activity.description}
                      secondary={activity.time}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Button
                  variant="contained"
                  startIcon={<People />}
                  onClick={() => navigate('/clients/new')}
                >
                  Add New Client
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Schedule />}
                  onClick={() => navigate('/viewings/schedule')}
                >
                  Schedule Viewing
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<ContactMail />}
                  onClick={() => navigate('/messages')}
                >
                  Contact Seller Agent
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Assessment />}
                  onClick={() => navigate('/reports')}
                >
                  Generate Reports
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default EnhancedBuyerAgentDashboard;
