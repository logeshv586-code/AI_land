import React from 'react';
import { Typography, Box } from '@mui/material';

const ComparePage: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Compare Locations
      </Typography>
      <Typography variant="body1" color="text.secondary">
        Compare multiple property analyses side by side.
      </Typography>
    </Box>
  );
};

export default ComparePage;