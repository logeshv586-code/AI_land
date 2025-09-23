import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  AppBar,
  Toolbar,
} from '@mui/material';
import {
  Check,
  Star,
  TrendingUp,
  Visibility,
  Analytics,
  VideoCall,
  Campaign,
  Diamond,
  ArrowBack,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

interface SubscriptionPlan {
  id: string;
  name: string;
  price: number;
  billing_period: 'monthly' | 'yearly';
  features: string[];
  limits: {
    listings?: number;
    featured_listings?: number;
    analytics?: boolean;
    video_tours?: boolean;
    banner_ads?: boolean;
    priority_support?: boolean;
  };
  popular?: boolean;
  current?: boolean;
}

const SubscriptionPlansPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [plans, setPlans] = useState<SubscriptionPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedPlan, setSelectedPlan] = useState<SubscriptionPlan | null>(null);
  const [upgradeDialogOpen, setUpgradeDialogOpen] = useState(false);
  const [processingPayment, setProcessingPayment] = useState(false);

  useEffect(() => {
    fetchSubscriptionPlans();
  }, []);

  const fetchSubscriptionPlans = async () => {
    try {
      setLoading(true);
      // TODO: Replace with actual API call
      // Mock data for now
      const mockPlans: SubscriptionPlan[] = [
        {
          id: 'basic',
          name: 'Basic Plan',
          price: 49,
          billing_period: 'monthly',
          features: [
            'Up to 10 property listings',
            'Standard visibility',
            'Basic lead access',
            'Email support',
            'Mobile app access'
          ],
          limits: {
            listings: 10,
            featured_listings: 0,
            analytics: false,
            video_tours: false,
            banner_ads: false,
            priority_support: false,
          },
          current: user?.subscription_plan === 'basic'
        },
        {
          id: 'pro',
          name: 'Pro Plan',
          price: 99,
          billing_period: 'monthly',
          features: [
            'Unlimited property listings',
            'Featured listings (priority placement)',
            'Advanced analytics (views, clicks, leads)',
            'Access to verified buyer leads',
            'Priority email support',
            'Mobile app access',
            'Lead management tools'
          ],
          limits: {
            listings: -1, // unlimited
            featured_listings: 5,
            analytics: true,
            video_tours: false,
            banner_ads: false,
            priority_support: true,
          },
          popular: true,
          current: user?.subscription_plan === 'pro'
        },
        {
          id: 'premium',
          name: 'Premium Plan',
          price: 199,
          billing_period: 'monthly',
          features: [
            'All Pro features',
            'Banner placement on homepage',
            'Exclusive leads (priority notifications)',
            'Dedicated account manager',
            'Custom branding options',
            'API access',
            'White-label solutions'
          ],
          limits: {
            listings: -1, // unlimited
            featured_listings: -1, // unlimited
            analytics: true,
            video_tours: true,
            banner_ads: true,
            priority_support: true,
          },
          current: user?.subscription_plan === 'premium'
        }
      ];
      
      setPlans(mockPlans);
    } catch (err: any) {
      setError('Failed to load pricing plans');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPlan = (plan: SubscriptionPlan) => {
    if (!user) {
      // For non-authenticated users, show a dialog prompting them to register/login
      setError('Please create an account or login to select a plan.');
      setTimeout(() => {
        navigate('/register');
      }, 2000);
      return;
    }

    if (plan.current) {
      return; // Already on this plan
    }

    setSelectedPlan(plan);
    setUpgradeDialogOpen(true);
  };

  const handleUpgrade = async () => {
    if (!selectedPlan) return;

    try {
      setProcessingPayment(true);
      // TODO: Integrate with Stripe/PayPal
      // For now, just simulate the process
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // TODO: Call API to update subscription
      setError('Payment integration coming soon! Please contact support to upgrade your plan.');
      setUpgradeDialogOpen(false);
    } catch (err: any) {
      setError('Payment failed. Please try again.');
    } finally {
      setProcessingPayment(false);
    }
  };

  const getPlanIcon = (planId: string) => {
    switch (planId) {
      case 'basic':
        return <Star color="primary" />;
      case 'pro':
        return <TrendingUp color="secondary" />;
      case 'premium':
        return <Diamond sx={{ color: 'gold' }} />;
      default:
        return <Star />;
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(price);
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4, textAlign: 'center' }}>
        <CircularProgress />
        <Typography sx={{ mt: 2 }}>Loading pricing plans...</Typography>
      </Container>
    );
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* Public Navigation Header - only show when not using Layout */}
      <AppBar position="static" elevation={1} sx={{ backgroundColor: 'white', color: 'text.primary', mb: 4 }}>
        <Toolbar>
          <Button
            startIcon={<ArrowBack />}
            onClick={() => navigate('/')}
            sx={{ mr: 2 }}
          >
            Back to Home
          </Button>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, color: 'primary.main', fontWeight: 'bold' }}>
            Land Analysis AI - Pricing
          </Typography>
          {!user && (
            <>
              <Button color="primary" onClick={() => navigate('/login')} sx={{ mr: 1 }}>
                Login
              </Button>
              <Button variant="contained" onClick={() => navigate('/register')}>
                Get Started
              </Button>
            </>
          )}
          {user && (
            <Button color="primary" onClick={() => navigate('/dashboard')}>
              Go to Dashboard
            </Button>
          )}
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ textAlign: 'center', mb: 6 }}>
        <Typography variant="h3" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
          Pricing Plans
        </Typography>
        <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
          Unlock powerful features to grow your real estate business
        </Typography>
        {user && (
          <Chip
            label={`Current Plan: ${user.subscription_plan?.toUpperCase() || 'FREE'}`}
            color="primary"
            variant="outlined"
          />
        )}
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {/* Plans Grid */}
      <Grid container spacing={4} justifyContent="center">
        {plans.map((plan, index) => (
          <Grid item xs={12} md={4} key={plan.id}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
            >
              <Card
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  position: 'relative',
                  border: plan.popular ? '2px solid' : '1px solid',
                  borderColor: plan.popular ? 'secondary.main' : 'divider',
                  '&:hover': {
                    transform: 'translateY(-8px)',
                    boxShadow: 6,
                  },
                  transition: 'all 0.3s ease-in-out',
                }}
              >
                {/* Popular Badge */}
                {plan.popular && (
                  <Chip
                    label="Most Popular"
                    color="secondary"
                    size="small"
                    sx={{
                      position: 'absolute',
                      top: -10,
                      left: '50%',
                      transform: 'translateX(-50%)',
                      zIndex: 1,
                    }}
                  />
                )}

                {/* Current Plan Badge */}
                {plan.current && (
                  <Chip
                    label="Current Plan"
                    color="success"
                    size="small"
                    sx={{
                      position: 'absolute',
                      top: 16,
                      right: 16,
                      zIndex: 1,
                    }}
                  />
                )}

                <CardContent sx={{ 
                  flexGrow: 1, 
                  p: 4, 
                  display: 'flex', 
                  flexDirection: 'column',
                  minHeight: '500px'
                }}>
                  {/* Plan Header */}
                  <Box sx={{ textAlign: 'center', mb: 3, minHeight: '120px', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                    <Box sx={{ mb: 2, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                      {getPlanIcon(plan.id)}
                    </Box>
                    <Typography 
                      variant="h4" 
                      component="h2" 
                      gutterBottom 
                      sx={{ 
                        fontWeight: 'bold',
                        textAlign: 'center',
                        lineHeight: 1.2,
                        mb: 2
                      }}
                    >
                      {plan.name}
                    </Typography>
                    <Box sx={{ 
                      display: 'flex', 
                      alignItems: 'baseline', 
                      justifyContent: 'center',
                      gap: 0.5
                    }}>
                      <Typography 
                        variant="h3" 
                        component="span" 
                        sx={{ 
                          fontWeight: 'bold', 
                          color: 'primary.main',
                          textAlign: 'center'
                        }}
                      >
                        {formatPrice(plan.price)}
                      </Typography>
                      <Typography 
                        variant="h6" 
                        component="span" 
                        color="text.secondary" 
                        sx={{ ml: 1 }}
                      >
                        /month
                      </Typography>
                    </Box>
                  </Box>

                  {/* Features List */}
                  <List sx={{ mb: 3, flexGrow: 1 }}>
                    {plan.features.map((feature, featureIndex) => (
                      <ListItem key={featureIndex} sx={{ px: 0, py: 0.5 }}>
                        <ListItemIcon sx={{ minWidth: 32 }}>
                          <Check color="success" fontSize="small" />
                        </ListItemIcon>
                        <ListItemText
                          primary={feature}
                          primaryTypographyProps={{ variant: 'body2' }}
                        />
                      </ListItem>
                    ))}
                  </List>

                  {/* Plan Limits */}
                  <Box sx={{ mb: 3, p: 2, backgroundColor: 'grey.50', borderRadius: 1 }}>
                    <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
                      Plan Limits:
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      <Chip
                        size="small"
                        label={`${plan.limits.listings === -1 ? 'Unlimited' : plan.limits.listings} Listings`}
                        variant="outlined"
                      />
                      {plan.limits.featured_listings !== undefined && (
                        <Chip
                          size="small"
                          label={`${plan.limits.featured_listings === -1 ? 'Unlimited' : plan.limits.featured_listings} Featured`}
                          variant="outlined"
                        />
                      )}
                      {plan.limits.analytics && (
                        <Chip size="small" label="Analytics" color="primary" variant="outlined" />
                      )}
                      {plan.limits.video_tours && (
                        <Chip size="small" label="Video Tours" color="secondary" variant="outlined" />
                      )}
                    </Box>
                  </Box>

                  {/* Action Button */}
                  <Button
                    fullWidth
                    variant={plan.current ? "outlined" : plan.popular ? "contained" : "outlined"}
                    color={plan.popular ? "secondary" : "primary"}
                    size="large"
                    disabled={plan.current}
                    onClick={() => handleSelectPlan(plan)}
                    sx={{ 
                      mt: 'auto',
                      alignSelf: 'flex-end'
                    }}
                  >
                    {plan.current ? 'Current Plan' : user ? `Upgrade to ${plan.name}` : `Get Started with ${plan.name}`}
                  </Button>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>
        ))}
      </Grid>

      {/* Additional Info */}
      <Box sx={{ textAlign: 'center', mt: 6 }}>
        <Typography variant="body1" color="text.secondary" paragraph>
          All plans include a 14-day free trial. Cancel anytime.
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Need a custom solution? <Button variant="text" size="small">Contact Sales</Button>
        </Typography>
      </Box>

      {/* Upgrade Dialog */}
      <Dialog open={upgradeDialogOpen} onClose={() => setUpgradeDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          Upgrade to {selectedPlan?.name}
        </DialogTitle>
        <DialogContent>
          {selectedPlan && (
            <Box>
              <Typography variant="body1" paragraph>
                You're about to upgrade to the {selectedPlan.name} for {formatPrice(selectedPlan.price)}/month.
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Your new plan will be active immediately, and you'll be charged {formatPrice(selectedPlan.price)} today.
              </Typography>
              <Alert severity="info" sx={{ mt: 2 }}>
                Payment integration is coming soon! Please contact our support team to complete your upgrade.
              </Alert>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUpgradeDialogOpen(false)}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleUpgrade}
            disabled={processingPayment}
            startIcon={processingPayment ? <CircularProgress size={20} /> : null}
          >
            {processingPayment ? 'Processing...' : 'Upgrade Now'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
    </Box>
  );
};

export default SubscriptionPlansPage;
