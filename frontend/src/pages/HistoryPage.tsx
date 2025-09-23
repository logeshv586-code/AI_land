import React from 'react';
import { Typography, Box } from '@mui/material';

const HistoryPage: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Analysis History
      </Typography>
      <Typography variant="body1" color="text.secondary">
        View and manage your previous land analyses.
      </Typography>
    </Box>
  );
};

export default HistoryPage;