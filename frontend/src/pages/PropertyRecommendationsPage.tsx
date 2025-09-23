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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
  Divider,
  IconButton,
  Tooltip,
  Slider,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  Recommend,
  LocationOn,
  Home,
  AttachMoney,
  TrendingUp,
  Star,
  Favorite,
  Share,
  MoreVert,
  FilterList,
  Search,
  MyLocation,
  Tune,
  Psychology,
  Speed,
  CheckCircle,
} from '@mui/icons-material';
import { useForm, Controller } from 'react-hook-form';
import { motion } from 'framer-motion';
import { toast } from 'react-toastify';

interface RecommendationForm {
  search_type: 'location' | 'property';
  property_id?: number;
  location?: {
    lat: number;
    lon: number;
  };
  address?: string;
  radius_km?: number;
  max_recommendations: number;
  recommendation_type: 'content_based' | 'collaborative' | 'hybrid';
  user_preferences?: {
    min_beds?: number;
    max_beds?: number;
    min_baths?: number;
    max_baths?: number;
    min_price?: number;
    max_price?: number;
    property_type?: string;
    min_sqft?: number;
    max_sqft?: number;
  };
}

interface PropertyRecommendation {
  id: number;
  recommended_property: {
    id: number;
    predicted_value: number;
    beds: number;
    baths: number;
    sqft: number;
    year_built: number;
    address: string;
    property_type: string;
  };
  recommendation_type: string;
  similarity_score: number;
  confidence_score: number;
  rank_position: number;
  recommendation_reason: string;
  created_at: string;
}

const PropertyRecommendationsPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<PropertyRecommendation[]>([]);
  const [showFilters, setShowFilters] = useState(false);

  const { control, handleSubmit, formState: { errors }, watch } = useForm<RecommendationForm>({
    defaultValues: {
      search_type: 'location',
      radius_km: 10,
      max_recommendations: 10,
      recommendation_type: 'hybrid',
      user_preferences: {
        min_beds: 2,
        max_beds: 5,
        min_baths: 1,
        max_baths: 4,
        min_price: 100000,
        max_price: 1000000,
        property_type: 'residential',
        min_sqft: 800,
        max_sqft: 4000,
      }
    }
  });

  const searchType = watch('search_type');
  const preferences = watch('user_preferences');

  const onSubmit = async (data: RecommendationForm) => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2500));
      
      // Mock results
      const mockResults: PropertyRecommendation[] = Array.from({ length: data.max_recommendations }, (_, index) => ({
        id: index + 1,
        recommended_property: {
          id: Math.floor(Math.random() * 10000),
          predicted_value: 200000 + Math.random() * 500000,
          beds: Math.floor(Math.random() * 4) + 2,
          baths: Math.floor(Math.random() * 3) + 1,
          sqft: Math.floor(Math.random() * 2000) + 1000,
          year_built: Math.floor(Math.random() * 50) + 1970,
          address: `${Math.floor(Math.random() * 9999) + 1} ${['Main', 'Oak', 'Pine', 'Elm', 'Cedar'][Math.floor(Math.random() * 5)]} St, ${['Chicago', 'Austin', 'Denver', 'Seattle', 'Portland'][Math.floor(Math.random() * 5)]}, ${['IL', 'TX', 'CO', 'WA', 'OR'][Math.floor(Math.random() * 5)]}`,
          property_type: 'residential',
        },
        recommendation_type: data.recommendation_type,
        similarity_score: 0.6 + Math.random() * 0.4,
        confidence_score: 0.7 + Math.random() * 0.3,
        rank_position: index + 1,
        recommendation_reason: [
          'Similar property characteristics',
          'Great investment potential',
          'Excellent location match',
          'Strong market performance',
          'High user rating similarity'
        ][Math.floor(Math.random() * 5)],
        created_at: new Date().toISOString(),
      })).sort((a, b) => b.similarity_score - a.similarity_score);

      setResults(mockResults);
      toast.success(`Found ${mockResults.length} property recommendations!`);
    } catch (error) {
      toast.error('Failed to get property recommendations. Please try again.');
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

  const getSimilarityColor = (similarity: number) => {
    if (similarity >= 0.8) return '#2563eb';
    if (similarity >= 0.6) return '#10b981';
    return '#f59e0b';
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
            🎯 Property Recommendations
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
            Hybrid ML-powered property recommendations and similarity analysis
          </Typography>
          <Alert severity="info" sx={{ mb: 3 }}>
            <strong>Hybrid AI:</strong> Combines content-based filtering (property characteristics) with collaborative filtering (user behavior) for optimal recommendations.
          </Alert>
        </Box>
      </motion.div>

      <Grid container spacing={4}>
        {/* Search Form */}
        <Grid item xs={12} lg={4}>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, display: 'flex', alignItems: 'center' }}>
                  <Search sx={{ mr: 1 }} />
                  Search Criteria
                </Typography>
                
                <Box component="form" onSubmit={handleSubmit(onSubmit)} sx={{ mt: 2 }}>
                  <Grid container spacing={3}>
                    <Grid item xs={12}>
                      <Controller
                        name="search_type"
                        control={control}
                        render={({ field }) => (
                          <FormControl fullWidth>
                            <InputLabel>Search Type</InputLabel>
                            <Select {...field} label="Search Type">
                              <MenuItem value="location">By Location</MenuItem>
                              <MenuItem value="property">By Similar Property</MenuItem>
                            </Select>
                          </FormControl>
                        )}
                      />
                    </Grid>

                    {searchType === 'location' && (
                      <>
                        <Grid item xs={12}>
                          <Controller
                            name="address"
                            control={control}
                            rules={{ required: 'Address is required for location search' }}
                            render={({ field }) => (
                              <TextField
                                {...field}
                                fullWidth
                                label="Search Location"
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

                        <Grid item xs={12}>
                          <Typography gutterBottom sx={{ fontWeight: 600 }}>
                            Search Radius: {watch('radius_km')} km
                          </Typography>
                          <Controller
                            name="radius_km"
                            control={control}
                            render={({ field }) => (
                              <Slider
                                {...field}
                                min={1}
                                max={50}
                                step={1}
                                marks={[
                                  { value: 1, label: '1km' },
                                  { value: 25, label: '25km' },
                                  { value: 50, label: '50km' }
                                ]}
                                valueLabelDisplay="auto"
                                sx={{ color: '#2563eb' }}
                              />
                            )}
                          />
                        </Grid>
                      </>
                    )}

                    {searchType === 'property' && (
                      <Grid item xs={12}>
                        <Controller
                          name="property_id"
                          control={control}
                          rules={{ required: 'Property ID is required for property search' }}
                          render={({ field }) => (
                            <TextField
                              {...field}
                              fullWidth
                              type="number"
                              label="Property ID"
                              placeholder="Enter property ID"
                              error={!!errors.property_id}
                              helperText={errors.property_id?.message}
                            />
                          )}
                        />
                      </Grid>
                    )}

                    <Grid item xs={12}>
                      <Controller
                        name="recommendation_type"
                        control={control}
                        render={({ field }) => (
                          <FormControl fullWidth>
                            <InputLabel>Recommendation Algorithm</InputLabel>
                            <Select {...field} label="Recommendation Algorithm">
                              <MenuItem value="content_based">Content-Based</MenuItem>
                              <MenuItem value="collaborative">Collaborative Filtering</MenuItem>
                              <MenuItem value="hybrid">Hybrid (Recommended)</MenuItem>
                            </Select>
                          </FormControl>
                        )}
                      />
                    </Grid>

                    <Grid item xs={12}>
                      <Typography gutterBottom sx={{ fontWeight: 600 }}>
                        Max Results: {watch('max_recommendations')}
                      </Typography>
                      <Controller
                        name="max_recommendations"
                        control={control}
                        render={({ field }) => (
                          <Slider
                            {...field}
                            min={5}
                            max={50}
                            step={5}
                            marks
                            valueLabelDisplay="auto"
                            sx={{ color: '#10b981' }}
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
                        startIcon={loading ? <CircularProgress size={20} /> : <Recommend />}
                        sx={{ py: 1.5 }}
                      >
                        {loading ? 'Finding Recommendations...' : 'Get Recommendations'}
                      </Button>
                    </Grid>
                  </Grid>
                </Box>
              </CardContent>
            </Card>

            {/* Filters */}
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="h6" sx={{ fontWeight: 600, display: 'flex', alignItems: 'center' }}>
                    <FilterList sx={{ mr: 1 }} />
                    Preferences
                  </Typography>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={showFilters}
                        onChange={(e) => setShowFilters(e.target.checked)}
                      />
                    }
                    label="Advanced"
                  />
                </Box>

                {showFilters && (
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Controller
                        name="user_preferences.min_beds"
                        control={control}
                        render={({ field }) => (
                          <TextField
                            {...field}
                            fullWidth
                            type="number"
                            label="Min Beds"
                            size="small"
                          />
                        )}
                      />
                    </Grid>
                    <Grid item xs={6}>
                      <Controller
                        name="user_preferences.max_beds"
                        control={control}
                        render={({ field }) => (
                          <TextField
                            {...field}
                            fullWidth
                            type="number"
                            label="Max Beds"
                            size="small"
                          />
                        )}
                      />
                    </Grid>
                    <Grid item xs={6}>
                      <Controller
                        name="user_preferences.min_price"
                        control={control}
                        render={({ field }) => (
                          <TextField
                            {...field}
                            fullWidth
                            type="number"
                            label="Min Price"
                            size="small"
                          />
                        )}
                      />
                    </Grid>
                    <Grid item xs={6}>
                      <Controller
                        name="user_preferences.max_price"
                        control={control}
                        render={({ field }) => (
                          <TextField
                            {...field}
                            fullWidth
                            type="number"
                            label="Max Price"
                            size="small"
                          />
                        )}
                      />
                    </Grid>
                  </Grid>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Results */}
        <Grid item xs={12} lg={8}>
          {results.length > 0 ? (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
            >
              <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
                🏠 Found {results.length} Recommendations
              </Typography>
              
              <Grid container spacing={3}>
                {results.map((recommendation, index) => (
                  <Grid item xs={12} key={recommendation.id}>
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.1 }}
                    >
                      <Card sx={{ '&:hover': { boxShadow: 4 }, transition: 'box-shadow 0.2s' }}>
                        <CardContent>
                          <Grid container spacing={3} alignItems="center">
                            <Grid item xs={12} md={1}>
                              <Avatar
                                sx={{
                                  bgcolor: getSimilarityColor(recommendation.similarity_score),
                                  fontWeight: 700,
                                  fontSize: '1.2rem',
                                }}
                              >
                                #{recommendation.rank_position}
                              </Avatar>
                            </Grid>
                            
                            <Grid item xs={12} md={6}>
                              <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                                {recommendation.recommended_property.address}
                              </Typography>
                              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                                <Chip
                                  label={`${recommendation.recommended_property.beds} bed`}
                                  size="small"
                                  variant="outlined"
                                />
                                <Chip
                                  label={`${recommendation.recommended_property.baths} bath`}
                                  size="small"
                                  variant="outlined"
                                />
                                <Chip
                                  label={`${recommendation.recommended_property.sqft.toLocaleString()} sqft`}
                                  size="small"
                                  variant="outlined"
                                />
                                <Chip
                                  label={recommendation.recommended_property.year_built}
                                  size="small"
                                  variant="outlined"
                                />
                              </Box>
                              <Typography variant="body2" color="text.secondary">
                                {recommendation.recommendation_reason}
                              </Typography>
                            </Grid>
                            
                            <Grid item xs={12} md={3}>
                              <Typography variant="h5" sx={{ fontWeight: 700, color: '#2563eb', mb: 1 }}>
                                {formatCurrency(recommendation.recommended_property.predicted_value)}
                              </Typography>
                              <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                                <Chip
                                  label={`${(recommendation.similarity_score * 100).toFixed(0)}% match`}
                                  size="small"
                                  sx={{
                                    bgcolor: getSimilarityColor(recommendation.similarity_score),
                                    color: 'white',
                                    fontWeight: 600,
                                  }}
                                />
                                <Chip
                                  label={`${(recommendation.confidence_score * 100).toFixed(0)}% confidence`}
                                  size="small"
                                  sx={{
                                    bgcolor: getConfidenceColor(recommendation.confidence_score),
                                    color: 'white',
                                    fontWeight: 600,
                                  }}
                                />
                              </Box>
                              <Typography variant="caption" color="text.secondary">
                                {recommendation.recommendation_type.replace('_', ' ')}
                              </Typography>
                            </Grid>
                            
                            <Grid item xs={12} md={2}>
                              <Box sx={{ display: 'flex', gap: 1 }}>
                                <Tooltip title="Save to favorites">
                                  <IconButton size="small">
                                    <Favorite />
                                  </IconButton>
                                </Tooltip>
                                <Tooltip title="Share property">
                                  <IconButton size="small">
                                    <Share />
                                  </IconButton>
                                </Tooltip>
                                <Tooltip title="More options">
                                  <IconButton size="small">
                                    <MoreVert />
                                  </IconButton>
                                </Tooltip>
                              </Box>
                            </Grid>
                          </Grid>
                        </CardContent>
                      </Card>
                    </motion.div>
                  </Grid>
                ))}
              </Grid>
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
            >
              <Paper sx={{ p: 6, textAlign: 'center', bgcolor: '#f8fafc' }}>
                <Recommend sx={{ fontSize: 80, color: '#cbd5e1', mb: 2 }} />
                <Typography variant="h5" color="text.secondary" gutterBottom>
                  Ready for Property Recommendations
                </Typography>
                <Typography color="text.secondary">
                  Enter search criteria to get AI-powered property recommendations tailored to your preferences
                </Typography>
              </Paper>
            </motion.div>
          )}
        </Grid>
      </Grid>
    </Container>
  );
};

export default PropertyRecommendationsPage;
