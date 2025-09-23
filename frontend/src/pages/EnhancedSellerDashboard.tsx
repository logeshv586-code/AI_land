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
  LinearProgress,
  Alert,
  CircularProgress,
  Divider,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import {
  Home,
  Visibility,
  TrendingUp,
  AttachMoney,
  CalendarToday,
  Notifications,
  Refresh,
  ShowChart,
  ContactMail,
  Assessment,
  Warning,
  CheckCircle,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { nvapiService, MarketTrend, PropertyValuation } from '../services/nvapiService';

const EnhancedSellerDashboard: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  
  // State for real-time data
  const [marketTrends, setMarketTrends] = useState<MarketTrend | null>(null);
  const [propertyValuations, setPropertyValuations] = useState<PropertyValuation[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  
  // Seller-specific state
  const [myListings, setMyListings] = useState([
    {
      id: 1,
      title: 'Beautiful Family Home',
      address: '123 Oak Street, Naperville, IL',
      price: 425000,
      status: 'active',
      daysOnMarket: 15,
      views: 234,
      inquiries: 12,
      scheduledViewings: 3
    },
    {
      id: 2,
      title: 'Modern Condo Downtown',
      address: '456 Michigan Ave, Chicago, IL',
      price: 350000,
      status: 'pending',
      daysOnMarket: 8,
      views: 189,
      inquiries: 8,
      scheduledViewings: 1
    }
  ]);
  
  const [recentInquiries, setRecentInquiries] = useState([
    { id: 1, property: 'Beautiful Family Home', buyer: 'John Smith', date: '2024-01-15', status: 'new' },
    { id: 2, property: 'Modern Condo Downtown', buyer: 'Sarah Johnson', date: '2024-01-14', status: 'responded' }
  ]);
  
  const [totalViews, setTotalViews] = useState(423);
  const [totalInquiries, setTotalInquiries] = useState(20);
  const [unreadMessages, setUnreadMessages] = useState(4);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load market trends for seller's area
      const trends = await nvapiService.getMarketTrends('Naperville, IL');
      setMarketTrends(trends);
      
      // Load property valuations for seller's listings
      const valuationPromises = myListings.map(listing => 
        nvapiService.getPropertyValuation({
          address: listing.address,
          sqft: 2100, // Mock data
          bedrooms: 3,
          bathrooms: 2.5,
          yearBuilt: 2015,
          lotSize: 0.25
        })
      );
      const valuations = await Promise.all(valuationPromises);
      setPropertyValuations(valuations);
      
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
      case 'active': return 'success';
      case 'pending': return 'warning';
      case 'sold': return 'primary';
      case 'expired': return 'error';
      default: return 'default';
    }
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
          <Typography sx={{ ml: 2 }}>Loading your seller dashboard...</Typography>
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
            Welcome back, {user?.first_name || user?.username}!
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            Track your property performance and connect with qualified buyers through seller agents.
          </Typography>
        </Box>
        <IconButton onClick={refreshData} disabled={refreshing}>
          <Refresh sx={{ animation: refreshing ? 'spin 1s linear infinite' : 'none' }} />
        </IconButton>
      </Box>

      {/* Important Notice for Sellers */}
      <Alert severity="info" sx={{ mb: 4 }}>
        <Typography variant="body2">
          <strong>How it works:</strong> As a seller, you can list properties and track performance. 
          To communicate with buyer agents and manage negotiations, work with a qualified seller agent who will represent your interests.
        </Typography>
      </Alert>

      {/* Performance Stats */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Property Views"
            value={totalViews}
            icon={<Visibility />}
            color="primary.main"
            subtitle="Last 30 days"
            trend={12}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Inquiries"
            value={totalInquiries}
            icon={<ContactMail />}
            color="secondary.main"
            subtitle="This month"
            trend={8}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Market Average Price"
            value={marketTrends ? formatPrice(marketTrends.averagePrice) : 'Loading...'}
            icon={<AttachMoney />}
            color="success.main"
            subtitle="Your area"
            trend={marketTrends?.priceChangePercent}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Unread Messages"
            value={unreadMessages}
            icon={<Notifications />}
            color="warning.main"
            subtitle="From agents"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Left Column */}
        <Grid item xs={12} md={8}>
          {/* My Listings */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  My Property Listings
                </Typography>
                <Button variant="outlined" size="small">
                  Add New Listing
                </Button>
              </Box>
              <TableContainer component={Paper} variant="outlined">
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Property</TableCell>
                      <TableCell>Price</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Days on Market</TableCell>
                      <TableCell>Views</TableCell>
                      <TableCell>Inquiries</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {myListings.map((listing) => (
                      <TableRow key={listing.id}>
                        <TableCell>
                          <Box>
                            <Typography variant="subtitle2">{listing.title}</Typography>
                            <Typography variant="body2" color="textSecondary">
                              {listing.address}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>{formatPrice(listing.price)}</TableCell>
                        <TableCell>
                          <Chip 
                            label={listing.status.toUpperCase()} 
                            color={getStatusColor(listing.status) as any}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{listing.daysOnMarket} days</TableCell>
                        <TableCell>{listing.views}</TableCell>
                        <TableCell>{listing.inquiries}</TableCell>
                        <TableCell>
                          <Button size="small" onClick={() => navigate(`/properties/${listing.id}`)}>
                            View
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>

          {/* Market Insights */}
          {marketTrends && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Market Insights - {marketTrends.location}
                </Typography>
                <Grid container spacing={3}>
                  <Grid item xs={12} sm={6}>
                    <Box sx={{ p: 2, backgroundColor: 'primary.light', borderRadius: 1, color: 'primary.contrastText' }}>
                      <Typography variant="h6">{formatPrice(marketTrends.averagePrice)}</Typography>
                      <Typography variant="body2">Average Sale Price</Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                        <TrendingUp fontSize="small" />
                        <Typography variant="body2" sx={{ ml: 0.5 }}>
                          {marketTrends.priceChangePercent > 0 ? '+' : ''}{marketTrends.priceChangePercent}% from last month
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Box sx={{ p: 2, backgroundColor: 'secondary.light', borderRadius: 1, color: 'secondary.contrastText' }}>
                      <Typography variant="h6">{marketTrends.daysOnMarket} days</Typography>
                      <Typography variant="body2">Average Days on Market</Typography>
                      <Typography variant="body2" sx={{ mt: 1 }}>
                        {marketTrends.inventory} homes available
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          )}
        </Grid>

        {/* Right Column */}
        <Grid item xs={12} md={4}>
          {/* Recent Inquiries */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Inquiries
              </Typography>
              <List>
                {recentInquiries.map((inquiry, index) => (
                  <ListItem key={inquiry.id} divider={index < recentInquiries.length - 1}>
                    <Box sx={{ width: '100%' }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant="subtitle2">{inquiry.buyer}</Typography>
                        <Chip 
                          label={inquiry.status} 
                          size="small" 
                          color={inquiry.status === 'new' ? 'warning' : 'success'}
                        />
                      </Box>
                      <Typography variant="body2" color="textSecondary">
                        {inquiry.property}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        {inquiry.date}
                      </Typography>
                    </Box>
                  </ListItem>
                ))}
              </List>
              <Button
                fullWidth
                variant="outlined"
                sx={{ mt: 2 }}
                onClick={() => navigate('/messages')}
              >
                View All Messages
              </Button>
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
                  startIcon={<Home />}
                  onClick={() => navigate('/properties/new')}
                >
                  List New Property
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Assessment />}
                  onClick={() => navigate('/analytics')}
                >
                  View Analytics
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
                  startIcon={<ShowChart />}
                  onClick={() => navigate('/market-insights')}
                >
                  Market Reports
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default EnhancedSellerDashboard;
