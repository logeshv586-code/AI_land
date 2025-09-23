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
  LinearProgress,
  IconButton,
} from '@mui/material';
import {
  Add,
  Home,
  Visibility,
  Message,
  TrendingUp,
  Edit,
  Analytics,
  AttachMoney,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';

const SellerDashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [myListings, setMyListings] = useState([
    {
      id: 1,
      title: "Beautiful 3BR Home in Naperville",
      price: 425000,
      views: 234,
      favorites: 12,
      inquiries: 8,
      status: "active",
      daysOnMarket: 15
    },
    {
      id: 2,
      title: "Modern Condo in Downtown Chicago",
      price: 350000,
      views: 189,
      favorites: 7,
      inquiries: 5,
      status: "pending",
      daysOnMarket: 8
    }
  ]);
  const [totalViews, setTotalViews] = useState(423);
  const [totalInquiries, setTotalInquiries] = useState(13);
  const [unreadMessages, setUnreadMessages] = useState(5);

  const StatCard: React.FC<{
    title: string;
    value: string | number;
    icon: React.ReactNode;
    color: string;
    subtitle?: string;
    onClick?: () => void;
  }> = ({ title, value, icon, color, subtitle, onClick }) => (
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
              {subtitle && (
                <Typography variant="caption" color="text.secondary">
                  {subtitle}
                </Typography>
              )}
            </Box>
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  );

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'pending': return 'warning';
      case 'sold': return 'info';
      default: return 'default';
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
            Manage your property listings and track performance with detailed analytics.
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => navigate('/properties/create')}
              size="large"
            >
              List New Property
            </Button>
            <Button
              variant="outlined"
              startIcon={<Analytics />}
              onClick={() => navigate('/analytics')}
              size="large"
            >
              View Analytics
            </Button>
            <Button
              variant="outlined"
              startIcon={<Message />}
              onClick={() => navigate('/messages')}
              size="large"
            >
              Messages ({unreadMessages})
            </Button>
          </Box>
        </Box>
      </motion.div>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Listings"
            value={myListings.filter(l => l.status === 'active').length}
            icon={<Home />}
            color="#2196f3"
            subtitle="Properties for sale"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Views"
            value={totalViews}
            icon={<Visibility />}
            color="#4caf50"
            subtitle="This month"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Inquiries"
            value={totalInquiries}
            icon={<Message />}
            color="#ff9800"
            subtitle="Potential buyers"
            onClick={() => navigate('/messages')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Avg. Days on Market"
            value={12}
            icon={<TrendingUp />}
            color="#9c27b0"
            subtitle="Current listings"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* My Listings */}
        <Grid item xs={12} lg={8}>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6" component="h2" sx={{ fontWeight: 'bold' }}>
                    My Property Listings
                  </Typography>
                  <Button
                    size="small"
                    onClick={() => navigate('/properties/my-listings')}
                    sx={{ textTransform: 'none' }}
                  >
                    View All
                  </Button>
                </Box>
                
                <List>
                  {myListings.map((listing, index) => (
                    <ListItem
                      key={listing.id}
                      sx={{
                        cursor: 'pointer',
                        borderRadius: 1,
                        '&:hover': { backgroundColor: 'action.hover' },
                        mb: 1,
                        border: '1px solid',
                        borderColor: 'divider'
                      }}
                      onClick={() => navigate(`/properties/${listing.id}`)}
                    >
                      <ListItemAvatar>
                        <Avatar sx={{ bgcolor: 'primary.main' }}>
                          <Home />
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                            <Typography variant="subtitle1" sx={{ fontWeight: 500 }}>
                              {listing.title}
                            </Typography>
                            <Chip
                              label={listing.status.toUpperCase()}
                              size="small"
                              color={getStatusColor(listing.status) as any}
                              variant="outlined"
                            />
                          </Box>
                        }
                        secondary={
                          <Box>
                            <Typography variant="h6" color="primary" sx={{ fontWeight: 'bold' }}>
                              ${listing.price.toLocaleString()}
                            </Typography>
                            <Box sx={{ display: 'flex', gap: 2, mt: 1 }}>
                              <Typography variant="caption">
                                👁 {listing.views} views
                              </Typography>
                              <Typography variant="caption">
                                ❤️ {listing.favorites} favorites
                              </Typography>
                              <Typography variant="caption">
                                💬 {listing.inquiries} inquiries
                              </Typography>
                              <Typography variant="caption">
                                📅 {listing.daysOnMarket} days on market
                              </Typography>
                            </Box>
                          </Box>
                        }
                      />
                      <IconButton
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/properties/${listing.id}/edit`);
                        }}
                      >
                        <Edit />
                      </IconButton>
                    </ListItem>
                  ))}
                </List>
                
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<Add />}
                  onClick={() => navigate('/properties/create')}
                  sx={{ mt: 2 }}
                >
                  Add New Property
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Performance & Tips */}
        <Grid item xs={12} lg={4}>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" component="h2" sx={{ fontWeight: 'bold', mb: 2 }}>
                  Performance This Month
                </Typography>
                
                <Box sx={{ mb: 3 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Views Goal</Typography>
                    <Typography variant="body2">423/500</Typography>
                  </Box>
                  <LinearProgress variant="determinate" value={84.6} sx={{ height: 8, borderRadius: 4 }} />
                </Box>
                
                <Box sx={{ mb: 3 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Inquiry Rate</Typography>
                    <Typography variant="body2">3.1%</Typography>
                  </Box>
                  <LinearProgress variant="determinate" value={62} sx={{ height: 8, borderRadius: 4 }} />
                </Box>
                
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<Analytics />}
                  onClick={() => navigate('/analytics')}
                >
                  Detailed Analytics
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardContent>
                <Typography variant="h6" component="h2" sx={{ fontWeight: 'bold', mb: 2 }}>
                  Selling Tips
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemText
                      primary="Professional Photos"
                      secondary="Properties with professional photos get 40% more views"
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="Competitive Pricing"
                      secondary="Use our neighborhood analysis to price competitively"
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="Quick Responses"
                      secondary="Respond to inquiries within 2 hours for best results"
                    />
                  </ListItem>
                </List>
                <Button
                  fullWidth
                  variant="outlined"
                  onClick={() => navigate('/seller-resources')}
                  sx={{ mt: 2 }}
                >
                  More Selling Tips
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>
    </Box>
  );
};

export default SellerDashboard;
