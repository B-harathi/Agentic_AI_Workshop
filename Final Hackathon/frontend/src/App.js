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

// Dummy data for all dashboard sections
const dummyDashboardData = {
  budgetLoaded: true,
  budgetData: {
    departments: {
      Marketing: {
        total_budget: 30000,
        categories: {
          Advertising: { budget: 15000, constraints: ["Max $5,000 per campaign"] },
          "Social Media": { budget: 8000, constraints: ["VP approval required for >$2,000"] }
        }
      },
      Sales: {
        total_budget: 18000,
        categories: {
          Software: { budget: 12000, constraints: ["Renewal only after review"] },
          CRM: { budget: 6000, constraints: ["No single deal >$2,000"] }
        }
      }
    }
  },
  expenseTracking: {
    Marketing: {
      Advertising: { spent: 9000, limit: 15000, usage_percent: 60, transactions: [{ amount: 5000, vendor: "Google Ads", timestamp: "2024-06-01T10:00:00Z" }] },
      "Social Media": { spent: 4000, limit: 8000, usage_percent: 50, transactions: [{ amount: 2000, vendor: "Facebook", timestamp: "2024-06-02T11:00:00Z" }] }
    },
    Sales: {
      Software: { spent: 12000, limit: 12000, usage_percent: 100, transactions: [{ amount: 12000, vendor: "Salesforce", timestamp: "2024-06-03T12:00:00Z" }] },
      CRM: { spent: 2000, limit: 6000, usage_percent: 33, transactions: [{ amount: 2000, vendor: "HubSpot", timestamp: "2024-06-04T13:00:00Z" }] }
    }
  },
  detectedBreaches: [
    {
      department: "Sales",
      category: "Software",
      severity: "Critical",
      overage: 2000,
      detected_at: "2024-06-05T14:00:00Z"
    }
  ],
  recommendations: [
    {
      type: "Budget_Reallocation",
      description: "Reallocate $2,000 from Marketing to Sales Software.",
      target_savings: 2000
    },
    {
      type: "Spending_Pause",
      description: "Pause all new CRM purchases for 1 month.",
      target_savings: 1000
    }
  ],
  notifications: [
    {
      subject: "Critical Breach in Sales Software",
      sent_at: "2024-06-05T15:00:00Z"
    }
  ]
};

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
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
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

  // Define loadDashboardData for refresh actions
  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const response = await apiService.getDashboard();
      if (response.success && response.data && Object.keys(response.data.budgetData?.departments || {}).length > 0) {
        setDashboardData(response.data);
      } else {
        setDashboardData(dummyDashboardData);
      }
    } catch (error) {
      setDashboardData(dummyDashboardData);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

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

  // Defensive getOverallStatus
  function getOverallStatus(dashboardData) {
    if (!dashboardData || !Array.isArray(dashboardData.detectedBreaches)) {
      return 'No Data';
    }
    if (dashboardData.detectedBreaches.length === 0) {
      return 'Safe';
    }
    const critical = dashboardData.detectedBreaches.some(b => b.severity === 'Critical');
    if (critical) return 'Critical Breach';
    return 'Breaches Detected';
  }

  const overallStatus = getOverallStatus(dashboardData);

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
                  {dashboardData?.budgetLoaded ? 'Budget Loaded' : 'No Budget'}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  {Object.keys(dashboardData?.budgetData?.departments || {}).length} Departments
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h6" color="warning.main">
                  {Object.keys(dashboardData?.expenseTracking || {}).length}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Categories Tracked
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h6" color="error.main">
                  {dashboardData?.detectedBreaches?.length || 0}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Active Breaches
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h6" color="info.main">
                  {dashboardData?.recommendations?.length || 0}
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
                data={dashboardData || dummyDashboardData} 
                loading={loading}
                onRefresh={loadDashboardData}
              />
            </TabPanel>

            <TabPanel value={currentTab} index={1}>
              <BudgetUpload 
                onUploadSuccess={handleBudgetUploaded}
                budgetLoaded={dashboardData?.budgetLoaded || dummyDashboardData.budgetLoaded}
              />
            </TabPanel>

            <TabPanel value={currentTab} index={2}>
              <ExpenseList 
                budgetData={dashboardData?.budgetData || dummyDashboardData.budgetData}
                expenseTracking={dashboardData?.expenseTracking || dummyDashboardData.expenseTracking}
                onExpenseAdded={handleExpenseAdded}
                budgetLoaded={dashboardData?.budgetLoaded || dummyDashboardData.budgetLoaded}
              />
            </TabPanel>

            <TabPanel value={currentTab} index={3}>
              <BreachAlerts 
                breaches={dashboardData?.detectedBreaches || dummyDashboardData.detectedBreaches}
                notifications={dashboardData?.notifications || dummyDashboardData.notifications}
              />
            </TabPanel>

            <TabPanel value={currentTab} index={4}>
              <Recommendations 
                recommendations={dashboardData?.recommendations || dummyDashboardData.recommendations}
                breaches={dashboardData?.detectedBreaches || dummyDashboardData.detectedBreaches}
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