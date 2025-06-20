import React from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  Button,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  RefreshIcon
} from '@mui/material';
import {
  Warning,
  CheckCircle,
  Error,
  TrendingUp,
  AttachMoney,
  Refresh
} from '@mui/icons-material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

// Enhanced dummy data
const dummyData = {
  budgetData: {
    departments: {
      Marketing: {
        total_budget: 50000,
        categories: {
          Advertising: { budget: 25000, constraints: ["Max $5,000 per campaign", "Monthly approval required"] },
          "Social Media": { budget: 15000, constraints: ["VP approval required for >$2,000"] },
          "Content Creation": { budget: 10000, constraints: ["External vendor approval needed"] }
        }
      },
      Sales: {
        total_budget: 35000,
        categories: {
          Software: { budget: 20000, constraints: ["Renewal only after review", "IT approval required"] },
          CRM: { budget: 10000, constraints: ["No single deal >$2,000"] },
          "Training": { budget: 5000, constraints: ["HR approval required"] }
        }
      },
      IT: {
        total_budget: 40000,
        categories: {
          Hardware: { budget: 25000, constraints: ["Quarterly review required"] },
          Software: { budget: 15000, constraints: ["Security approval needed"] }
        }
      }
    }
  },
  expenseTracking: {
    Marketing: {
      Advertising: { spent: 18000, limit: 25000, usage_percent: 72 },
      "Social Media": { spent: 12500, limit: 15000, usage_percent: 83.3 },
      "Content Creation": { spent: 8500, limit: 10000, usage_percent: 85 }
    },
    Sales: {
      Software: { spent: 22000, limit: 20000, usage_percent: 110 },
      CRM: { spent: 7500, limit: 10000, usage_percent: 75 },
      Training: { spent: 3200, limit: 5000, usage_percent: 64 }
    },
    IT: {
      Hardware: { spent: 15000, limit: 25000, usage_percent: 60 },
      Software: { spent: 14800, limit: 15000, usage_percent: 98.7 }
    }
  },
  detectedBreaches: [
    {
      department: "Sales",
      category: "Software",
      amount: 22000,
      limit: 20000,
      detected_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
      severity: "high"
    },
    {
      department: "Marketing",
      category: "Social Media",
      amount: 12500,
      limit: 15000,
      detected_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
      severity: "warning"
    }
  ],
  notifications: [
    {
      subject: "Budget warning for Marketing - Social Media",
      sent_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
      type: "warning"
    },
    {
      subject: "Budget breach detected in Sales - Software",
      sent_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
      type: "breach"
    },
    {
      subject: "Monthly budget report generated",
      sent_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
      type: "info"
    }
  ],
  budgetLoaded: true,
  lastUpdated: new Date().toISOString()
};

