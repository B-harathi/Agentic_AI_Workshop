import React from 'react';
import { Card, CardContent, Typography } from '@mui/material';

function BreachAlerts() {
  return (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Typography variant="h6">Breach Alerts</Typography>
        <Typography variant="body2">Any budget breaches will be displayed here.</Typography>
      </CardContent>
    </Card>
  );
}

export default BreachAlerts; 