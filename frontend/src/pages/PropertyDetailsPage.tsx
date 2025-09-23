import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  Divider,
  Avatar,
  IconButton,
  ImageList,
  ImageListItem,
  Alert,
} from '@mui/material';
import {
  ArrowBack,
  LocationOn,
  Bed,
  Bathtub,
  SquareFoot,
  CalendarToday,
  Visibility,
  Favorite,
  FavoriteBorder,
  Message,
  Phone,
  Email,
  Star,
  Home,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import ContactAgentDialog from '../components/PropertyContact/ContactAgentDialog';

interface PropertyDetails {
  id: number;
  title: string;
  description: string;
  property_type: string;
  listing_type: string;
  price: number;
  bedrooms?: number;
  bathrooms?: number;
  sqft?: number;
  lot_size?: number;
  year_built?: number;
  location: {
    address: string;
    city: string;
    state: string;
    zip_code?: string;
  };
  images: string[];
  is_featured: boolean;
  views_count: number;
  favorites_count: number;
  created_at: string;
  agent: {
    id: number;
    first_name?: string;
    last_name?: string;
    username: string;
    email?: string;
    phone?: string;
    company_name?: string;
    bio?: string;
    avatar?: string;
  };
  features: string[];
  nearby_amenities: string[];
}

const PropertyDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [property, setProperty] = useState<PropertyDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isFavorite, setIsFavorite] = useState(false);
  const [selectedImage, setSelectedImage] = useState(0);
  const [contactDialogOpen, setContactDialogOpen] = useState(false);

  useEffect(() => {
    if (id) {
      fetchPropertyDetails(parseInt(id));
    }
  }, [id]);

  const fetchPropertyDetails = async (propertyId: number) => {
    try {
      setLoading(true);
      // TODO: Replace with actual API call
      // Mock data for now
      const mockProperty: PropertyDetails = {
        id: propertyId,
        title: "Beautiful 3BR Home in Naperville",
        description: "This stunning single-family home offers modern amenities and a great location in the heart of Naperville. The open floor plan features a spacious living room with fireplace, updated kitchen with granite countertops and stainless steel appliances, and a master suite with walk-in closet. The backyard is perfect for entertaining with a deck and mature landscaping. Located in a quiet neighborhood with excellent schools and close to shopping and dining.",
        property_type: "house",
        listing_type: "sale",
        price: 425000,
        bedrooms: 3,
        bathrooms: 2.5,
        sqft: 2100,
        lot_size: 0.25,
        year_built: 2015,
        location: {
          address: "123 Oak Street",
          city: "Naperville",
          state: "Illinois",
          zip_code: "60540"
        },
        images: [
          "/api/placeholder/800/600",
          "/api/placeholder/800/600",
          "/api/placeholder/800/600",
          "/api/placeholder/800/600"
        ],
        is_featured: true,
        views_count: 234,
        favorites_count: 12,
        created_at: "2024-01-15T10:00:00Z",
        agent: {
          id: 2,
          first_name: "Sarah",
          last_name: "Johnson",
          username: "sarah_agent",
          email: "sarah@premierrealty.com",
          phone: "(555) 123-4567",
          company_name: "Premier Realty",
          bio: "Experienced real estate agent specializing in residential properties in the Naperville area.",
          avatar: "/api/placeholder/100/100"
        },
        features: [
          "Hardwood floors",
          "Updated kitchen",
          "Fireplace",
          "Walk-in closets",
          "Deck",
          "Garage",
          "Central air",
          "Dishwasher"
        ],
        nearby_amenities: [
          "Excellent schools",
          "Shopping centers",
          "Parks and recreation",
          "Public transportation",
          "Restaurants",
          "Medical facilities"
        ]
      };
      
      setProperty(mockProperty);
    } catch (err: any) {
      setError('Failed to load property details');
    } finally {
      setLoading(false);
    }
  };

  const handleFavorite = () => {
    setIsFavorite(!isFavorite);
    // TODO: API call to update favorites
  };

  const handleContactAgent = () => {
    if (!user) {
      navigate('/login');
      return;
    }

    if (!property?.agent) return;

    // Open contact dialog instead of navigating
    setContactDialogOpen(true);
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(price);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography>Loading property details...</Typography>
      </Container>
    );
  }

  if (error || !property) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">{error || 'Property not found'}</Alert>
        <Button startIcon={<ArrowBack />} onClick={() => navigate('/properties')} sx={{ mt: 2 }}>
          Back to Properties
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Back Button */}
      <Button
        startIcon={<ArrowBack />}
        onClick={() => navigate('/properties')}
        sx={{ mb: 3 }}
      >
        Back to Properties
      </Button>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <Grid container spacing={4}>
        {/* Left Column - Images and Details */}
        <Grid item xs={12} md={8}>
          {/* Main Image */}
          <Card sx={{ mb: 3 }}>
            <Box sx={{ position: 'relative' }}>
              <img
                src={property.images[selectedImage]}
                alt={property.title}
                style={{
                  width: '100%',
                  height: '400px',
                  objectFit: 'cover'
                }}
              />
              
              {/* Featured Badge */}
              {property.is_featured && (
                <Chip
                  label="Featured"
                  color="primary"
                  size="small"
                  icon={<Star />}
                  sx={{
                    position: 'absolute',
                    top: 16,
                    left: 16,
                  }}
                />
              )}

              {/* Favorite Button */}
              <IconButton
                onClick={handleFavorite}
                sx={{
                  position: 'absolute',
                  top: 16,
                  right: 16,
                  backgroundColor: 'rgba(255, 255, 255, 0.9)',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 1)',
                  },
                }}
              >
                {isFavorite ? (
                  <Favorite color="error" />
                ) : (
                  <FavoriteBorder />
                )}
              </IconButton>
            </Box>

            {/* Image Thumbnails */}
            {property.images.length > 1 && (
              <Box sx={{ p: 2 }}>
                <ImageList cols={4} gap={8}>
                  {property.images.map((image, index) => (
                    <ImageListItem key={index}>
                      <img
                        src={image}
                        alt={`Property ${index + 1}`}
                        style={{
                          width: '100%',
                          height: '80px',
                          objectFit: 'cover',
                          cursor: 'pointer',
                          border: selectedImage === index ? '2px solid #1976d2' : '2px solid transparent',
                          borderRadius: '4px'
                        }}
                        onClick={() => setSelectedImage(index)}
                      />
                    </ImageListItem>
                  ))}
                </ImageList>
              </Box>
            )}
          </Card>

          {/* Property Details */}
          <Card>
            <CardContent>
              <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
                {property.title}
              </Typography>

              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <LocationOn color="action" sx={{ mr: 1 }} />
                <Typography variant="h6" color="text.secondary">
                  {property.location.address}, {property.location.city}, {property.location.state} {property.location.zip_code}
                </Typography>
              </Box>

              <Typography variant="h3" component="h2" gutterBottom sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                {formatPrice(property.price)}
              </Typography>

              {/* Property Stats */}
              <Grid container spacing={2} sx={{ mb: 3 }}>
                {property.bedrooms && (
                  <Grid item xs={6} sm={3}>
                    <Box sx={{ display: 'flex', alignItems: 'center', flexDirection: 'column', p: 2, backgroundColor: 'grey.50', borderRadius: 1 }}>
                      <Bed color="primary" sx={{ mb: 1 }} />
                      <Typography variant="h6">{property.bedrooms}</Typography>
                      <Typography variant="body2" color="text.secondary">Bedrooms</Typography>
                    </Box>
                  </Grid>
                )}
                {property.bathrooms && (
                  <Grid item xs={6} sm={3}>
                    <Box sx={{ display: 'flex', alignItems: 'center', flexDirection: 'column', p: 2, backgroundColor: 'grey.50', borderRadius: 1 }}>
                      <Bathtub color="primary" sx={{ mb: 1 }} />
                      <Typography variant="h6">{property.bathrooms}</Typography>
                      <Typography variant="body2" color="text.secondary">Bathrooms</Typography>
                    </Box>
                  </Grid>
                )}
                {property.sqft && (
                  <Grid item xs={6} sm={3}>
                    <Box sx={{ display: 'flex', alignItems: 'center', flexDirection: 'column', p: 2, backgroundColor: 'grey.50', borderRadius: 1 }}>
                      <SquareFoot color="primary" sx={{ mb: 1 }} />
                      <Typography variant="h6">{property.sqft.toLocaleString()}</Typography>
                      <Typography variant="body2" color="text.secondary">Sq Ft</Typography>
                    </Box>
                  </Grid>
                )}
                {property.year_built && (
                  <Grid item xs={6} sm={3}>
                    <Box sx={{ display: 'flex', alignItems: 'center', flexDirection: 'column', p: 2, backgroundColor: 'grey.50', borderRadius: 1 }}>
                      <Home color="primary" sx={{ mb: 1 }} />
                      <Typography variant="h6">{property.year_built}</Typography>
                      <Typography variant="body2" color="text.secondary">Year Built</Typography>
                    </Box>
                  </Grid>
                )}
              </Grid>

              <Divider sx={{ my: 3 }} />

              {/* Description */}
              <Typography variant="h6" gutterBottom>
                Description
              </Typography>
              <Typography variant="body1" paragraph>
                {property.description}
              </Typography>

              <Divider sx={{ my: 3 }} />

              {/* Features */}
              <Typography variant="h6" gutterBottom>
                Features & Amenities
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 3 }}>
                {property.features.map((feature, index) => (
                  <Chip key={index} label={feature} variant="outlined" />
                ))}
              </Box>

              {/* Nearby Amenities */}
              <Typography variant="h6" gutterBottom>
                Nearby Amenities
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {property.nearby_amenities.map((amenity, index) => (
                  <Chip key={index} label={amenity} variant="outlined" color="primary" />
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Right Column - Agent Info and Actions */}
        <Grid item xs={12} md={4}>
          {/* Agent Card */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Listed by
              </Typography>
              
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar
                  src={property.agent.avatar}
                  alt={`${property.agent.first_name} ${property.agent.last_name}`}
                  sx={{ width: 60, height: 60, mr: 2 }}
                />
                <Box>
                  <Typography variant="h6">
                    {property.agent.first_name} {property.agent.last_name}
                  </Typography>
                  {property.agent.company_name && (
                    <Typography variant="body2" color="text.secondary">
                      {property.agent.company_name}
                    </Typography>
                  )}
                </Box>
              </Box>

              {property.agent.bio && (
                <Typography variant="body2" paragraph>
                  {property.agent.bio}
                </Typography>
              )}

              <Divider sx={{ my: 2 }} />

              {/* Contact Info */}
              {property.agent.phone && (
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Phone fontSize="small" color="action" sx={{ mr: 1 }} />
                  <Typography variant="body2">{property.agent.phone}</Typography>
                </Box>
              )}
              {property.agent.email && (
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Email fontSize="small" color="action" sx={{ mr: 1 }} />
                  <Typography variant="body2">{property.agent.email}</Typography>
                </Box>
              )}

              {/* Contact Button */}
              <Button
                fullWidth
                variant="contained"
                size="large"
                startIcon={<Message />}
                onClick={handleContactAgent}
                sx={{ mb: 2 }}
              >
                Contact Agent
              </Button>
            </CardContent>
          </Card>

          {/* Property Stats */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Property Stats
              </Typography>
              
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Visibility fontSize="small" color="action" sx={{ mr: 1 }} />
                <Typography variant="body2">
                  {property.views_count} views
                </Typography>
              </Box>
              
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Favorite fontSize="small" color="action" sx={{ mr: 1 }} />
                <Typography variant="body2">
                  {property.favorites_count} favorites
                </Typography>
              </Box>
              
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <CalendarToday fontSize="small" color="action" sx={{ mr: 1 }} />
                <Typography variant="body2">
                  Listed on {formatDate(property.created_at)}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Contact Agent Dialog */}
      {property && property.agent && (
        <ContactAgentDialog
          open={contactDialogOpen}
          onClose={() => setContactDialogOpen(false)}
          agent={property.agent}
          property={{
            id: property.id,
            title: property.title,
            price: property.price,
            location: property.location
          }}
          onSuccess={() => {
            // Show success message or redirect
            setError('');
            // Could show a success toast here
          }}
        />
      )}
    </Container>
  );
};

export default PropertyDetailsPage;
