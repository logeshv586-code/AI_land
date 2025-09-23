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
  Slider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  LinearProgress,
  Tooltip,
  IconButton,
} from '@mui/material';
import {
  Assessment,
  LocationOn,
  TuneRounded,
  School,
  LocalPolice,
  Park,
  DirectionsCar,
  AttachMoney,
  ExpandMore,
  Info,
  Psychology,
  TrendingUp,
  Star,
  CheckCircle,
  Warning,
} from '@mui/icons-material';
import { useForm, Controller } from 'react-hook-form';
import { motion } from 'framer-motion';
import { toast } from 'react-toastify';

interface BeneficiaryScoringForm {
  location_id?: number;
  property_valuation_id?: number;
  address: string;
  latitude?: number;
  longitude?: number;
  custom_weights: {
    value: number;
    school: number;
    crime_inv: number;
    env_inv: number;
    employer_proximity: number;
  };
}

interface ScoringResult {
  id: number;
  overall_score: number;
  value_score: number;
  school_score: number;
  safety_score: number;
  environmental_score: number;
  accessibility_score: number;
  scoring_weights: {
    value: number;
    school: number;
    crime_inv: number;
    env_inv: number;
    employer_proximity: number;
  };
  score_components: {
    value: number;
    school: number;
    crime: number;
    env: number;
    employer: number;
  };
  calculated_at: string;
  model_version: string;
  explanation?: {
    overall_score: number;
    component_explanations: Array<{
      component: string;
      raw_score: number;
      weight: number;
      weighted_contribution: number;
      description: string;
    }>;
  };
}

const BeneficiaryScoringPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ScoringResult | null>(null);

  const { control, handleSubmit, formState: { errors }, watch } = useForm<BeneficiaryScoringForm>({
    defaultValues: {
      custom_weights: {
        value: 8.0,
        school: 8.0,
        crime_inv: 6.0,
        env_inv: 5.0,
        employer_proximity: 7.0,
      }
    }
  });

  const weights = watch('custom_weights');

  const onSubmit = async (data: BeneficiaryScoringForm) => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Mock result
      const mockResult: ScoringResult = {
        id: Math.floor(Math.random() * 10000),
        overall_score: 65 + Math.random() * 30,
        value_score: 70 + Math.random() * 25,
        school_score: 80 + Math.random() * 20,
        safety_score: 60 + Math.random() * 30,
        environmental_score: 85 + Math.random() * 15,
        accessibility_score: 75 + Math.random() * 20,
        scoring_weights: data.custom_weights,
        score_components: {
          value: data.custom_weights.value * (0.7 + Math.random() * 0.3),
          school: data.custom_weights.school * (0.8 + Math.random() * 0.2),
          crime: data.custom_weights.crime_inv * (0.6 + Math.random() * 0.3),
          env: data.custom_weights.env_inv * (0.85 + Math.random() * 0.15),
          employer: data.custom_weights.employer_proximity * (0.75 + Math.random() * 0.2),
        },
        calculated_at: new Date().toISOString(),
        model_version: '2.0.0',
        explanation: {
          overall_score: 78.2,
          component_explanations: [
            {
              component: 'school',
              raw_score: 85.0,
              weight: data.custom_weights.school,
              weighted_contribution: 6.8,
              description: `School quality and accessibility: excellent (85.0%) with weight ${data.custom_weights.school}`
            },
            {
              component: 'value',
              raw_score: 75.0,
              weight: data.custom_weights.value,
              weighted_contribution: 6.0,
              description: `Property value competitiveness: good (75.0%) with weight ${data.custom_weights.value}`
            },
            {
              component: 'safety',
              raw_score: 70.0,
              weight: data.custom_weights.crime_inv,
              weighted_contribution: 4.2,
              description: `Safety and crime levels: good (70.0%) with weight ${data.custom_weights.crime_inv}`
            },
            {
              component: 'environment',
              raw_score: 88.0,
              weight: data.custom_weights.env_inv,
              weighted_contribution: 4.4,
              description: `Environmental risk factors: excellent (88.0%) with weight ${data.custom_weights.env_inv}`
            },
            {
              component: 'accessibility',
              raw_score: 72.0,
              weight: data.custom_weights.employer_proximity,
              weighted_contribution: 5.04,
              description: `Employment and economic opportunities: good (72.0%) with weight ${data.custom_weights.employer_proximity}`
            }
          ]
        }
      };

      setResult(mockResult);
      toast.success('Beneficiary scoring completed successfully!');
    } catch (error) {
      toast.error('Failed to calculate beneficiary score. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return '#10b981';
    if (score >= 60) return '#f59e0b';
    if (score >= 40) return '#f97316';
    return '#ef4444';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Fair';
    return 'Poor';
  };

  const scoreComponents = [
    { key: 'value_score', label: 'Value Competitiveness', icon: <AttachMoney />, description: 'Property value vs market' },
    { key: 'school_score', label: 'School Quality', icon: <School />, description: 'Education accessibility & quality' },
    { key: 'safety_score', label: 'Safety & Security', icon: <LocalPolice />, description: 'Crime rates & safety metrics' },
    { key: 'environmental_score', label: 'Environmental', icon: <Park />, description: 'Environmental risks & quality' },
    { key: 'accessibility_score', label: 'Accessibility', icon: <DirectionsCar />, description: 'Transportation & amenities' },
  ];

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
            🎯 Beneficiary Scoring
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
            Multi-factor investment attractiveness scoring with custom weights
          </Typography>
          <Alert severity="info" sx={{ mb: 3 }}>
            <strong>Customizable Weights:</strong> Adjust the importance of each factor based on your investment priorities and risk tolerance.
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
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, display: 'flex', alignItems: 'center' }}>
                  <LocationOn sx={{ mr: 1 }} />
                  Property Location
                </Typography>
                
                <Box component="form" onSubmit={handleSubmit(onSubmit)} sx={{ mt: 2 }}>
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
                        sx={{ mb: 3 }}
                        InputProps={{
                          startAdornment: <LocationOn sx={{ mr: 1, color: 'text.secondary' }} />
                        }}
                      />
                    )}
                  />
                </Box>
              </CardContent>
            </Card>

            {/* Custom Weights */}
            <Card>
              <CardContent>
                <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, display: 'flex', alignItems: 'center' }}>
                  <TuneRounded sx={{ mr: 1 }} />
                  Scoring Weights
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  Adjust the importance of each factor (1-10 scale)
                </Typography>

                <Grid container spacing={3}>
                  <Grid item xs={12}>
                    <Typography gutterBottom sx={{ fontWeight: 600, display: 'flex', alignItems: 'center' }}>
                      <AttachMoney sx={{ mr: 1, fontSize: 20 }} />
                      Value Competitiveness: {weights.value}
                    </Typography>
                    <Controller
                      name="custom_weights.value"
                      control={control}
                      render={({ field }) => (
                        <Slider
                          {...field}
                          min={1}
                          max={10}
                          step={0.5}
                          marks
                          valueLabelDisplay="auto"
                          sx={{ color: '#2563eb' }}
                        />
                      )}
                    />
                  </Grid>

                  <Grid item xs={12}>
                    <Typography gutterBottom sx={{ fontWeight: 600, display: 'flex', alignItems: 'center' }}>
                      <School sx={{ mr: 1, fontSize: 20 }} />
                      School Quality: {weights.school}
                    </Typography>
                    <Controller
                      name="custom_weights.school"
                      control={control}
                      render={({ field }) => (
                        <Slider
                          {...field}
                          min={1}
                          max={10}
                          step={0.5}
                          marks
                          valueLabelDisplay="auto"
                          sx={{ color: '#10b981' }}
                        />
                      )}
                    />
                  </Grid>

                  <Grid item xs={12}>
                    <Typography gutterBottom sx={{ fontWeight: 600, display: 'flex', alignItems: 'center' }}>
                      <LocalPolice sx={{ mr: 1, fontSize: 20 }} />
                      Safety & Security: {weights.crime_inv}
                    </Typography>
                    <Controller
                      name="custom_weights.crime_inv"
                      control={control}
                      render={({ field }) => (
                        <Slider
                          {...field}
                          min={1}
                          max={10}
                          step={0.5}
                          marks
                          valueLabelDisplay="auto"
                          sx={{ color: '#f59e0b' }}
                        />
                      )}
                    />
                  </Grid>

                  <Grid item xs={12}>
                    <Typography gutterBottom sx={{ fontWeight: 600, display: 'flex', alignItems: 'center' }}>
                      <Park sx={{ mr: 1, fontSize: 20 }} />
                      Environmental Quality: {weights.env_inv}
                    </Typography>
                    <Controller
                      name="custom_weights.env_inv"
                      control={control}
                      render={({ field }) => (
                        <Slider
                          {...field}
                          min={1}
                          max={10}
                          step={0.5}
                          marks
                          valueLabelDisplay="auto"
                          sx={{ color: '#10b981' }}
                        />
                      )}
                    />
                  </Grid>

                  <Grid item xs={12}>
                    <Typography gutterBottom sx={{ fontWeight: 600, display: 'flex', alignItems: 'center' }}>
                      <DirectionsCar sx={{ mr: 1, fontSize: 20 }} />
                      Accessibility: {weights.employer_proximity}
                    </Typography>
                    <Controller
                      name="custom_weights.employer_proximity"
                      control={control}
                      render={({ field }) => (
                        <Slider
                          {...field}
                          min={1}
                          max={10}
                          step={0.5}
                          marks
                          valueLabelDisplay="auto"
                          sx={{ color: '#8b5cf6' }}
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
                      onClick={handleSubmit(onSubmit)}
                    >
                      {loading ? 'Calculating Score...' : 'Calculate Beneficiary Score'}
                    </Button>
                  </Grid>
                </Grid>
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
              {/* Overall Score */}
              <Card sx={{ mb: 3 }}>
                <CardContent>
                  <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, display: 'flex', alignItems: 'center' }}>
                    <Star sx={{ mr: 1 }} />
                    Overall Investment Score
                  </Typography>
                  
                  <Paper sx={{ p: 4, textAlign: 'center', bgcolor: '#f0f9ff', mb: 3 }}>
                    <Typography variant="h2" sx={{ fontWeight: 700, color: getScoreColor(result.overall_score) }}>
                      {result.overall_score.toFixed(1)}
                    </Typography>
                    <Typography variant="h5" color="text.secondary">
                      out of 100
                    </Typography>
                    <Chip
                      label={getScoreLabel(result.overall_score)}
                      sx={{
                        mt: 2,
                        bgcolor: getScoreColor(result.overall_score),
                        color: 'white',
                        fontWeight: 600,
                        fontSize: '1rem',
                        px: 2,
                        py: 1,
                      }}
                    />
                  </Paper>

                  {/* Component Scores */}
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mt: 3 }}>
                    Score Breakdown
                  </Typography>
                  <Grid container spacing={2}>
                    {scoreComponents.map((component) => {
                      const score = result[component.key as keyof ScoringResult] as number;
                      return (
                        <Grid item xs={12} sm={6} key={component.key}>
                          <Paper sx={{ p: 2 }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                              {component.icon}
                              <Typography variant="subtitle1" sx={{ ml: 1, fontWeight: 600 }}>
                                {component.label}
                              </Typography>
                            </Box>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                              <LinearProgress
                                variant="determinate"
                                value={score}
                                sx={{
                                  flexGrow: 1,
                                  height: 8,
                                  borderRadius: 4,
                                  bgcolor: '#e2e8f0',
                                  '& .MuiLinearProgress-bar': {
                                    bgcolor: getScoreColor(score),
                                  }
                                }}
                              />
                              <Typography variant="body2" sx={{ ml: 2, fontWeight: 600, minWidth: 40 }}>
                                {score.toFixed(1)}
                              </Typography>
                            </Box>
                            <Typography variant="caption" color="text.secondary">
                              {component.description}
                            </Typography>
                          </Paper>
                        </Grid>
                      );
                    })}
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
                        Scoring Explanation
                      </Typography>
                      <Tooltip title="Detailed breakdown of how each component contributes to the overall score">
                        <IconButton size="small">
                          <Info />
                        </IconButton>
                      </Tooltip>
                    </Box>

                    <Accordion defaultExpanded>
                      <AccordionSummary expandIcon={<ExpandMore />}>
                        <Typography sx={{ fontWeight: 600 }}>
                          📊 Component Contributions
                        </Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <List>
                          {result.explanation.component_explanations
                            .sort((a, b) => b.weighted_contribution - a.weighted_contribution)
                            .map((component, index) => (
                            <ListItem key={index}>
                              <ListItemIcon>
                                <TrendingUp sx={{ color: getScoreColor(component.raw_score) }} />
                              </ListItemIcon>
                              <ListItemText
                                primary={component.description}
                                secondary={`Weighted contribution: ${component.weighted_contribution.toFixed(2)} points`}
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
                <Assessment sx={{ fontSize: 80, color: '#cbd5e1', mb: 2 }} />
                <Typography variant="h5" color="text.secondary" gutterBottom>
                  Ready for Beneficiary Scoring
                </Typography>
                <Typography color="text.secondary">
                  Enter property location and adjust scoring weights to get investment attractiveness analysis
                </Typography>
              </Paper>
            </motion.div>
          )}
        </Grid>
      </Grid>
    </Container>
  );
};

export default BeneficiaryScoringPage;
