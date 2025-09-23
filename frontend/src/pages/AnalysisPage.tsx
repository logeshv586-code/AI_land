import React from 'react';
import { Typography, Box } from '@mui/material';

const AnalysisPage: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Land Analysis
      </Typography>
      <Typography variant="body1" color="text.secondary">
        Perform comprehensive AI-powered land suitability analysis.
      </Typography>
    </Box>
  );
};

export default AnalysisPage;