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
  TextField,
  InputAdornment,
} from '@mui/material';
import {
  Home,
  Search,
  Favorite,
  TrendingUp,
  LocationOn,
  AttachMoney,
  CalendarToday,
  Notifications,
  Refresh,
  ShowChart,
  School,
  DirectionsCar,
  Message,
  Warning,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { nvapiService, MarketTrend, LocationInsights } from '../services/nvapiService';

const EnhancedBuyerDashboard: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  
  // State for real-time data
  const [marketTrends, setMarketTrends] = useState<MarketTrend[]>([]);
  const [locationInsights, setLocationInsights] = useState<LocationInsights | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [searchLocation, setSearchLocation] = useState('Chicago, IL');
  
  // Buyer-specific state
  const [savedSearches, setSavedSearches] = useState([
    { location: 'Chicago, IL', criteria: '3BR, $300K-$500K' },
    { location: 'Naperville, IL', criteria: '4BR, $400K-$600K' },
    { location: 'Schaumburg, IL', criteria: '2BR, $250K-$400K' }
  ]);
  const [favoriteProperties, setFavoriteProperties] = useState([
    { id: 1, title: 'Beautiful 3BR Home', price: 425000, location: 'Naperville, IL' },
    { id: 2, title: 'Modern Condo', price: 350000, location: 'Chicago, IL' }
  ]);
  const [recentViewings, setRecentViewings] = useState([
    { id: 1, title: 'Luxury Townhouse', date: '2024-01-15', agent: 'Sarah Johnson' },
    { id: 2, title: 'Family Home', date: '2024-01-12', agent: 'Mike Davis' }
  ]);
  const [unreadMessages, setUnreadMessages] = useState(2);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load market trends for buyer's preferred locations
      const trendsPromises = savedSearches.map(search => 
        nvapiService.getMarketTrends(search.location)
      );
      const trends = await Promise.all(trendsPromises);
      setMarketTrends(trends);
      
      // Load location insights for primary search location
      const insights = await nvapiService.getLocationInsights(searchLocation);
      setLocationInsights(insights);
      
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

  const handleSearch = () => {
    navigate(`/properties?location=${encodeURIComponent(searchLocation)}`);
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(price);
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
          <Typography sx={{ ml: 2 }}>Loading your personalized dashboard...</Typography>
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
            Find your perfect home with AI-powered insights and real-time market data.
          </Typography>
        </Box>
        <IconButton onClick={refreshData} disabled={refreshing}>
          <Refresh sx={{ animation: refreshing ? 'spin 1s linear infinite' : 'none' }} />
        </IconButton>
      </Box>

      {/* Important Notice for Buyers */}
      <Alert severity="info" sx={{ mb: 4 }}>
        <Typography variant="body2">
          <strong>How it works:</strong> As a buyer, you can browse properties and contact seller agents directly. 
          For the best experience, consider working with a buyer agent who can represent your interests and negotiate on your behalf.
        </Typography>
      </Alert>

      {/* Quick Search */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Quick Property Search
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            <TextField
              fullWidth
              placeholder="Enter location (e.g., Chicago, IL)"
              value={searchLocation}
              onChange={(e) => setSearchLocation(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <LocationOn />
                  </InputAdornment>
                ),
              }}
            />
            <Button
              variant="contained"
              size="large"
              startIcon={<Search />}
              onClick={handleSearch}
              sx={{ minWidth: 120 }}
            >
              Search
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Market Overview Stats */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Avg. Home Price"
            value={marketTrends[0] ? formatPrice(marketTrends[0].averagePrice) : 'Loading...'}
            icon={<AttachMoney />}
            color="primary.main"
            subtitle={searchLocation}
            trend={marketTrends[0]?.priceChangePercent}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Days on Market"
            value={marketTrends[0]?.daysOnMarket || 'Loading...'}
            icon={<CalendarToday />}
            color="secondary.main"
            subtitle="Average time"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Available Homes"
            value={marketTrends[0]?.inventory || 'Loading...'}
            icon={<Home />}
            color="success.main"
            subtitle="Current inventory"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Unread Messages"
            value={unreadMessages}
            icon={<Message />}
            color="warning.main"
            subtitle="From agents"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Left Column */}
        <Grid item xs={12} md={8}>
          {/* Location Insights */}
          {locationInsights && (
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Location Insights: {locationInsights.location}
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6} sm={3}>
                    <Box sx={{ textAlign: 'center', p: 2 }}>
                      <DirectionsCar color="primary" sx={{ fontSize: 40, mb: 1 }} />
                      <Typography variant="h6">{locationInsights.walkScore}</Typography>
                      <Typography variant="body2" color="textSecondary">Walk Score</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Box sx={{ textAlign: 'center', p: 2 }}>
                      <School color="secondary" sx={{ fontSize: 40, mb: 1 }} />
                      <Typography variant="h6">{locationInsights.schoolRating}/10</Typography>
                      <Typography variant="body2" color="textSecondary">School Rating</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Box sx={{ textAlign: 'center', p: 2 }}>
                      <ShowChart color="success" sx={{ fontSize: 40, mb: 1 }} />
                      <Typography variant="h6">{locationInsights.futureGrowthPotential}%</Typography>
                      <Typography variant="body2" color="textSecondary">Growth Potential</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Box sx={{ textAlign: 'center', p: 2 }}>
                      <AttachMoney color="warning" sx={{ fontSize: 40, mb: 1 }} />
                      <Typography variant="h6">{formatPrice(locationInsights.demographics.medianIncome)}</Typography>
                      <Typography variant="body2" color="textSecondary">Median Income</Typography>
                    </Box>
                  </Grid>
                </Grid>
                
                <Divider sx={{ my: 2 }} />
                
                <Typography variant="subtitle2" gutterBottom>
                  Nearby Amenities:
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {locationInsights.amenities.map((amenity, index) => (
                    <Chip key={index} label={amenity} size="small" variant="outlined" />
                  ))}
                </Box>
              </CardContent>
            </Card>
          )}

          {/* Favorite Properties */}
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Favorite Properties
                </Typography>
                <Button size="small" onClick={() => navigate('/properties')}>
                  View All
                </Button>
              </Box>
              <List>
                {favoriteProperties.map((property, index) => (
                  <ListItem key={property.id} divider={index < favoriteProperties.length - 1}>
                    <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                      <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                        <Home />
                      </Avatar>
                      <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="subtitle1">{property.title}</Typography>
                        <Typography variant="body2" color="textSecondary">
                          {property.location} • {formatPrice(property.price)}
                        </Typography>
                      </Box>
                      <Button
                        variant="outlined"
                        size="small"
                        onClick={() => navigate(`/properties/${property.id}`)}
                      >
                        View
                      </Button>
                    </Box>
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Right Column */}
        <Grid item xs={12} md={4}>
          {/* Saved Searches */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Saved Searches
              </Typography>
              <List>
                {savedSearches.map((search, index) => (
                  <ListItem key={index} divider={index < savedSearches.length - 1}>
                    <ListItemText
                      primary={search.location}
                      secondary={search.criteria}
                    />
                    <Button size="small" onClick={() => navigate(`/properties?location=${search.location}`)}>
                      Search
                    </Button>
                  </ListItem>
                ))}
              </List>
              <Button
                fullWidth
                variant="outlined"
                sx={{ mt: 2 }}
                onClick={() => navigate('/properties')}
              >
                Create New Search
              </Button>
            </CardContent>
          </Card>

          {/* Recent Activity */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Viewings
              </Typography>
              <List>
                {recentViewings.map((viewing, index) => (
                  <ListItem key={viewing.id} divider={index < recentViewings.length - 1}>
                    <ListItemText
                      primary={viewing.title}
                      secondary={`${viewing.date} • Agent: ${viewing.agent}`}
                    />
                  </ListItem>
                ))}
              </List>
              <Button
                fullWidth
                variant="outlined"
                sx={{ mt: 2 }}
                onClick={() => navigate('/messages')}
              >
                View Messages
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default EnhancedBuyerDashboard;
