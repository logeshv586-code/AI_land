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
  Alert,
} from '@mui/material';
import {
  Add,
  Home,
  People,
  Message,
  TrendingUp,
  Star,
  Analytics,
  AttachMoney,
  Upgrade,
  Warning,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';

const AgentDashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [subscriptionStatus, setSubscriptionStatus] = useState('active'); // active, expiring, expired
  const [subscriptionPlan, setSubscriptionPlan] = useState('pro');
  const [daysUntilExpiry, setDaysUntilExpiry] = useState(7);
  const [clientListings, setClientListings] = useState(15);
  const [activeLeads, setActiveLeads] = useState(8);
  const [monthlyCommission, setMonthlyCommission] = useState(12500);
  const [unreadMessages, setUnreadMessages] = useState(12);

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

  const isSellerAgent = user?.user_role === 'seller_agent';

  return (
    <Box>
      {/* Pricing Alert */}
      {subscriptionStatus === 'expiring' && (
        <Alert 
          severity="warning" 
          sx={{ mb: 3 }}
          action={
            <Button color="inherit" size="small" onClick={() => navigate('/subscription')}>
              RENEW
            </Button>
          }
        >
          Your {subscriptionPlan} plan expires in {daysUntilExpiry} days. Renew now to avoid service interruption.
        </Alert>
      )}

      {/* Welcome Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
            <Box>
              <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
                Welcome back, Agent {user?.first_name || user?.username}!
              </Typography>
              <Typography variant="body1" color="text.secondary">
                {isSellerAgent ? 'Manage your seller clients and property listings' : 'Connect buyers with their perfect homes'}
              </Typography>
            </Box>
            <Chip
              label={`${subscriptionPlan.toUpperCase()} PLAN`}
              color="primary"
              variant="outlined"
              icon={<Star />}
            />
          </Box>
          
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            {isSellerAgent ? (
              <>
                <Button
                  variant="contained"
                  startIcon={<Add />}
                  onClick={() => navigate('/properties/create')}
                  size="large"
                >
                  List Property
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<People />}
                  onClick={() => navigate('/clients')}
                  size="large"
                >
                  Manage Clients
                </Button>
              </>
            ) : (
              <>
                <Button
                  variant="contained"
                  startIcon={<People />}
                  onClick={() => navigate('/leads')}
                  size="large"
                >
                  View Leads
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Home />}
                  onClick={() => navigate('/properties')}
                  size="large"
                >
                  Browse Properties
                </Button>
              </>
            )}
            <Button
              variant="outlined"
              startIcon={<Analytics />}
              onClick={() => navigate('/agent-analytics')}
              size="large"
            >
              Analytics
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
            title={isSellerAgent ? "Client Listings" : "Active Leads"}
            value={isSellerAgent ? clientListings : activeLeads}
            icon={isSellerAgent ? <Home /> : <People />}
            color="#2196f3"
            subtitle={isSellerAgent ? "Properties managed" : "Potential buyers"}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Monthly Commission"
            value={`$${monthlyCommission.toLocaleString()}`}
            icon={<AttachMoney />}
            color="#4caf50"
            subtitle="This month"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Messages"
            value={unreadMessages}
            icon={<Message />}
            color="#ff9800"
            subtitle="Unread"
            onClick={() => navigate('/messages')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Client Satisfaction"
            value="4.8/5"
            icon={<Star />}
            color="#9c27b0"
            subtitle="Average rating"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Recent Activity */}
        <Grid item xs={12} lg={8}>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <Card>
              <CardContent>
                <Typography variant="h6" component="h2" sx={{ fontWeight: 'bold', mb: 2 }}>
                  Recent Activity
                </Typography>
                
                <List>
                  <ListItem>
                    <ListItemAvatar>
                      <Avatar sx={{ bgcolor: 'success.main' }}>
                        <Home />
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary="New property inquiry"
                      secondary="John Smith interested in 123 Main St, Naperville - 2 hours ago"
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemAvatar>
                      <Avatar sx={{ bgcolor: 'info.main' }}>
                        <Message />
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary="Message from client"
                      secondary="Sarah Johnson asking about closing timeline - 4 hours ago"
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemAvatar>
                      <Avatar sx={{ bgcolor: 'warning.main' }}>
                        <TrendingUp />
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary="Property price updated"
                      secondary="456 Oak Ave price reduced to $425,000 - 1 day ago"
                    />
                  </ListItem>
                </List>
                
                <Button
                  fullWidth
                  variant="outlined"
                  onClick={() => navigate('/activity')}
                  sx={{ mt: 2 }}
                >
                  View All Activity
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Pricing & Performance */}
        <Grid item xs={12} lg={4}>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" component="h2" sx={{ fontWeight: 'bold', mb: 2 }}>
                  Plan Usage
                </Typography>
                
                <Box sx={{ mb: 3 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Featured Listings</Typography>
                    <Typography variant="body2">3/5</Typography>
                  </Box>
                  <LinearProgress variant="determinate" value={60} sx={{ height: 8, borderRadius: 4 }} />
                </Box>
                
                <Box sx={{ mb: 3 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Analytics Views</Typography>
                    <Typography variant="body2">750/1000</Typography>
                  </Box>
                  <LinearProgress variant="determinate" value={75} sx={{ height: 8, borderRadius: 4 }} />
                </Box>
                
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<Upgrade />}
                  onClick={() => navigate('/subscription')}
                  sx={{ mb: 1 }}
                >
                  Upgrade Plan
                </Button>
                
                <Button
                  fullWidth
                  variant="text"
                  onClick={() => navigate('/subscription')}
                  size="small"
                >
                  Manage Pricing
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardContent>
                <Typography variant="h6" component="h2" sx={{ fontWeight: 'bold', mb: 2 }}>
                  {isSellerAgent ? 'Seller' : 'Buyer'} Agent Tips
                </Typography>
                <List dense>
                  {isSellerAgent ? (
                    <>
                      <ListItem>
                        <ListItemText
                          primary="Market Analysis"
                          secondary="Use neighborhood quality scores to justify pricing"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText
                          primary="Professional Staging"
                          secondary="Staged homes sell 73% faster than non-staged"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText
                          primary="Featured Listings"
                          secondary="Get 3x more views with featured placement"
                        />
                      </ListItem>
                    </>
                  ) : (
                    <>
                      <ListItem>
                        <ListItemText
                          primary="Quick Response"
                          secondary="Respond to leads within 5 minutes for best conversion"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText
                          primary="Neighborhood Insights"
                          secondary="Share Illinois quality scores with buyers"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText
                          primary="Follow Up"
                          secondary="Follow up with leads within 24 hours"
                        />
                      </ListItem>
                    </>
                  )}
                </List>
                <Button
                  fullWidth
                  variant="outlined"
                  onClick={() => navigate('/agent-resources')}
                  sx={{ mt: 2 }}
                >
                  More Resources
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AgentDashboard;
