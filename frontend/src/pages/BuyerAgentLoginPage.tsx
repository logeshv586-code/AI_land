import React, { useState } from 'react';
import {
  Box,
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Link,
  Alert,
  InputAdornment,
  IconButton,
  Divider,
  Card,
  CardContent,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Person,
  Lock,
  ArrowBack,
  AccountBalance,
  People,
  Analytics,
  Star,
} from '@mui/icons-material';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';

interface LoginFormData {
  username: string;
  password: string;
}

const BuyerAgentLoginPage: React.FC = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>();

  const onSubmit = async (data: LoginFormData) => {
    setError('');
    setLoading(true);

    try {
      const success = await login(data.username, data.password);
      if (success) {
        navigate('/dashboard');
      }
    } catch (err: any) {
      setError(err.message || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleClickShowPassword = () => {
    setShowPassword(!showPassword);
  };

  const features = [
    {
      icon: <People sx={{ color: '#4CAF50' }} />,
      title: 'Client Management',
      description: 'Comprehensive client portal and lead tracking'
    },
    {
      icon: <Analytics sx={{ color: '#4CAF50' }} />,
      title: 'AI-Powered Tools',
      description: 'Advanced analytics and market insights'
    },
    {
      icon: <Star sx={{ color: '#4CAF50' }} />,
      title: 'Commission Tracking',
      description: 'Real-time earnings and performance metrics'
    }
  ];

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #4CAF50 0%, #388E3C 100%)',
        display: 'flex',
        py: 4,
      }}
    >
      <Container maxWidth="lg">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <Box sx={{ display: 'flex', gap: 4, alignItems: 'center', minHeight: '90vh' }}>
            {/* Left side - Features */}
            <Box sx={{ flex: 1, color: 'white', display: { xs: 'none', md: 'block' } }}>
              <Button
                startIcon={<ArrowBack />}
                onClick={() => navigate('/role-selection')}
                sx={{ 
                  color: 'white', 
                  mb: 4,
                  '&:hover': { backgroundColor: 'rgba(255,255,255,0.1)' }
                }}
              >
                Back to Role Selection
              </Button>
              
              <Box sx={{ mb: 6 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <AccountBalance sx={{ fontSize: 40, mr: 2 }} />
                  <Typography variant="h3" component="h1" sx={{ fontWeight: 700 }}>
                    Buyer Agent
                  </Typography>
                </Box>
                <Typography variant="h6" sx={{ opacity: 0.9, mb: 4 }}>
                  Professional tools for helping buyers find their dream home
                </Typography>
              </Box>

              {features.map((feature, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.2 + index * 0.1 }}
                >
                  <Card
                    sx={{
                      mb: 3,
                      background: 'rgba(255,255,255,0.1)',
                      backdropFilter: 'blur(10px)',
                      border: '1px solid rgba(255,255,255,0.2)',
                    }}
                  >
                    <CardContent sx={{ display: 'flex', alignItems: 'center' }}>
                      <Box sx={{ mr: 3 }}>
                        {feature.icon}
                      </Box>
                      <Box>
                        <Typography variant="h6" sx={{ color: 'white', fontWeight: 600 }}>
                          {feature.title}
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)' }}>
                          {feature.description}
                        </Typography>
                      </Box>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </Box>

            {/* Right side - Login Form */}
            <Box sx={{ flex: 1, maxWidth: 480 }}>
              <Paper
                elevation={10}
                sx={{
                  p: 4,
                  borderRadius: 3,
                  background: 'rgba(255, 255, 255, 0.95)',
                  backdropFilter: 'blur(10px)',
                }}
              >
                {/* Mobile back button */}
                <Box sx={{ display: { xs: 'block', md: 'none' }, mb: 2 }}>
                  <Button
                    startIcon={<ArrowBack />}
                    onClick={() => navigate('/role-selection')}
                    size="small"
                  >
                    Back
                  </Button>
                </Box>

                {/* Header */}
                <Box sx={{ textAlign: 'center', mb: 4 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
                    <AccountBalance sx={{ fontSize: 48, color: '#4CAF50' }} />
                  </Box>
                  <Typography
                    variant="h4"
                    component="h1"
                    gutterBottom
                    sx={{
                      fontWeight: 700,
                      color: '#4CAF50',
                    }}
                  >
                    Buyer Agent Login
                  </Typography>
                  <Typography variant="body1" color="text.secondary">
                    Access your professional agent dashboard
                  </Typography>
                </Box>

                {/* Error Alert */}
                {error && (
                  <Alert severity="error" sx={{ mb: 3 }}>
                    {error}
                  </Alert>
                )}

                {/* Login Form */}
                <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate>
                  <TextField
                    fullWidth
                    label="Username"
                    margin="normal"
                    autoComplete="username"
                    autoFocus
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <Person color="action" />
                        </InputAdornment>
                      ),
                    }}
                    {...register('username', {
                      required: 'Username is required',
                      minLength: {
                        value: 3,
                        message: 'Username must be at least 3 characters',
                      },
                    })}
                    error={!!errors.username}
                    helperText={errors.username?.message}
                  />

                  <TextField
                    fullWidth
                    label="Password"
                    type={showPassword ? 'text' : 'password'}
                    margin="normal"
                    autoComplete="current-password"
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <Lock color="action" />
                        </InputAdornment>
                      ),
                      endAdornment: (
                        <InputAdornment position="end">
                          <IconButton
                            aria-label="toggle password visibility"
                            onClick={handleClickShowPassword}
                            edge="end"
                          >
                            {showPassword ? <VisibilityOff /> : <Visibility />}
                          </IconButton>
                        </InputAdornment>
                      ),
                    }}
                    {...register('password', {
                      required: 'Password is required',
                      minLength: {
                        value: 6,
                        message: 'Password must be at least 6 characters',
                      },
                    })}
                    error={!!errors.password}
                    helperText={errors.password?.message}
                  />

                  <Button
                    type="submit"
                    fullWidth
                    variant="contained"
                    size="large"
                    disabled={loading}
                    sx={{
                      mt: 3,
                      mb: 2,
                      py: 1.5,
                      background: 'linear-gradient(45deg, #4CAF50, #388E3C)',
                      '&:hover': {
                        background: 'linear-gradient(45deg, #388E3C, #2E7D32)',
                      },
                    }}
                  >
                    {loading ? 'Signing In...' : 'Login as Buyer Agent'}
                  </Button>

                  <Divider sx={{ my: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      New agent?
                    </Typography>
                  </Divider>

                  <Box sx={{ textAlign: 'center' }}>
                    <Link
                      component={RouterLink}
                      to="/register/buyer-agent"
                      variant="body2"
                      sx={{
                        textDecoration: 'none',
                        fontWeight: 500,
                        color: '#4CAF50',
                        '&:hover': {
                          textDecoration: 'underline',
                        },
                      }}
                    >
                      Register as buyer agent
                    </Link>
                  </Box>
                </Box>

                {/* Demo Credentials */}
                <Box
                  sx={{
                    mt: 3,
                    p: 2,
                    backgroundColor: '#E8F5E8',
                    borderRadius: 2,
                    border: '1px solid #C8E6C9',
                  }}
                >
                  <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                    Demo Buyer Agent Credentials:
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Username: <strong>demo_buyer_agent</strong> | Password: <strong>agent123</strong>
                  </Typography>
                </Box>
              </Paper>
            </Box>
          </Box>
        </motion.div>
      </Container>
    </Box>
  );
};

export default BuyerAgentLoginPage;