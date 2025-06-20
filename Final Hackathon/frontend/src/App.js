import React, { useState, useEffect } from 'react';
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  Box,
  AppBar,
  Toolbar,
  Typography,
  Container,
  Grid,
  Paper,
  Tab,
  Tabs,
  Alert,
  Snackbar
} from '@mui/material';
import { Dashboard, Upload, AccountBalance, TrendingUp, Notifications } from '@mui/icons-material';

// Import components
import DashboardView from './components/Dashboard';
import BudgetUpload from './components/BudgetUpload';
import ExpenseList from './components/ExpenseList';
import BreachAlerts from './components/BreachAlerts';
import Recommendations from './components/Recommendations';

// Import services
import { apiService } from './services/api';
import { useWebSocket } from './hooks/useWebSocket';

// Material-UI theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    h4: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 500,
    },
  },
});

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

function App() {
  const [currentTab, setCurrentTab] = useState(0);
  const [dashboardData, setDashboardData] = useState({
    budgetLoaded: false,
    budgetData: {},
    expenseTracking: {},
    detectedBreaches: [],
    recommendations: [],
    notifications: [],
    lastUpdated: null
  });
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'info' });

  // WebSocket connection for real-time updates
  const { isConnected } = useWebSocket('http://localhost:3002', (data) => {
    setDashboardData(prev => ({ ...prev, ...data }));
    
    // Show notification for important updates
    if (data.detectedBreaches && data.detectedBreaches.length > 0) {
      setNotification({
        open: true,
        message: `${data.detectedBreaches.length} budget breaches detected!`,
        severity: 'error'
      });
    }
  });

  // Load initial dashboard data
  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const response = await apiService.getDashboard();
      if (response.success) {
        setDashboardData(response.data);
      }
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      setNotification({
        open: true,
        message: 'Failed to load dashboard data',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue);
  };

  const handleBudgetUploaded = async (result) => {
    setNotification({
      open: true,
      message: 'Budget file uploaded successfully!',
      severity: 'success'
    });
    await loadDashboardData();
  };

  const handleExpenseAdded = async (result) => {
    setNotification({
      open: true,
      message: 'Expense tracked successfully!',
      severity: 'success'
    });
    await loadDashboardData();
  };

  const closeNotification = () => {
    setNotification({ ...notification, open: false });
  };

  // Calculate overall status
  const getOverallStatus = () => {
    if (dashboardData.detectedBreaches?.length > 0) {
      const criticalBreaches = dashboardData.detectedBreaches.filter(b => 
        b.severity === 'Critical' || b.severity === 'High'
      );
      return criticalBreaches.length > 0 ? 'Critical' : 'Warning';
    }
    return 'Safe';
  };

  const overallStatus = getOverallStatus();

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ flexGrow: 1 }}>
        {/* Header */}
        <AppBar position="static" elevation={1}>
          <Toolbar>
            <AccountBalance sx={{ mr: 2 }} />
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Smart Budget Enforcer
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Typography variant="body2">
                Status: <strong style={{ 
                  color: overallStatus === 'Critical' ? '#f44336' : 
                         overallStatus === 'Warning' ? '#ff9800' : '#4caf50' 
                }}>
                  {overallStatus}
                </strong>
              </Typography>
              {isConnected ? (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Box sx={{ width: 8, height: 8, bgcolor: '#4caf50', borderRadius: '50%' }} />
                  <Typography variant="caption">Live</Typography>
                </Box>
              ) : (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Box sx={{ width: 8, height: 8, bgcolor: '#f44336', borderRadius: '50%' }} />
                  <Typography variant="caption">Offline</Typography>
                </Box>
              )}
            </Box>
          </Toolbar>
        </AppBar>

        {/* Main Content */}
        <Container maxWidth="xl" sx={{ mt: 2 }}>
          {/* Overview Cards */}
          <Grid container spacing={3} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h6" color="primary">
                  {dashboardData.budgetLoaded ? 'Budget Loaded' : 'No Budget'}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  {Object.keys(dashboardData.budgetData?.departments || {}).length} Departments
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h6" color="warning.main">
                  {Object.keys(dashboardData.expenseTracking || {}).length}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Categories Tracked
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h6" color="error.main">
                  {dashboardData.detectedBreaches?.length || 0}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Active Breaches
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h6" color="info.main">
                  {dashboardData.recommendations?.length || 0}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Recommendations
                </Typography>
              </Paper>
            </Grid>
          </Grid>

          {/* Navigation Tabs */}
          <Paper sx={{ width: '100%', mb: 2 }}>
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
              <Tabs value={currentTab} onChange={handleTabChange} variant="fullWidth">
                <Tab icon={<Dashboard />} label="Dashboard" />
                <Tab icon={<Upload />} label="Upload Budget" />
                <Tab icon={<TrendingUp />} label="Track Expenses" />
                <Tab icon={<Notifications />} label="Breach Alerts" />
                <Tab icon={<AccountBalance />} label="Recommendations" />
              </Tabs>
            </Box>

            {/* Tab Content */}
            <TabPanel value={currentTab} index={0}>
              <DashboardView 
                data={dashboardData} 
                loading={loading}
                onRefresh={loadDashboardData}
              />
            </TabPanel>

            <TabPanel value={currentTab} index={1}>
              <BudgetUpload 
                onUploadSuccess={handleBudgetUploaded}
                budgetLoaded={dashboardData.budgetLoaded}
              />
            </TabPanel>

            <TabPanel value={currentTab} index={2}>
              <ExpenseList 
                budgetData={dashboardData.budgetData}
                expenseTracking={dashboardData.expenseTracking}
                onExpenseAdded={handleExpenseAdded}
                budgetLoaded={dashboardData.budgetLoaded}
              />
            </TabPanel>

            <TabPanel value={currentTab} index={3}>
              <BreachAlerts 
                breaches={dashboardData.detectedBreaches}
                notifications={dashboardData.notifications}
              />
            </TabPanel>

            <TabPanel value={currentTab} index={4}>
              <Recommendations 
                recommendations={dashboardData.recommendations}
                breaches={dashboardData.detectedBreaches}
              />
            </TabPanel>
          </Paper>
        </Container>

        {/* Notifications */}
        <Snackbar
          open={notification.open}
          autoHideDuration={6000}
          onClose={closeNotification}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        >
          <Alert onClose={closeNotification} severity={notification.severity} sx={{ width: '100%' }}>
            {notification.message}
          </Alert>
        </Snackbar>
      </Box>
    </ThemeProvider>
  );
}

export default App;