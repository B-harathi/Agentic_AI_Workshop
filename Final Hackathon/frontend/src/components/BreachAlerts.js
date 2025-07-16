import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Paper,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress
} from '@mui/material';
import {
  Warning,
  Error,
  Info,
  ExpandMore,
  AttachMoney,
  Business,
  Category,
  Schedule,
  Email,
  Visibility,
  TrendingUp
} from '@mui/icons-material';

const dummyBreaches = [
  {
    department: "Sales",
    category: "Software",
    severity: "Critical",
    overage: 2000,
    detected_at: "2024-06-05T14:00:00Z"
  }
];
const dummyNotifications = [
  {
    subject: "Critical Breach in Sales Software",
    sent_at: "2024-06-05T15:00:00Z"
  }
];

const BreachAlerts = ({ breaches, notifications }) => {
  const [selectedBreach, setSelectedBreach] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  const breachList = breaches && breaches.length > 0 ? breaches : dummyBreaches;
  const notificationList = notifications && notifications.length > 0 ? notifications : dummyNotifications;

  // Get severity icon and color
  const getSeverityIcon = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'critical':
        return <Error color="error" />;
      case 'high':
        return <Warning color="error" />;
      case 'medium':
        return <Warning color="warning" />;
      case 'low':
        return <Info color="info" />;
      default:
        return <Info color="info" />;
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'critical':
        return 'error';
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'info';
      default:
        return 'default';
    }
  };

  // Format currency
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount || 0);
  };

  // Format percentage
  const formatPercentage = (percent) => {
    return `${(percent || 0).toFixed(1)}%`;
  };

  // Handle breach details view
  const viewBreachDetails = (breach) => {
    setSelectedBreach(breach);
    setDialogOpen(true);
  };

  const closeDialog = () => {
    setDialogOpen(false);
    setSelectedBreach(null);
  };

  // Group breaches by severity
  const groupedBreaches = (breaches || []).reduce((acc, breach) => {
    const severity = breach.severity || breach.severity_level || 'medium';
    if (!acc[severity]) acc[severity] = [];
    acc[severity].push(breach);
    return acc;
  }, {});

  // Sort severity levels
  const severityOrder = ['critical', 'high', 'medium', 'low'];
  const sortedSeverities = Object.keys(groupedBreaches).sort((a, b) => {
    return severityOrder.indexOf(a.toLowerCase()) - severityOrder.indexOf(b.toLowerCase());
  });

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Budget Breach Alerts
      </Typography>
      
      <Typography variant="body1" color="textSecondary" paragraph>
        The Breach Detector Agent has identified the following budget violations. 
        Review each breach and implement the recommended corrective actions.
      </Typography>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Error color="error" sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="h4" color="error.main">
                {(groupedBreaches.critical || []).length + (groupedBreaches.high || []).length}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Critical & High Severity
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Warning color="warning" sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="h4" color="warning.main">
                {(groupedBreaches.medium || []).length}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Medium Severity
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Info color="info" sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="h4" color="info.main">
                {(groupedBreaches.low || []).length}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Low Severity
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Email color="primary" sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="h4" color="primary.main">
                {(notifications || []).length}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Notifications Sent
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* No Breaches Message */}
      {(!breaches || breaches.length === 0) && (
        <Alert severity="success" sx={{ mb: 3 }}>
          <Typography variant="h6">
            🎉 No Budget Breaches Detected
          </Typography>
          <Typography variant="body2">
            All departments are currently within their budget limits. Keep monitoring expenses to maintain healthy spending.
          </Typography>
        </Alert>
      )}

      {/* Breach Cards by Severity */}
      {sortedSeverities.map(severity => (
        <Box key={severity} sx={{ mb: 3 }}>
          <Typography variant="h5" gutterBottom sx={{ textTransform: 'capitalize', mb: 2 }}>
            {getSeverityIcon(severity)} {severity} Severity Breaches ({groupedBreaches[severity].length})
          </Typography>
          
          <Grid container spacing={2}>
            {groupedBreaches[severity].map((breach, index) => (
              <Grid item xs={12} md={6} key={breach.id || index}>
                <Card sx={{ height: '100%' }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                      <Box>
                        <Typography variant="h6" gutterBottom>
                          {breach.department} - {breach.category}
                        </Typography>
                        <Chip 
                          size="small"
                          label={severity.toUpperCase()}
                          color={getSeverityColor(severity)}
                          icon={getSeverityIcon(severity)}
                        />
                      </Box>
                      <Button
                        size="small"
                        startIcon={<Visibility />}
                        onClick={() => viewBreachDetails(breach)}
                      >
                        Details
                      </Button>
                    </Box>

                    <List dense>
                      <ListItem>
                        <ListItemIcon>
                          <AttachMoney />
                        </ListItemIcon>
                        <ListItemText 
                          primary="Budget Overage"
                          secondary={`${formatCurrency(breach.overage || breach.overage_amount)} (${formatPercentage(breach.overage_percent)}% over)`}
                        />
                      </ListItem>
                      
                      <ListItem>
                        <ListItemIcon>
                          <TrendingUp />
                        </ListItemIcon>
                        <ListItemText 
                          primary="Current Usage"
                          secondary={`${formatCurrency(breach.spent)} / ${formatCurrency(breach.limit)}`}
                        />
                      </ListItem>
                      
                      <ListItem>
                        <ListItemIcon>
                          <Schedule />
                        </ListItemIcon>
                        <ListItemText 
                          primary="Detected"
                          secondary={new Date(breach.detected_at || breach.timestamp || Date.now()).toLocaleString()}
                        />
                      </ListItem>
                    </List>

                    {/* Usage Progress Bar */}
                    <Box sx={{ mt: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="caption">Budget Usage</Typography>
                        <Typography variant="caption">
                          {formatPercentage(breach.usage_percent || ((breach.spent / breach.limit) * 100))}
                        </Typography>
                      </Box>
                      <LinearProgress 
                        variant="determinate" 
                        value={Math.min(breach.usage_percent || ((breach.spent / breach.limit) * 100), 100)} 
                        color={getSeverityColor(severity)}
                        sx={{ height: 8, borderRadius: 4 }}
                      />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      ))}

      {/* Recent Notifications */}
      {notifications && notifications.length > 0 && (
        <Paper sx={{ mt: 4 }}>
          <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
            <Typography variant="h6">
              Recent Escalation Notifications
            </Typography>
          </Box>
          
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Sent At</TableCell>
                  <TableCell>Subject</TableCell>
                  <TableCell>Recipients</TableCell>
                  <TableCell>Urgency</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {notifications.slice(0, 10).map((notification, index) => (
                  <TableRow key={notification.notification_id || index}>
                    <TableCell>
                      {new Date(notification.sent_at).toLocaleString()}
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" noWrap>
                        {notification.subject}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      {Array.isArray(notification.recipients) 
                        ? notification.recipients.join(', ')
                        : notification.recipients || 'N/A'
                      }
                    </TableCell>
                    <TableCell>
                      <Chip 
                        size="small"
                        label={notification.urgency || 'Medium'}
                        color={getSeverityColor(notification.urgency)}
                      />
                    </TableCell>
                    <TableCell>
                      <Chip 
                        size="small"
                        label={notification.status || 'Sent'}
                        color={notification.status === 'sent' ? 'success' : 'default'}
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      )}

      {/* Breach Details Dialog */}
      <Dialog 
        open={dialogOpen} 
        onClose={closeDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {selectedBreach && getSeverityIcon(selectedBreach.severity || selectedBreach.severity_level)}
            <Typography variant="h6">
              Breach Details: {selectedBreach?.department} - {selectedBreach?.category}
            </Typography>
          </Box>
        </DialogTitle>
        
        <DialogContent>
          {selectedBreach && (
            <Box>
              {/* Financial Impact */}
              <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                Financial Impact
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="body2" color="textSecondary">
                        Budget Limit
                      </Typography>
                      <Typography variant="h6">
                        {formatCurrency(selectedBreach.limit)}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={6}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="body2" color="textSecondary">
                        Total Spent
                      </Typography>
                      <Typography variant="h6" color="error.main">
                        {formatCurrency(selectedBreach.spent)}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={6}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="body2" color="textSecondary">
                        Overage Amount
                      </Typography>
                      <Typography variant="h6" color="error.main">
                        {formatCurrency(selectedBreach.overage || selectedBreach.overage_amount)}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={6}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="body2" color="textSecondary">
                        Usage Percentage
                      </Typography>
                      <Typography variant="h6" color="error.main">
                        {formatPercentage(selectedBreach.usage_percent || ((selectedBreach.spent / selectedBreach.limit) * 100))}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              {/* Triggering Transactions */}
              {selectedBreach.triggering_transactions && selectedBreach.triggering_transactions.length > 0 && (
                <Box sx={{ mt: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Triggering Transactions
                  </Typography>
                  <TableContainer component={Paper} variant="outlined">
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Date</TableCell>
                          <TableCell>Amount</TableCell>
                          <TableCell>Vendor</TableCell>
                          <TableCell>Description</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {selectedBreach.triggering_transactions.map((transaction, idx) => (
                          <TableRow key={idx}>
                            <TableCell>
                              {new Date(transaction.timestamp).toLocaleDateString()}
                            </TableCell>
                            <TableCell>{formatCurrency(transaction.amount)}</TableCell>
                            <TableCell>{transaction.vendor}</TableCell>
                            <TableCell>{transaction.description}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Box>
              )}

              {/* Additional Details */}
              <Box sx={{ mt: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Additional Information
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemText 
                      primary="Breach ID"
                      secondary={selectedBreach.id || selectedBreach.breach_id || 'N/A'}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Detection Time"
                      secondary={new Date(selectedBreach.detected_at || selectedBreach.timestamp || Date.now()).toLocaleString()}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Recurrence"
                      secondary={selectedBreach.is_recurring ? 'Yes - This is a recurring breach' : 'No - First occurrence'}
                    />
                  </ListItem>
                  {selectedBreach.recurrence_count && (
                    <ListItem>
                      <ListItemText 
                        primary="Previous Occurrences"
                        secondary={`${selectedBreach.recurrence_count} times`}
                      />
                    </ListItem>
                  )}
                </List>
              </Box>
            </Box>
          )}
        </DialogContent>
        
        <DialogActions>
          <Button onClick={closeDialog}>
            Close
          </Button>
          <Button variant="contained" onClick={closeDialog}>
            View Recommendations
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default BreachAlerts;