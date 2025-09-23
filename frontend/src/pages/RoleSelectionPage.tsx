import React from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Chip,
} from '@mui/material';
import {
  Home,
  Business,
  AccountBalance,
  Person,
  ArrowForward,
  ArrowBack,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

interface RoleCardProps {
  title: string;
  description: string;
  icon: React.ReactElement;
  color: string;
  benefits: string[];
  loginPath: string;
  registerPath: string;
}

const RoleCard: React.FC<RoleCardProps> = ({
  title,
  description,
  icon,
  color,
  benefits,
  loginPath,
  registerPath,
}) => {
  const navigate = useNavigate();

  return (
    <motion.div
      whileHover={{ y: -8, scale: 1.02 }}
      transition={{ duration: 0.3 }}
    >
      <Card
        sx={{
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          background: `linear-gradient(135deg, ${color}20 0%, ${color}10 100%)`,
          border: `2px solid ${color}30`,
          borderRadius: 3,
          overflow: 'hidden',
          position: 'relative',
        }}
      >
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            right: 0,
            width: 80,
            height: 80,
            background: `linear-gradient(135deg, ${color}40, ${color}60)`,
            borderRadius: '0 0 0 100%',
            display: 'flex',
            alignItems: 'flex-end',
            justifyContent: 'flex-start',
            pl: 2,
            pb: 2,
          }}
        >
          {React.cloneElement(icon, { sx: { color: 'white', fontSize: 24 } })}
        </Box>

        <CardContent sx={{ flexGrow: 1, pt: 4 }}>
          <Typography variant="h5" component="h3" gutterBottom sx={{ fontWeight: 'bold', color }}>
            {title}
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            {description}
          </Typography>

          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
              Key Benefits:
            </Typography>
            {benefits.map((benefit, index) => (
              <Chip
                key={index}
                label={benefit}
                size="small"
                sx={{
                  m: 0.5,
                  backgroundColor: `${color}20`,
                  color: color,
                  fontWeight: 500,
                }}
              />
            ))}
          </Box>

          <Box sx={{ display: 'flex', gap: 1, mt: 'auto' }}>
            <Button
              variant="contained"
              fullWidth
              onClick={() => navigate(loginPath)}
              sx={{
                background: `linear-gradient(45deg, ${color}, ${color}CC)`,
                '&:hover': {
                  background: `linear-gradient(45deg, ${color}CC, ${color}AA)`,
                },
              }}
            >
              Login
            </Button>
            <Button
              variant="outlined"
              fullWidth
              onClick={() => navigate(registerPath)}
              sx={{
                borderColor: color,
                color: color,
                '&:hover': {
                  borderColor: color,
                  backgroundColor: `${color}10`,
                },
              }}
            >
              Register
            </Button>
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  );
};

const RoleSelectionPage: React.FC = () => {
  const navigate = useNavigate();

  const roles: RoleCardProps[] = [
    {
      title: 'Property Buyer',
      description: 'Looking to purchase your dream home or investment property? Get AI-powered insights and connect with top buyer agents.',
      icon: <Home />,
      color: '#2196F3',
      benefits: ['AI Property Analysis', 'Market Insights', 'Agent Matching', 'Exclusive Listings'],
      loginPath: '/login/buyer',
      registerPath: '/register/buyer',
    },
    {
      title: 'Property Seller',
      description: 'Ready to sell your property? Get accurate valuations and connect with experienced seller agents to maximize your returns.',
      icon: <Business />,
      color: '#FF9800',
      benefits: ['Property Valuation', 'Market Analysis', 'Agent Support', 'Premium Listings'],
      loginPath: '/login/seller',
      registerPath: '/register/seller',
    },
    {
      title: 'Buyer Agent',
      description: 'Professional real estate agent helping buyers find their perfect property. Access advanced tools and client management features.',
      icon: <AccountBalance />,
      color: '#4CAF50',
      benefits: ['Client Management', 'Lead Generation', 'AI Tools', 'Commission Tracking'],
      loginPath: '/login/buyer-agent',
      registerPath: '/register/buyer-agent',
    },
    {
      title: 'Seller Agent',
      description: 'Professional real estate agent helping sellers get the best value. Use AI-powered market analysis and listing optimization.',
      icon: <Person />,
      color: '#9C27B0',
      benefits: ['Listing Tools', 'Market Analytics', 'Client Portal', 'Performance Reports'],
      loginPath: '/login/seller-agent',
      registerPath: '/register/seller-agent',
    },
  ];

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        py: 8,
      }}
    >
      <Container maxWidth="xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          {/* Header */}
          <Box sx={{ textAlign: 'center', mb: 6 }}>
            <Button
              startIcon={<ArrowBack />}
              onClick={() => navigate('/')}
              sx={{ 
                mb: 4, 
                color: 'white', 
                alignSelf: 'flex-start',
                '&:hover': { backgroundColor: 'rgba(255,255,255,0.1)' }
              }}
            >
              Back to Home
            </Button>
            <Typography
              variant="h2"
              component="h1"
              gutterBottom
              sx={{
                fontWeight: 700,
                color: 'white',
                textShadow: '2px 2px 4px rgba(0,0,0,0.3)',
                mb: 2,
              }}
            >
              Choose Your Role
            </Typography>
            <Typography
              variant="h6"
              color="rgba(255,255,255,0.9)"
              sx={{ maxWidth: 800, mx: 'auto', mb: 4 }}
            >
              Select your role to access tailored features and connect with the right professionals
              in our AI-powered real estate platform
            </Typography>
          </Box>

          {/* Role Cards */}
          <Grid container spacing={4}>
            {roles.map((role, index) => (
              <Grid item xs={12} sm={6} lg={3} key={index}>
                <RoleCard {...role} />
              </Grid>
            ))}
          </Grid>

          {/* General Login */}
          <Box sx={{ textAlign: 'center', mt: 6 }}>
            <Paper
              sx={{
                p: 3,
                background: 'rgba(255,255,255,0.1)',
                backdropFilter: 'blur(10px)',
                borderRadius: 3,
                maxWidth: 500,
                mx: 'auto',
              }}
            >
              <Typography variant="h6" color="white" gutterBottom>
                Already have an account?
              </Typography>
              <Typography variant="body2" color="rgba(255,255,255,0.8)" sx={{ mb: 2 }}>
                Use the general login if you're unsure of your role
              </Typography>
              <Button
                variant="outlined"
                endIcon={<ArrowForward />}
                onClick={() => navigate('/login')}
                sx={{
                  borderColor: 'white',
                  color: 'white',
                  '&:hover': {
                    borderColor: 'white',
                    backgroundColor: 'rgba(255,255,255,0.1)',
                  },
                }}
              >
                General Login
              </Button>
            </Paper>
          </Box>
        </motion.div>
      </Container>
    </Box>
  );
};

export default RoleSelectionPage;