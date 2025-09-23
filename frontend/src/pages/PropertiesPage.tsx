import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Card,
  CardContent,
  CardMedia,
  Typography,
  Button,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  IconButton,
  Pagination,
  Alert,
} from '@mui/material';
import {
  Search,
  FilterList,
  LocationOn,
  Home,
  Bed,
  Bathtub,
  SquareFoot,
  AttachMoney,
  Favorite,
  FavoriteBorder,
  Star,
  Message,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

interface Property {
  id: number;
  title: string;
  description: string;
  property_type: string;
  listing_type: string;
  price: number;
  bedrooms?: number;
  bathrooms?: number;
  sqft?: number;
  location: {
    address: string;
    city: string;
    state: string;
  };
  images?: string[];
  is_featured: boolean;
  views_count: number;
  favorites_count: number;
  agent?: {
    id: number;
    first_name?: string;
    last_name?: string;
    username: string;
    company_name?: string;
    user_role?: 'buyer_agent' | 'seller_agent';
  };
}

const PropertiesPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [propertyType, setPropertyType] = useState('');
  const [minPrice, setMinPrice] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [minBedrooms, setMinBedrooms] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [favorites, setFavorites] = useState<Set<number>>(new Set());

  useEffect(() => {
    fetchProperties();
  }, [page, propertyType, minPrice, maxPrice, minBedrooms]);

  const fetchProperties = async () => {
    try {
      setLoading(true);
      // TODO: Replace with actual API call
      // For now, using mock data
      const mockProperties: Property[] = [
        {
          id: 1,
          title: "Beautiful 3BR Home in Naperville",
          description: "Stunning single-family home with modern amenities and great location.",
          property_type: "house",
          listing_type: "sale",
          price: 425000,
          bedrooms: 3,
          bathrooms: 2.5,
          sqft: 2100,
          location: {
            address: "123 Oak Street",
            city: "Naperville",
            state: "Illinois"
          },
          images: ["/api/placeholder/400/300"],
          is_featured: true,
          views_count: 234,
          favorites_count: 12,
          agent: {
            id: 2,
            first_name: "Sarah",
            last_name: "Johnson",
            username: "sarah_agent",
            company_name: "Premier Realty",
            user_role: "seller_agent"
          }
        },
        {
          id: 2,
          title: "Modern Condo in Downtown Chicago",
          description: "Luxury condo with city views and premium finishes.",
          property_type: "condo",
          listing_type: "sale",
          price: 350000,
          bedrooms: 2,
          bathrooms: 2,
          sqft: 1200,
          location: {
            address: "456 Michigan Ave",
            city: "Chicago",
            state: "Illinois"
          },
          images: ["/api/placeholder/400/300"],
          is_featured: false,
          views_count: 189,
          favorites_count: 7,
          agent: {
            id: 3,
            first_name: "Mike",
            last_name: "Davis",
            username: "mike_agent",
            company_name: "Urban Properties",
            user_role: "seller_agent"
          }
        }
      ];
      
      setProperties(mockProperties);
      setTotalPages(1);
    } catch (err: any) {
      setError('Failed to load properties');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setPage(1);
    fetchProperties();
  };

  const handleFavorite = (propertyId: number) => {
    const newFavorites = new Set(favorites);
    if (newFavorites.has(propertyId)) {
      newFavorites.delete(propertyId);
    } else {
      newFavorites.add(propertyId);
    }
    setFavorites(newFavorites);
    // TODO: API call to update favorites
  };

  const handleContactAgent = (property: Property) => {
    if (!user) {
      navigate('/login');
      return;
    }

    // Enhanced role-based access with agent-mediated communication
    if (user.user_role === 'buyer') {
      // Buyers can contact seller agents for properties
      if (property.agent && property.agent.user_role === 'seller_agent') {
        navigate(`/messages/new?agent=${property.agent.id}&property=${property.id}`);
      } else {
        // If no seller agent is assigned, show message
        setError('This property does not have an assigned seller agent. Please contact the property owner directly or find an alternative listing.');
      }
    } else if (user.user_role === 'seller') {
      // Sellers need to work through their assigned seller agent
      setError('As a seller, you should work with your assigned seller agent to handle communications with buyers and other agents.');
    } else if (user.user_role === 'buyer_agent') {
      // Buyer agents can contact seller agents
      if (property.agent) {
        navigate(`/messages/new?agent=${property.agent.id}&property=${property.id}`);
      } else {
        setError('This property does not have an assigned agent to contact.');
      }
    } else if (user.user_role === 'seller_agent') {
      // Seller agents can contact anyone
      if (property.agent) {
        navigate(`/messages/new?agent=${property.agent.id}&property=${property.id}`);
      } else {
        setError('This property does not have an assigned agent to contact.');
      }
    } else {
      setError('Unable to determine your role for contacting agents.');
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(price);
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
          Property Listings
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Discover your perfect property in Illinois
        </Typography>
      </Box>

      {/* Search and Filters */}
      <Card sx={{ mb: 4, p: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              placeholder="Search by location, property type..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={2}>
            <FormControl fullWidth>
              <InputLabel>Property Type</InputLabel>
              <Select
                value={propertyType}
                label="Property Type"
                onChange={(e) => setPropertyType(e.target.value)}
              >
                <MenuItem value="">All Types</MenuItem>
                <MenuItem value="house">House</MenuItem>
                <MenuItem value="condo">Condo</MenuItem>
                <MenuItem value="townhouse">Townhouse</MenuItem>
                <MenuItem value="land">Land</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6} md={2}>
            <TextField
              fullWidth
              label="Min Price"
              value={minPrice}
              onChange={(e) => setMinPrice(e.target.value)}
              type="number"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={2}>
            <TextField
              fullWidth
              label="Max Price"
              value={maxPrice}
              onChange={(e) => setMaxPrice(e.target.value)}
              type="number"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={2}>
            <Button
              fullWidth
              variant="contained"
              onClick={handleSearch}
              startIcon={<Search />}
              sx={{ height: 56 }}
            >
              Search
            </Button>
          </Grid>
        </Grid>
      </Card>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {/* Properties Grid */}
      {loading ? (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <Typography>Loading properties...</Typography>
        </Box>
      ) : (
        <>
          <Grid container spacing={3}>
            {properties.map((property) => (
              <Grid item xs={12} sm={6} lg={4} key={property.id}>
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <Card 
                    sx={{ 
                      height: '100%', 
                      display: 'flex', 
                      flexDirection: 'column',
                      position: 'relative',
                      '&:hover': {
                        transform: 'translateY(-4px)',
                        boxShadow: 4,
                      },
                      transition: 'all 0.3s ease-in-out',
                    }}
                  >
                    {/* Featured Badge */}
                    {property.is_featured && (
                      <Chip
                        label="Featured"
                        color="primary"
                        size="small"
                        icon={<Star />}
                        sx={{
                          position: 'absolute',
                          top: 8,
                          left: 8,
                          zIndex: 1,
                        }}
                      />
                    )}

                    {/* Favorite Button */}
                    <IconButton
                      onClick={() => handleFavorite(property.id)}
                      sx={{
                        position: 'absolute',
                        top: 8,
                        right: 8,
                        zIndex: 1,
                        backgroundColor: 'rgba(255, 255, 255, 0.9)',
                        '&:hover': {
                          backgroundColor: 'rgba(255, 255, 255, 1)',
                        },
                      }}
                    >
                      {favorites.has(property.id) ? (
                        <Favorite color="error" />
                      ) : (
                        <FavoriteBorder />
                      )}
                    </IconButton>

                    {/* Property Image */}
                    <CardMedia
                      component="img"
                      height="200"
                      image={property.images?.[0] || '/api/placeholder/400/300'}
                      alt={property.title}
                      sx={{ cursor: 'pointer' }}
                      onClick={() => navigate(`/properties/${property.id}`)}
                    />

                    <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
                      {/* Price */}
                      <Typography variant="h5" component="h2" gutterBottom sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                        {formatPrice(property.price)}
                      </Typography>

                      {/* Title */}
                      <Typography 
                        variant="h6" 
                        component="h3" 
                        gutterBottom 
                        sx={{ 
                          cursor: 'pointer',
                          '&:hover': { color: 'primary.main' }
                        }}
                        onClick={() => navigate(`/properties/${property.id}`)}
                      >
                        {property.title}
                      </Typography>

                      {/* Location */}
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <LocationOn fontSize="small" color="action" sx={{ mr: 0.5 }} />
                        <Typography variant="body2" color="text.secondary">
                          {property.location.address}, {property.location.city}, {property.location.state}
                        </Typography>
                      </Box>

                      {/* Property Details */}
                      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                        {property.bedrooms && (
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Bed fontSize="small" color="action" sx={{ mr: 0.5 }} />
                            <Typography variant="body2">{property.bedrooms} bed</Typography>
                          </Box>
                        )}
                        {property.bathrooms && (
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Bathtub fontSize="small" color="action" sx={{ mr: 0.5 }} />
                            <Typography variant="body2">{property.bathrooms} bath</Typography>
                          </Box>
                        )}
                        {property.sqft && (
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <SquareFoot fontSize="small" color="action" sx={{ mr: 0.5 }} />
                            <Typography variant="body2">{property.sqft.toLocaleString()} sqft</Typography>
                          </Box>
                        )}
                      </Box>

                      {/* Agent Info */}
                      {property.agent && (
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="body2" color="text.secondary">
                            Listed by: {property.agent.first_name} {property.agent.last_name}
                          </Typography>
                          {property.agent.company_name && (
                            <Typography variant="body2" color="text.secondary">
                              {property.agent.company_name}
                            </Typography>
                          )}
                        </Box>
                      )}

                      {/* Action Buttons */}
                      <Box sx={{ mt: 'auto', display: 'flex', gap: 1 }}>
                        <Button
                          variant="outlined"
                          fullWidth
                          onClick={() => navigate(`/properties/${property.id}`)}
                        >
                          View Details
                        </Button>
                        {user && property.agent && (
                          <Button
                            variant="contained"
                            startIcon={<Message />}
                            onClick={() => handleContactAgent(property)}
                          >
                            Contact
                          </Button>
                        )}
                      </Box>
                    </CardContent>
                  </Card>
                </motion.div>
              </Grid>
            ))}
          </Grid>

          {/* Pagination */}
          {totalPages > 1 && (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
              <Pagination
                count={totalPages}
                page={page}
                onChange={(_, newPage) => setPage(newPage)}
                color="primary"
                size="large"
              />
            </Box>
          )}
        </>
      )}
    </Container>
  );
};

export default PropertiesPage;
