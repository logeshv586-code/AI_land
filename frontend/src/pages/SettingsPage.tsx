import React from 'react';
import { Typography, Box } from '@mui/material';

const SettingsPage: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Settings
      </Typography>
      <Typography variant="body1" color="text.secondary">
        Manage your account settings and preferences.
      </Typography>
    </Box>
  );
};

export default SettingsPage;