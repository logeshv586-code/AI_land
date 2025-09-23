import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  TextField,
  Button,
  Paper,
  Chip,
  Alert,
  CircularProgress,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Tooltip,
  IconButton,
} from '@mui/material';
import {
  AttachMoney,
  LocationOn,
  Home,
  CalendarToday,
  SquareFoot,
  TrendingUp,
  Assessment,
  ExpandMore,
  Info,
  Psychology,
  Speed,
  Security,
  Timeline,
  ShowChart,
} from '@mui/icons-material';
import { useForm, Controller } from 'react-hook-form';
import { motion } from 'framer-motion';
import { toast } from 'react-toastify';

interface PropertyValuationForm {
  address: string;
  latitude?: number;
  longitude?: number;
  property_type: string;
  beds: number;
  baths: number;
  sqft: number;
  year_built: number;
  lot_size?: number;
}

interface ValuationResult {
  id: number;
  predicted_value: number;
  value_uncertainty: number;
  price_per_sqft: number;
  comparable_sales_count: number;
  days_on_market_avg: number;
  valuation_date: string;
  confidence_score: number;
  explanation?: {
    base_value: number;
    prediction_value: number;
    top_positive_features: Array<{
      feature_name: string;
      attribution_value: number;
      feature_value: number;
      impact_description: string;
    }>;
    top_negative_features: Array<{
      feature_name: string;
      attribution_value: number;
      feature_value: number;
      impact_description: string;
    }>;
  };
}

const PropertyValuationPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ValuationResult | null>(null);
  const [showExplanation, setShowExplanation] = useState(false);

  const { control, handleSubmit, formState: { errors }, reset } = useForm<PropertyValuationForm>({
    defaultValues: {
      property_type: 'residential',
      beds: 3,
      baths: 2,
      sqft: 1500,
      year_built: 2000,
      lot_size: 0.25,
    }
  });

  const onSubmit = async (data: PropertyValuationForm) => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Mock result
      const mockResult: ValuationResult = {
        id: Math.floor(Math.random() * 10000),
        predicted_value: 275000 + Math.random() * 100000,
        value_uncertainty: 15000 + Math.random() * 10000,
        price_per_sqft: 183.33,
        comparable_sales_count: 12,
        days_on_market_avg: 45.5,
        valuation_date: new Date().toISOString(),
        confidence_score: 0.85 + Math.random() * 0.1,
        explanation: {
          base_value: 192500,
          prediction_value: 275000,
          top_positive_features: [
            {
              feature_name: 'sqft',
              attribution_value: 45000,
              feature_value: data.sqft,
              impact_description: `Property size (${data.sqft} sq ft) increases property value by $45,000`
            },
            {
              feature_name: 'location',
              attribution_value: 25000,
              feature_value: 0.85,
              impact_description: 'Excellent location increases property value by $25,000'
            },
            {
              feature_name: 'beds',
              attribution_value: 12000,
              feature_value: data.beds,
              impact_description: `${data.beds} bedrooms increases property value by $12,000`
            }
          ],
          top_negative_features: [
            {
              feature_name: 'age',
              attribution_value: -8000,
              feature_value: 2024 - data.year_built,
              impact_description: `Property age (${2024 - data.year_built} years) decreases property value by $8,000`
            }
          ]
        }
      };

      setResult(mockResult);
      toast.success('Property valuation completed successfully!');
    } catch (error) {
      toast.error('Failed to get property valuation. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return '#10b981';
    if (confidence >= 0.6) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Box sx={{ mb: 4 }}>
          <Typography variant="h3" component="h1" gutterBottom sx={{ fontWeight: 700, color: '#1e293b' }}>
            💰 Property Valuation (AVM)
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
            AI-powered automated valuation model with uncertainty estimation
          </Typography>
          <Alert severity="info" sx={{ mb: 3 }}>
            <strong>Advanced ML:</strong> Our RandomForest model analyzes 40+ features to provide accurate property valuations with confidence intervals.
          </Alert>
        </Box>
      </motion.div>

      <Grid container spacing={4}>
        {/* Input Form */}
        <Grid item xs={12} lg={5}>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <Card>
              <CardContent>
                <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, display: 'flex', alignItems: 'center' }}>
                  <Home sx={{ mr: 1 }} />
                  Property Details
                </Typography>
                
                <Box component="form" onSubmit={handleSubmit(onSubmit)} sx={{ mt: 2 }}>
                  <Grid container spacing={3}>
                    <Grid item xs={12}>
                      <Controller
                        name="address"
                        control={control}
                        rules={{ required: 'Address is required' }}
                        render={({ field }) => (
                          <TextField
                            {...field}
                            fullWidth
                            label="Property Address"
                            placeholder="123 Main St, City, State"
                            error={!!errors.address}
                            helperText={errors.address?.message}
                            InputProps={{
                              startAdornment: <LocationOn sx={{ mr: 1, color: 'text.secondary' }} />
                            }}
                          />
                        )}
                      />
                    </Grid>

                    <Grid item xs={6}>
                      <Controller
                        name="beds"
                        control={control}
                        rules={{ required: 'Bedrooms is required', min: 1 }}
                        render={({ field }) => (
                          <TextField
                            {...field}
                            fullWidth
                            type="number"
                            label="Bedrooms"
                            error={!!errors.beds}
                            helperText={errors.beds?.message}
                          />
                        )}
                      />
                    </Grid>

                    <Grid item xs={6}>
                      <Controller
                        name="baths"
                        control={control}
                        rules={{ required: 'Bathrooms is required', min: 1 }}
                        render={({ field }) => (
                          <TextField
                            {...field}
                            fullWidth
                            type="number"
                            label="Bathrooms"
                            error={!!errors.baths}
                            helperText={errors.baths?.message}
                          />
                        )}
                      />
                    </Grid>

                    <Grid item xs={6}>
                      <Controller
                        name="sqft"
                        control={control}
                        rules={{ required: 'Square footage is required', min: 100 }}
                        render={({ field }) => (
                          <TextField
                            {...field}
                            fullWidth
                            type="number"
                            label="Square Feet"
                            error={!!errors.sqft}
                            helperText={errors.sqft?.message}
                            InputProps={{
                              startAdornment: <SquareFoot sx={{ mr: 1, color: 'text.secondary' }} />
                            }}
                          />
                        )}
                      />
                    </Grid>

                    <Grid item xs={6}>
                      <Controller
                        name="year_built"
                        control={control}
                        rules={{ required: 'Year built is required', min: 1800, max: new Date().getFullYear() }}
                        render={({ field }) => (
                          <TextField
                            {...field}
                            fullWidth
                            type="number"
                            label="Year Built"
                            error={!!errors.year_built}
                            helperText={errors.year_built?.message}
                            InputProps={{
                              startAdornment: <CalendarToday sx={{ mr: 1, color: 'text.secondary' }} />
                            }}
                          />
                        )}
                      />
                    </Grid>

                    <Grid item xs={12}>
                      <Controller
                        name="lot_size"
                        control={control}
                        render={({ field }) => (
                          <TextField
                            {...field}
                            fullWidth
                            type="number"
                            label="Lot Size (acres)"
                            placeholder="0.25"
                            inputProps={{ step: 0.01 }}
                          />
                        )}
                      />
                    </Grid>

                    <Grid item xs={12}>
                      <Button
                        type="submit"
                        variant="contained"
                        size="large"
                        fullWidth
                        disabled={loading}
                        startIcon={loading ? <CircularProgress size={20} /> : <Assessment />}
                        sx={{ py: 1.5 }}
                      >
                        {loading ? 'Analyzing Property...' : 'Get Property Valuation'}
                      </Button>
                    </Grid>
                  </Grid>
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Results */}
        <Grid item xs={12} lg={7}>
          {result ? (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
            >
              {/* Main Valuation Result */}
              <Card sx={{ mb: 3 }}>
                <CardContent>
                  <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, display: 'flex', alignItems: 'center' }}>
                    <AttachMoney sx={{ mr: 1 }} />
                    Valuation Result
                  </Typography>
                  
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                      <Paper sx={{ p: 3, textAlign: 'center', bgcolor: '#f0f9ff' }}>
                        <Typography variant="h3" sx={{ fontWeight: 700, color: '#0369a1' }}>
                          {formatCurrency(result.predicted_value)}
                        </Typography>
                        <Typography variant="h6" color="text.secondary">
                          Estimated Value
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                          ± {formatCurrency(result.value_uncertainty)} uncertainty
                        </Typography>
                      </Paper>
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
                      <List dense>
                        <ListItem>
                          <ListItemIcon><SquareFoot /></ListItemIcon>
                          <ListItemText 
                            primary="Price per sq ft" 
                            secondary={`$${result.price_per_sqft.toFixed(2)}`}
                          />
                        </ListItem>
                        <ListItem>
                          <ListItemIcon><Timeline /></ListItemIcon>
                          <ListItemText 
                            primary="Comparable Sales" 
                            secondary={`${result.comparable_sales_count} properties`}
                          />
                        </ListItem>
                        <ListItem>
                          <ListItemIcon><Speed /></ListItemIcon>
                          <ListItemText 
                            primary="Avg Days on Market" 
                            secondary={`${result.days_on_market_avg} days`}
                          />
                        </ListItem>
                        <ListItem>
                          <ListItemIcon><Security /></ListItemIcon>
                          <ListItemText 
                            primary="Confidence Score" 
                            secondary={
                              <Chip
                                label={`${(result.confidence_score * 100).toFixed(1)}%`}
                                size="small"
                                sx={{
                                  bgcolor: getConfidenceColor(result.confidence_score),
                                  color: 'white',
                                  fontWeight: 600,
                                }}
                              />
                            }
                          />
                        </ListItem>
                      </List>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>

              {/* AI Explanation */}
              {result.explanation && (
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                      <Typography variant="h5" sx={{ fontWeight: 600, display: 'flex', alignItems: 'center' }}>
                        <Psychology sx={{ mr: 1 }} />
                        AI Explanation
                      </Typography>
                      <Tooltip title="SHAP-based feature attributions explain how each property characteristic affects the valuation">
                        <IconButton size="small">
                          <Info />
                        </IconButton>
                      </Tooltip>
                    </Box>

                    <Accordion>
                      <AccordionSummary expandIcon={<ExpandMore />}>
                        <Typography sx={{ fontWeight: 600 }}>
                          🚀 Value Drivers (What increases property value)
                        </Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <List>
                          {result.explanation.top_positive_features.map((feature, index) => (
                            <ListItem key={index}>
                              <ListItemIcon>
                                <TrendingUp sx={{ color: '#10b981' }} />
                              </ListItemIcon>
                              <ListItemText
                                primary={feature.impact_description}
                                secondary={`Attribution: +${formatCurrency(feature.attribution_value)}`}
                              />
                            </ListItem>
                          ))}
                        </List>
                      </AccordionDetails>
                    </Accordion>

                    <Accordion>
                      <AccordionSummary expandIcon={<ExpandMore />}>
                        <Typography sx={{ fontWeight: 600 }}>
                          ⚠️ Value Detractors (What decreases property value)
                        </Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <List>
                          {result.explanation.top_negative_features.map((feature, index) => (
                            <ListItem key={index}>
                              <ListItemIcon>
                                <ShowChart sx={{ color: '#ef4444', transform: 'rotate(180deg)' }} />
                              </ListItemIcon>
                              <ListItemText
                                primary={feature.impact_description}
                                secondary={`Attribution: ${formatCurrency(feature.attribution_value)}`}
                              />
                            </ListItem>
                          ))}
                        </List>
                      </AccordionDetails>
                    </Accordion>
                  </CardContent>
                </Card>
              )}
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
            >
              <Paper sx={{ p: 6, textAlign: 'center', bgcolor: '#f8fafc' }}>
                <AttachMoney sx={{ fontSize: 80, color: '#cbd5e1', mb: 2 }} />
                <Typography variant="h5" color="text.secondary" gutterBottom>
                  Ready for Property Valuation
                </Typography>
                <Typography color="text.secondary">
                  Enter property details to get an AI-powered valuation with detailed explanations
                </Typography>
              </Paper>
            </motion.div>
          )}
        </Grid>
      </Grid>
    </Container>
  );
};

export default PropertyValuationPage;