const Dashboard = ({ data, loading, onRefresh }) => {
  // Use dummy data if no real data is provided or if data is empty
  const shouldUseDummyData = !data || Object.keys(data).length === 0 || !data.budgetData;
  const effectiveData = shouldUseDummyData ? dummyData : data;
  
  const budgetData = effectiveData?.budgetData || dummyData.budgetData;
  const departments = budgetData.departments || {};

  // Process budget usage data for charts
  const processChartData = () => {
    const chartData = [];
    const expenseTracking = effectiveData.expenseTracking || {};
    
    Object.entries(expenseTracking).forEach(([dept, categories]) => {
      Object.entries(categories || {}).forEach(([category, info]) => {
        if (!category.startsWith('_')) {
          chartData.push({
            name: `${dept}-${category}`,
            spent: info.spent || 0,
            limit: info.limit || 0,
            usage: info.usage_percent || 0,
            status: info.usage_percent >= 100 ? 'Over' : info.usage_percent >= 80 ? 'Warning' : 'Safe'
          });
        }
      });
    });
    
    return chartData;
  };

  const chartData = processChartData();

  // Status color mapping
  const getStatusColor = (status) => {
    switch (status) {
      case 'Over': return '#f44336';
      case 'Warning': return '#ff9800';
      case 'Safe': return '#4caf50';
      default: return '#9e9e9e';
    }
  };

  // Recent activities
  const recentActivities = [
    ...(effectiveData.detectedBreaches || []).slice(0, 3).map(breach => ({
      type: 'breach',
      message: `Budget breach in ${breach.department} - ${breach.category}`,
      severity: 'error',
      time: breach.detected_at || new Date().toISOString()
    })),
    ...(effectiveData.notifications || []).slice(0, 2).map(notif => ({
      type: 'notification',
      message: `Alert sent: ${notif.subject}`,
      severity: 'info',
      time: notif.sent_at || new Date().toISOString()
    }))
  ].sort((a, b) => new Date(b.time) - new Date(a.time)).slice(0, 5);

  if (loading) {
    return (
      <Box sx={{ width: '100%', mt: 2 }}>
        <LinearProgress />
        <Typography variant="body2" sx={{ mt: 1, textAlign: 'center' }}>
          Loading dashboard data...
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" component="h1">
            Budget Dashboard
          </Typography>
          {shouldUseDummyData && (
            <Chip 
              label="Demo Mode - Using Sample Data" 
              color="info" 
              size="small" 
              sx={{ mt: 1 }} 
            />
          )}
        </Box>
        <Button
          variant="outlined"
          startIcon={<Refresh />}
          onClick={onRefresh}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>

      <Grid container spacing={3}>
        {/* Key Metrics */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Budget Usage Overview
            </Typography>
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
                  <YAxis />
                  <Tooltip 
                    formatter={(value, name) => [
                      name === 'spent' ? `$${value.toLocaleString()}` : `$${value.toLocaleString()}`,
                      name === 'spent' ? 'Spent' : 'Limit'
                    ]}
                  />
                  <Bar dataKey="spent" fill="#2196f3" name="Spent" />
                  <Bar dataKey="limit" fill="#e0e0e0" name="Budget Limit" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="body1" color="textSecondary">
                  No expense data available. Upload a budget and track some expenses to see charts.
                </Typography>
              </Box>
            )}
          </Paper>

          {/* Budget Status by Department */}
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Department Status
            </Typography>
            <Grid container spacing={2}>
              {Object.entries(departments).map(([dept, deptData]) => {
                const deptTracking = effectiveData.expenseTracking?.[dept] || {};
                const totalSpent = Object.values(deptTracking)
                  .filter(cat => typeof cat === 'object' && !Object.keys(cat).some(k => k.startsWith('_')))
                  .reduce((sum, cat) => sum + (cat.spent || 0), 0);
                const totalLimit = deptData.total_budget || 0;
                const usage = totalLimit > 0 ? (totalSpent / totalLimit) * 100 : 0;

                return (
                  <Grid item xs={12} sm={6} md={4} key={dept}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          {dept}
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                          <Typography variant="body2">
                            ${totalSpent.toLocaleString()} / ${totalLimit.toLocaleString()}
                          </Typography>
                          <Chip 
                            size="small"
                            label={`${usage.toFixed(1)}%`}
                            color={usage >= 100 ? 'error' : usage >= 80 ? 'warning' : 'success'}
                          />
                        </Box>
                        <LinearProgress 
                          variant="determinate" 
                          value={Math.min(usage, 100)} 
                          color={usage >= 100 ? 'error' : usage >= 80 ? 'warning' : 'success'}
                        />
                        <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
                          {Object.keys(deptData.categories || {}).length} categories
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                );
              })}
            </Grid>
          </Paper>
        </Grid>

        {/* Sidebar */}
        <Grid item xs={12} md={4}>
          {/* Status Summary */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              System Status
            </Typography>
            <List dense>
              <ListItem>
                <ListItemIcon>
                  {effectiveData.budgetLoaded ? <CheckCircle color="success" /> : <Error color="error" />}
                </ListItemIcon>
                <ListItemText 
                  primary="Budget Status"
                  secondary={effectiveData.budgetLoaded ? 'Loaded & Active' : 'Not Loaded'}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <TrendingUp color={effectiveData.detectedBreaches?.length > 0 ? 'error' : 'success'} />
                </ListItemIcon>
                <ListItemText 
                  primary="Budget Health"
                  secondary={`${effectiveData.detectedBreaches?.length || 0} active breaches`}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <AttachMoney color="primary" />
                </ListItemIcon>
                <ListItemText 
                  primary="Tracking"
                  secondary={`${Object.keys(effectiveData.expenseTracking || {}).length} departments monitored`}
                />
              </ListItem>
            </List>
          </Paper>

          {/* Recent Activity */}
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Recent Activity
            </Typography>
            {recentActivities.length > 0 ? (
              <List dense>
                {recentActivities.map((activity, index) => (
                  <ListItem key={index} divider={index < recentActivities.length - 1}>
                    <ListItemIcon>
                      {activity.type === 'breach' ? (
                        <Warning color="error" />
                      ) : (
                        <CheckCircle color="info" />
                      )}
                    </ListItemIcon>
                    <ListItemText 
                      primary={activity.message}
                      secondary={new Date(activity.time).toLocaleString()}
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Typography variant="body2" color="textSecondary">
                No recent activity
              </Typography>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Last Updated */}
      {effectiveData.lastUpdated && (
        <Box sx={{ mt: 2, textAlign: 'center' }}>
          <Typography variant="caption" color="textSecondary">
            Last updated: {new Date(effectiveData.lastUpdated).toLocaleString()}
            {shouldUseDummyData && ' (Demo Data)'}
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default Dashboard;