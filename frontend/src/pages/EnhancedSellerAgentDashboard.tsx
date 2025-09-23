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
  Home,
  TrendingUp,
  AttachMoney,
  Visibility,
  Notifications,
  Refresh,
  Star,
  ContactMail,
  Assessment,
  Schedule,
  Phone,
  Email,
  ShowChart,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { nvapiService, PropertyValuation, MarketTrend } from '../services/nvapiService';

const EnhancedSellerAgentDashboard: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  
  // State for real-time data
  const [propertyValuations, setPropertyValuations] = useState<PropertyValuation[]>([]);
  const [marketTrends, setMarketTrends] = useState<MarketTrend[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  
  // Seller Agent specific state
  const [activeListings, setActiveListings] = useState([
    {
      id: 1,
      title: 'Luxury Family Home',
      address: '123 Oak Street, Naperville, IL',
      price: 525000,
      seller: 'Robert Johnson',
      status: 'active',
      daysOnMarket: 12,
      views: 156,
      inquiries: 8,
      scheduledViewings: 4,
      offers: 1
    },
    {
      id: 2,
      title: 'Modern Downtown Condo',
      address: '456 Michigan Ave, Chicago, IL',
      price: 425000,
      seller: 'Lisa Chen',
      status: 'pending',
      daysOnMarket: 6,
      views: 203,
      inquiries: 12,
      scheduledViewings: 2,
      offers: 2
    }
  ]);
  
  const [sellerClients, setSellerClients] = useState([
    {
      id: 1,
      name: 'Robert Johnson',
      email: 'robert@email.com',
      phone: '(555) 123-4567',
      propertyCount: 1,
      totalValue: 525000,
      status: 'active_listing',
      lastContact: '2024-01-15'
    },
    {
      id: 2,
      name: 'Lisa Chen',
      email: 'lisa@email.com',
      phone: '(555) 987-6543',
      propertyCount: 1,
      totalValue: 425000,
      status: 'offer_pending',
      lastContact: '2024-01-14'
    }
  ]);
  
  const [upcomingShowings, setUpcomingShowings] = useState([
    { id: 1, property: 'Luxury Family Home', buyerAgent: 'Sarah Wilson', time: '2024-01-16 10:00 AM' },
    { id: 2, property: 'Modern Downtown Condo', buyerAgent: 'Mike Davis', time: '2024-01-16 2:00 PM' },
    { id: 3, property: 'Luxury Family Home', buyerAgent: 'Emma Thompson', time: '2024-01-17 11:00 AM' }
  ]);
  
  const [recentOffers, setRecentOffers] = useState([
    { id: 1, property: 'Modern Downtown Condo', amount: 420000, status: 'pending', buyerAgent: 'Mike Davis' },
    { id: 2, property: 'Luxury Family Home', amount: 510000, status: 'countered', buyerAgent: 'Sarah Wilson' }
  ]);
  
  const [totalCommission, setTotalCommission] = useState(67500);
  const [closedDeals, setClosedDeals] = useState(12);
  const [unreadMessages, setUnreadMessages] = useState(8);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load property valuations for active listings
      const valuationPromises = activeListings.map(listing => 
        nvapiService.getPropertyValuation({
          address: listing.address,
          sqft: 2400, // Mock data
          bedrooms: 4,
          bathrooms: 3,
          yearBuilt: 2018,
          lotSize: 0.3
        })
      );
      const valuations = await Promise.all(valuationPromises);
      setPropertyValuations(valuations);
      
      // Load market trends for listing areas
      const locationSet = new Set(activeListings.map(l => l.address.split(',').slice(-2).join(',').trim()));
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
      case 'active': return 'success';
      case 'pending': return 'warning';
      case 'sold': return 'primary';
      case 'expired': return 'error';
      case 'active_listing': return 'success';
      case 'offer_pending': return 'warning';
      default: return 'default';
    }
  };

  const getOfferStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'warning';
      case 'accepted': return 'success';
      case 'rejected': return 'error';
      case 'countered': return 'info';
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
          <Typography sx={{ ml: 2 }}>Loading your seller agent dashboard...</Typography>
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
            Manage your seller clients and listings with AI-powered market insights and valuation tools.
          </Typography>
        </Box>
        <IconButton onClick={refreshData} disabled={refreshing}>
          <Refresh sx={{ animation: refreshing ? 'spin 1s linear infinite' : 'none' }} />
        </IconButton>
      </Box>

      {/* Agent Role Notice */}
      <Alert severity="success" sx={{ mb: 4 }}>
        <Typography variant="body2">
          <strong>Seller Agent Dashboard:</strong> You represent sellers in marketing their properties. 
          You can communicate with buyer agents, manage offers, and help sellers get the best price for their homes.
        </Typography>
      </Alert>

      {/* Performance Stats */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Listings"
            value={activeListings.length}
            icon={<Home />}
            color="primary.main"
            subtitle="Currently marketing"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Closed Deals"
            value={closedDeals}
            icon={<Star />}
            color="success.main"
            subtitle="This year"
            trend={18}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Commission"
            value={formatPrice(totalCommission)}
            icon={<AttachMoney />}
            color="secondary.main"
            subtitle="Year to date"
            trend={25}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Unread Messages"
            value={unreadMessages}
            icon={<Notifications />}
            color="warning.main"
            subtitle="From buyers & agents"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Left Column */}
        <Grid item xs={12} md={8}>
          {/* Active Listings with AI Valuations */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Active Listings (AI Valuations)
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
                      <TableCell>Listed Price</TableCell>
                      <TableCell>AI Valuation</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Views</TableCell>
                      <TableCell>Offers</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {activeListings.map((listing, index) => {
                      const valuation = propertyValuations[index];
                      const priceDiff = valuation ? ((listing.price - valuation.estimatedValue) / valuation.estimatedValue * 100) : 0;
                      return (
                        <TableRow key={listing.id}>
                          <TableCell>
                            <Box>
                              <Typography variant="subtitle2">{listing.title}</Typography>
                              <Typography variant="body2" color="textSecondary">
                                {listing.address}
                              </Typography>
                              <Typography variant="caption" color="textSecondary">
                                Seller: {listing.seller}
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell>{formatPrice(listing.price)}</TableCell>
                          <TableCell>
                            {valuation ? (
                              <Box>
                                <Typography variant="body2">
                                  {formatPrice(valuation.estimatedValue)}
                                </Typography>
                                <Typography 
                                  variant="caption" 
                                  sx={{ 
                                    color: priceDiff > 5 ? 'warning.main' : priceDiff < -5 ? 'error.main' : 'success.main'
                                  }}
                                >
                                  {priceDiff > 0 ? '+' : ''}{priceDiff.toFixed(1)}%
                                </Typography>
                              </Box>
                            ) : 'Loading...'}
                          </TableCell>
                          <TableCell>
                            <Chip 
                              label={listing.status.toUpperCase()} 
                              color={getStatusColor(listing.status) as any}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>{listing.views}</TableCell>
                          <TableCell>
                            <Badge badgeContent={listing.offers} color="primary">
                              <Typography variant="body2">Offers</Typography>
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <Button size="small" onClick={() => navigate(`/properties/${listing.id}`)}>
                              Manage
                            </Button>
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>

          {/* Market Insights */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Market Insights - Listing Areas
              </Typography>
              <Grid container spacing={2}>
                {marketTrends.map((trend, index) => (
                  <Grid item xs={12} sm={6} key={index}>
                    <Box sx={{ p: 2, backgroundColor: 'primary.light', borderRadius: 1, color: 'primary.contrastText' }}>
                      <Typography variant="h6">{trend.location}</Typography>
                      <Typography variant="body2">Avg Price: {formatPrice(trend.averagePrice)}</Typography>
                      <Typography variant="body2">Days on Market: {trend.daysOnMarket}</Typography>
                      <Typography variant="body2">Inventory: {trend.inventory} homes</Typography>
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
          {/* Recent Offers */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <Badge badgeContent={recentOffers.length} color="primary">
                  Recent Offers
                </Badge>
              </Typography>
              <List>
                {recentOffers.map((offer, index) => (
                  <ListItem key={offer.id} divider={index < recentOffers.length - 1}>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Typography variant="subtitle2">{formatPrice(offer.amount)}</Typography>
                          <Chip 
                            label={offer.status} 
                            size="small" 
                            color={getOfferStatusColor(offer.status) as any}
                          />
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2">{offer.property}</Typography>
                          <Typography variant="caption" color="textSecondary">
                            Buyer Agent: {offer.buyerAgent}
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
                onClick={() => navigate('/offers')}
              >
                Manage All Offers
              </Button>
            </CardContent>
          </Card>

          {/* Upcoming Showings */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <Badge badgeContent={upcomingShowings.length} color="secondary">
                  Upcoming Showings
                </Badge>
              </Typography>
              <List>
                {upcomingShowings.map((showing, index) => (
                  <ListItem key={showing.id} divider={index < upcomingShowings.length - 1}>
                    <ListItemText
                      primary={showing.property}
                      secondary={
                        <Box>
                          <Typography variant="body2">Agent: {showing.buyerAgent}</Typography>
                          <Typography variant="caption" color="primary">
                            {showing.time}
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
                  onClick={() => navigate('/listings/new')}
                >
                  Add New Listing
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<ShowChart />}
                  onClick={() => navigate('/market-analysis')}
                >
                  Market Analysis
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<ContactMail />}
                  onClick={() => navigate('/messages')}
                >
                  Contact Buyer Agent
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

export default EnhancedSellerAgentDashboard;
