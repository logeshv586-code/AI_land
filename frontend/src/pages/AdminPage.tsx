import React from 'react';
import { Typography, Box } from '@mui/material';

const AdminPage: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Admin Panel
      </Typography>
      <Typography variant="body1" color="text.secondary">
        System administration and data management.
      </Typography>
    </Box>
  );
};

export default AdminPage;