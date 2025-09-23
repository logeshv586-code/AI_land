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
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  LinearProgress,
  Divider,
  Tooltip,
  IconButton,
} from '@mui/material';
import {
  AutoAwesome,
  LocationOn,
  Home,
  AttachMoney,
  Assessment,
  Recommend,
  Psychology,
  TrendingUp,
  CheckCircle,
  ExpandMore,
  Info,
  Speed,
  Security,
  Star,
  Timeline,
  ShowChart,
} from '@mui/icons-material';
import { useForm, Controller } from 'react-hook-form';
import { motion } from 'framer-motion';
import { toast } from 'react-toastify';

interface ComprehensiveAnalysisForm {
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

interface ComprehensiveResult {
  property_valuation: {
    predicted_value: number;
    value_uncertainty: number;
    price_per_sqft: number;
    confidence_score: number;
  };
  beneficiary_score: {
    overall_score: number;
    value_score: number;
    school_score: number;
    safety_score: number;
    environmental_score: number;
    accessibility_score: number;
  };
  recommendations: Array<{
    id: number;
    address: string;
    predicted_value: number;
    similarity_score: number;
    confidence_score: number;
  }>;
  risk_assessment: {
    risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
    risk_factors: string[];
    opportunities: string[];
  };
  explanation: {
    valuation_factors: Array<{
      feature: string;
      impact: number;
      description: string;
    }>;
    scoring_factors: Array<{
      component: string;
      score: number;
      weight: number;
      description: string;
    }>;
  };
}

const ComprehensiveAnalysisPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ComprehensiveResult | null>(null);
  const [activeStep, setActiveStep] = useState(0);

  const { control, handleSubmit, formState: { errors } } = useForm<ComprehensiveAnalysisForm>({
    defaultValues: {
      property_type: 'residential',
      beds: 3,
      baths: 2,
      sqft: 1500,
      year_built: 2000,
      lot_size: 0.25,
    }
  });

  const analysisSteps = [
    'Property Valuation (AVM)',
    'Beneficiary Scoring',
    'Property Recommendations',
    'Risk Assessment',
    'AI Explanations'
  ];

