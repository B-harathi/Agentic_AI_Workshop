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

const Dashboard = ({ data, loading, onRefresh }) => {
  // Process budget usage data for charts
  const processChartData = () => {
    const chartData = [];
    
    Object.entries(data.expenseTracking || {}).forEach(([dept, categories]) => {
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
    ...(data.detectedBreaches || []).slice(0, 3).map(breach => ({
      type: 'breach',
      message: `Budget breach in ${breach.department} - ${breach.category}`,
      severity: 'error',
      time: breach.detected_at || new Date().toISOString()
    })),
    ...(data.notifications || []).slice(0, 2).map(notif => ({
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
        <Typography variant="h4" component="h1">
          Budget Dashboard
        </Typography>
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
                  <Bar dataKey="spent" fill="#2196f3" />
                  <Bar dataKey="limit" fill="#e0e0e0" />
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
              {Object.entries(data.budgetData?.departments || {}).map(([dept, deptInfo]) => {
                const deptTracking = data.expenseTracking?.[dept] || {};
                const totalSpent = Object.values(deptTracking)
                  .filter(cat => !Object.keys(cat).some(k => k.startsWith('_')))
                  .reduce((sum, cat) => sum + (cat.spent || 0), 0);
                const totalLimit = deptInfo.total_budget || 0;
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
                  {data.budgetLoaded ? <CheckCircle color="success" /> : <Error color="error" />}
                </ListItemIcon>
                <ListItemText 
                  primary="Budget Status"
                  secondary={data.budgetLoaded ? 'Loaded & Active' : 'Not Loaded'}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <TrendingUp color={data.detectedBreaches?.length > 0 ? 'error' : 'success'} />
                </ListItemIcon>
                <ListItemText 
                  primary="Budget Health"
                  secondary={`${data.detectedBreaches?.length || 0} active breaches`}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <AttachMoney color="primary" />
                </ListItemIcon>
                <ListItemText 
                  primary="Tracking"
                  secondary={`${Object.keys(data.expenseTracking || {}).length} departments monitored`}
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
      {data.lastUpdated && (
        <Box sx={{ mt: 2, textAlign: 'center' }}>
          <Typography variant="caption" color="textSecondary">
            Last updated: {new Date(data.lastUpdated).toLocaleString()}
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default Dashboard;