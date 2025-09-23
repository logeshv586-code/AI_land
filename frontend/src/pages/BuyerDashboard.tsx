import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Chip,
  TextField,
  InputAdornment,
  IconButton,
} from '@mui/material';
import {
  Search,
  Favorite,
  Home,
  LocationOn,
  TrendingUp,
  Message,
  Notifications,
  FilterList,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';

const BuyerDashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');
  const [recentSearches, setRecentSearches] = useState([
    'Chicago, IL',
    'Naperville, IL',
    'Schaumburg, IL'
  ]);
  const [favoriteProperties, setFavoriteProperties] = useState([]);
  const [recommendedProperties, setRecommendedProperties] = useState([]);
  const [unreadMessages, setUnreadMessages] = useState(3);

  const StatCard: React.FC<{
    title: string;
    value: string | number;
    icon: React.ReactNode;
    color: string;
    onClick?: () => void;
  }> = ({ title, value, icon, color, onClick }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card sx={{ height: '100%', cursor: onClick ? 'pointer' : 'default' }} onClick={onClick}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Avatar sx={{ bgcolor: color, mr: 2 }}>
              {icon}
            </Avatar>
            <Box>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold' }}>
                {value}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {title}
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  );

  const handleSearch = () => {
    if (searchQuery.trim()) {
      navigate(`/properties?search=${encodeURIComponent(searchQuery)}`);
    }
  };

  return (
    <Box>
      {/* Welcome Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
            Welcome back, {user?.first_name || user?.username}!
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            Find your dream home in Illinois with our comprehensive property search and neighborhood analysis.
          </Typography>
          
          {/* Search Bar */}
          <Box sx={{ mb: 3 }}>
            <TextField
              fullWidth
              placeholder="Search properties by location, address, or neighborhood..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <LocationOn color="action" />
                  </InputAdornment>
                ),
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton onClick={handleSearch} color="primary">
                      <Search />
                    </IconButton>
                    <IconButton onClick={() => navigate('/properties?filters=true')} color="primary">
                      <FilterList />
                    </IconButton>
                  </InputAdornment>
                ),
              }}
              sx={{ maxWidth: 600 }}
            />
          </Box>

          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            <Button
              variant="contained"
              startIcon={<Search />}
              onClick={() => navigate('/properties')}
              size="large"
            >
              Browse Properties
            </Button>
            <Button
              variant="outlined"
              startIcon={<TrendingUp />}
              onClick={() => navigate('/illinois-neighborhood/assess')}
              size="large"
            >
              Neighborhood Analysis
            </Button>
            <Button
              variant="outlined"
              startIcon={<Favorite />}
              onClick={() => navigate('/favorites')}
              size="large"
            >
              My Favorites
            </Button>
          </Box>
        </Box>
      </motion.div>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Saved Properties"
            value={favoriteProperties.length || 12}
            icon={<Favorite />}
            color="#e91e63"
            onClick={() => navigate('/favorites')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Property Views"
            value={47}
            icon={<Home />}
            color="#2196f3"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Unread Messages"
            value={unreadMessages}
            icon={<Message />}
            color="#ff9800"
            onClick={() => navigate('/messages')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Searches This Month"
            value={23}
            icon={<Search />}
            color="#4caf50"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Recent Searches */}
        <Grid item xs={12} md={6}>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <Card>
              <CardContent>
                <Typography variant="h6" component="h2" sx={{ fontWeight: 'bold', mb: 2 }}>
                  Recent Searches
                </Typography>
                <List>
                  {recentSearches.map((search, index) => (
                    <ListItem
                      key={index}
                      sx={{
                        cursor: 'pointer',
                        borderRadius: 1,
                        '&:hover': { backgroundColor: 'action.hover' },
                      }}
                      onClick={() => navigate(`/properties?search=${encodeURIComponent(search)}`)}
                    >
                      <ListItemAvatar>
                        <Avatar sx={{ bgcolor: 'primary.main' }}>
                          <LocationOn />
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={search}
                        secondary="Click to search again"
                      />
                    </ListItem>
                  ))}
                </List>
                <Button
                  fullWidth
                  variant="outlined"
                  onClick={() => navigate('/properties')}
                  sx={{ mt: 2 }}
                >
                  Advanced Search
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Recommended Properties */}
        <Grid item xs={12} md={6}>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            <Card>
              <CardContent>
                <Typography variant="h6" component="h2" sx={{ fontWeight: 'bold', mb: 2 }}>
                  Recommended for You
                </Typography>
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Home sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                  <Typography variant="h6" color="text.secondary" gutterBottom>
                    Personalized Recommendations
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    Start browsing properties to get personalized recommendations based on your preferences
                  </Typography>
                  <Button
                    variant="contained"
                    startIcon={<Search />}
                    onClick={() => navigate('/properties')}
                  >
                    Start Browsing
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Market Insights */}
        <Grid item xs={12}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.6 }}
          >
            <Card>
              <CardContent>
                <Typography variant="h6" component="h2" sx={{ fontWeight: 'bold', mb: 2 }}>
                  Illinois Market Insights
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={4}>
                    <Box sx={{ textAlign: 'center', p: 2 }}>
                      <Typography variant="h4" color="primary" sx={{ fontWeight: 'bold' }}>
                        $285K
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Median Home Price
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Box sx={{ textAlign: 'center', p: 2 }}>
                      <Typography variant="h4" color="success.main" sx={{ fontWeight: 'bold' }}>
                        +3.2%
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Year-over-Year Growth
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Box sx={{ textAlign: 'center', p: 2 }}>
                      <Typography variant="h4" color="info.main" sx={{ fontWeight: 'bold' }}>
                        45
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Days on Market (Avg)
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
                <Button
                  fullWidth
                  variant="outlined"
                  onClick={() => navigate('/market-insights')}
                  sx={{ mt: 2 }}
                >
                  View Detailed Market Report
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>
    </Box>
  );
};

export default BuyerDashboard;