  const onSubmit = async (data: ComprehensiveAnalysisForm) => {
    setLoading(true);
    setActiveStep(0);
    
    try {
      // Simulate step-by-step analysis
      for (let i = 0; i < analysisSteps.length; i++) {
        await new Promise(resolve => setTimeout(resolve, 800));
        setActiveStep(i + 1);
      }
      
      // Mock comprehensive result
      const mockResult: ComprehensiveResult = {
        property_valuation: {
          predicted_value: 275000 + Math.random() * 100000,
          value_uncertainty: 15000 + Math.random() * 10000,
          price_per_sqft: 183.33,
          confidence_score: 0.85 + Math.random() * 0.1,
        },
        beneficiary_score: {
          overall_score: 65 + Math.random() * 30,
          value_score: 70 + Math.random() * 25,
          school_score: 80 + Math.random() * 20,
          safety_score: 60 + Math.random() * 30,
          environmental_score: 85 + Math.random() * 15,
          accessibility_score: 75 + Math.random() * 20,
        },
        recommendations: Array.from({ length: 5 }, (_, index) => ({
          id: index + 1,
          address: `${Math.floor(Math.random() * 9999) + 1} ${['Main', 'Oak', 'Pine'][Math.floor(Math.random() * 3)]} St`,
          predicted_value: 200000 + Math.random() * 200000,
          similarity_score: 0.6 + Math.random() * 0.4,
          confidence_score: 0.7 + Math.random() * 0.3,
        })),
        risk_assessment: {
          risk_level: ['LOW', 'MEDIUM', 'HIGH'][Math.floor(Math.random() * 3)] as 'LOW' | 'MEDIUM' | 'HIGH',
          risk_factors: [
            'Market volatility in the area',
            'Aging infrastructure',
            'Limited public transportation'
          ],
          opportunities: [
            'Upcoming development projects',
            'Strong school district',
            'Growing employment opportunities'
          ]
        },
        explanation: {
          valuation_factors: [
            { feature: 'Square Footage', impact: 45000, description: `${data.sqft} sq ft increases value significantly` },
            { feature: 'Location Quality', impact: 25000, description: 'Excellent neighborhood location' },
            { feature: 'Property Age', impact: -8000, description: `${2024 - data.year_built} years old reduces value slightly` }
          ],
          scoring_factors: [
            { component: 'School Quality', score: 85, weight: 8.0, description: 'Excellent school district access' },
            { component: 'Safety', score: 70, weight: 6.0, description: 'Good safety ratings' },
            { component: 'Environment', score: 88, weight: 5.0, description: 'Low environmental risks' }
          ]
        }
      };

      setResult(mockResult);
      toast.success('Comprehensive analysis completed successfully!');
    } catch (error) {
      toast.error('Failed to complete comprehensive analysis. Please try again.');
    } finally {
      setLoading(false);
      setActiveStep(0);
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

  const getScoreColor = (score: number) => {
    if (score >= 80) return '#10b981';
    if (score >= 60) return '#f59e0b';
    return '#ef4444';
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'LOW': return '#10b981';
      case 'MEDIUM': return '#f59e0b';
      case 'HIGH': return '#ef4444';
      default: return '#6b7280';
    }
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
            🚀 Comprehensive Analysis
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
            Complete property analysis combining AVM, beneficiary scoring, recommendations, and risk assessment
          </Typography>
          <Alert severity="info" sx={{ mb: 3 }}>
            <strong>All-in-One Analysis:</strong> Get property valuation, investment scoring, similar property recommendations, and AI explanations in one comprehensive report.
          </Alert>
        </Box>
      </motion.div>

      <Grid container spacing={4}>
        {/* Input Form */}
        <Grid item xs={12} lg={4}>
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
                        startIcon={loading ? <CircularProgress size={20} /> : <AutoAwesome />}
                        sx={{ py: 1.5 }}
                      >
                        {loading ? 'Running Analysis...' : 'Start Comprehensive Analysis'}
                      </Button>
                    </Grid>
                  </Grid>
                </Box>
              </CardContent>
            </Card>

            {/* Analysis Progress */}
            {loading && (
              <Card sx={{ mt: 3 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                    Analysis Progress
                  </Typography>
                  <Stepper activeStep={activeStep} orientation="vertical">
                    {analysisSteps.map((label, index) => (
                      <Step key={label}>
                        <StepLabel
                          StepIconComponent={() => (
                            <Box
                              sx={{
                                width: 24,
                                height: 24,
                                borderRadius: '50%',
                                bgcolor: index < activeStep ? '#10b981' : index === activeStep ? '#2563eb' : '#e2e8f0',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                              }}
                            >
                              {index < activeStep ? (
                                <CheckCircle sx={{ fontSize: 16, color: 'white' }} />
                              ) : (
                                <Typography variant="caption" sx={{ color: index === activeStep ? 'white' : '#6b7280', fontWeight: 600 }}>
                                  {index + 1}
                                </Typography>
                              )}
                            </Box>
                          )}
                        >
                          <Typography variant="body2" sx={{ fontWeight: index === activeStep ? 600 : 400 }}>
                            {label}
                          </Typography>
                        </StepLabel>
                      </Step>
                    ))}
                  </Stepper>
                </CardContent>
              </Card>
            )}
          </motion.div>
        </Grid>

        {/* Results */}
        <Grid item xs={12} lg={8}>
          {result ? (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
            >
              {/* Summary Cards */}
              <Grid container spacing={3} sx={{ mb: 3 }}>
                <Grid item xs={12} md={3}>
                  <Card>
                    <CardContent sx={{ textAlign: 'center' }}>
                      <AttachMoney sx={{ fontSize: 40, color: '#2563eb', mb: 1 }} />
                      <Typography variant="h5" sx={{ fontWeight: 700, color: '#2563eb' }}>
                        {formatCurrency(result.property_valuation.predicted_value)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Estimated Value
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                
                <Grid item xs={12} md={3}>
                  <Card>
                    <CardContent sx={{ textAlign: 'center' }}>
                      <Star sx={{ fontSize: 40, color: getScoreColor(result.beneficiary_score.overall_score), mb: 1 }} />
                      <Typography variant="h5" sx={{ fontWeight: 700, color: getScoreColor(result.beneficiary_score.overall_score) }}>
                        {result.beneficiary_score.overall_score.toFixed(1)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Investment Score
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                
                <Grid item xs={12} md={3}>
                  <Card>
                    <CardContent sx={{ textAlign: 'center' }}>
                      <Recommend sx={{ fontSize: 40, color: '#10b981', mb: 1 }} />
                      <Typography variant="h5" sx={{ fontWeight: 700, color: '#10b981' }}>
                        {result.recommendations.length}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Similar Properties
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                
                <Grid item xs={12} md={3}>
                  <Card>
                    <CardContent sx={{ textAlign: 'center' }}>
                      <Security sx={{ fontSize: 40, color: getRiskColor(result.risk_assessment.risk_level), mb: 1 }} />
                      <Typography variant="h5" sx={{ fontWeight: 700, color: getRiskColor(result.risk_assessment.risk_level) }}>
                        {result.risk_assessment.risk_level}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Risk Level
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              {/* Detailed Results */}
              <Accordion defaultExpanded>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography sx={{ fontWeight: 600, display: 'flex', alignItems: 'center' }}>
                    <AttachMoney sx={{ mr: 1 }} />
                    Property Valuation Details
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">Price per sq ft</Typography>
                      <Typography variant="h6">${result.property_valuation.price_per_sqft.toFixed(2)}</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">Confidence</Typography>
                      <Typography variant="h6">{(result.property_valuation.confidence_score * 100).toFixed(1)}%</Typography>
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>

              <Accordion>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography sx={{ fontWeight: 600, display: 'flex', alignItems: 'center' }}>
                    <Assessment sx={{ mr: 1 }} />
                    Investment Score Breakdown
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <List dense>
                    <ListItem>
                      <ListItemText primary="Value Competitiveness" secondary={`${result.beneficiary_score.value_score.toFixed(1)}/100`} />
                      <LinearProgress
                        variant="determinate"
                        value={result.beneficiary_score.value_score}
                        sx={{ width: 100, ml: 2 }}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText primary="School Quality" secondary={`${result.beneficiary_score.school_score.toFixed(1)}/100`} />
                      <LinearProgress
                        variant="determinate"
                        value={result.beneficiary_score.school_score}
                        sx={{ width: 100, ml: 2 }}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText primary="Safety & Security" secondary={`${result.beneficiary_score.safety_score.toFixed(1)}/100`} />
                      <LinearProgress
                        variant="determinate"
                        value={result.beneficiary_score.safety_score}
                        sx={{ width: 100, ml: 2 }}
                      />
                    </ListItem>
                  </List>
                </AccordionDetails>
              </Accordion>

              <Accordion>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography sx={{ fontWeight: 600, display: 'flex', alignItems: 'center' }}>
                    <Psychology sx={{ mr: 1 }} />
                    AI Explanations
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
                    Key Valuation Factors:
                  </Typography>
                  <List dense>
                    {result.explanation.valuation_factors.map((factor, index) => (
                      <ListItem key={index}>
                        <ListItemIcon>
                          <TrendingUp sx={{ color: factor.impact > 0 ? '#10b981' : '#ef4444' }} />
                        </ListItemIcon>
                        <ListItemText
                          primary={factor.description}
                          secondary={`Impact: ${factor.impact > 0 ? '+' : ''}${formatCurrency(factor.impact)}`}
                        />
                      </ListItem>
                    ))}
                  </List>
                </AccordionDetails>
              </Accordion>
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
            >
              <Paper sx={{ p: 6, textAlign: 'center', bgcolor: '#f8fafc' }}>
                <AutoAwesome sx={{ fontSize: 80, color: '#cbd5e1', mb: 2 }} />
                <Typography variant="h5" color="text.secondary" gutterBottom>
                  Ready for Comprehensive Analysis
                </Typography>
                <Typography color="text.secondary">
                  Enter property details to get a complete AI-powered analysis including valuation, scoring, recommendations, and explanations
                </Typography>
              </Paper>
            </motion.div>
          )}
        </Grid>
      </Grid>
    </Container>
  );
};

export default ComprehensiveAnalysisPage;
