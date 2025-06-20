import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  TextField,
  MenuItem,
  Grid,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Fab
} from '@mui/material';
import {
  Add,
  AttachMoney,
  Business,
  Category,
  Store,
  Send
} from '@mui/icons-material';
import { apiService } from '../services/api';

const ExpenseList = ({ budgetData, expenseTracking, onExpenseAdded, budgetLoaded }) => {
  const [expenses, setExpenses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    amount: '',
    department: '',
    category: '',
    vendor: '',
    description: ''
  });
  const [formErrors, setFormErrors] = useState({});

  // Load expenses on component mount
  useEffect(() => {
    loadExpenses();
  }, []);

  const loadExpenses = async () => {
    try {
      setLoading(true);
      const response = await apiService.getExpenses();
      if (response.success) {
        setExpenses(response.expenses || []);
      }
    } catch (error) {
      console.error('Error loading expenses:', error);
    } finally {
      setLoading(false);
    }
  };

  // Get departments and categories from budget data
  const getDepartments = () => {
    return Object.keys(budgetData?.departments || {});
  };

  const getCategories = (department) => {
    if (!department || !budgetData?.departments?.[department]) return [];
    return Object.keys(budgetData.departments[department].categories || {});
  };

  const getVendors = (department) => {
    if (!department || !budgetData?.departments?.[department]) return [];
    return budgetData.departments[department].categories?.vendors || [];
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
      // Reset dependent fields
      ...(field === 'department' ? { category: '', vendor: '' } : {})
    }));

    // Clear error for this field
    if (formErrors[field]) {
      setFormErrors(prev => ({
        ...prev,
        [field]: null
      }));
    }
  };

  const validateForm = () => {
    const errors = {};

    if (!formData.amount || isNaN(formData.amount) || parseFloat(formData.amount) <= 0) {
      errors.amount = 'Please enter a valid amount greater than 0';
    }

    if (!formData.department) {
      errors.department = 'Please select a department';
    }

    if (!formData.category) {
      errors.category = 'Please select a category';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;

    try {
      setLoading(true);
      
      const expenseData = {
        amount: parseFloat(formData.amount),
        department: formData.department,
        category: formData.category,
        vendor: formData.vendor || 'Unknown',
        description: formData.description || 'No description'
      };

      console.log('💰 Submitting expense:', expenseData);

      const response = await apiService.trackExpense(expenseData);
      
      if (response.success) {
        // Add to local state
        setExpenses(prev => [
          {
            ...expenseData,
            id: `exp_${Date.now()}`,
            timestamp: new Date().toISOString(),
            status: 'Tracked'
          },
          ...prev
        ]);

        // Reset form
        setFormData({
          amount: '',
          department: '',
          category: '',
          vendor: '',
          description: ''
        });

        setDialogOpen(false);

        if (onExpenseAdded) {
          onExpenseAdded(response);
        }

        // Reload expenses to get updated data
        setTimeout(() => {
          loadExpenses();
        }, 1000);
      }

    } catch (error) {
      console.error('Error tracking expense:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (usage) => {
    if (usage >= 100) return 'error';
    if (usage >= 80) return 'warning';
    return 'success';
  };

  const getStatusText = (usage) => {
    if (usage >= 100) return 'Over Budget';
    if (usage >= 80) return 'Approaching Limit';
    return 'Within Budget';
  };

  // Calculate usage for display
  const getCategoryUsage = (department, category) => {
    const tracking = expenseTracking?.[department]?.[category];
    if (!tracking) return { spent: 0, limit: 0, usage: 0 };
    
    const spent = tracking.spent || 0;
    const limit = tracking.limit || 0;
    const usage = limit > 0 ? (spent / limit) * 100 : 0;
    
    return { spent, limit, usage };
  };

  if (!budgetLoaded) {
    return (
      <Box>
        <Typography variant="h4" component="h1" gutterBottom>
          Track Expenses
        </Typography>
        <Alert severity="warning">
          Please upload a budget file first to start tracking expenses.
        </Alert>
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Track Expenses
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setDialogOpen(true)}
          disabled={loading}
        >
          Add Expense
        </Button>
      </Box>

      <Typography variant="body1" color="textSecondary" paragraph>
        Track new expenses against your budget limits. The Real-Time Expense Tracker Agent monitors 
        transactions and automatically detects budget breaches.
      </Typography>

      {/* Current Budget Status */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {getDepartments().map(dept => {
          const deptData = budgetData.departments[dept];
          const categories = Object.keys(deptData.categories || {});
          
          return (
            <Grid item xs={12} sm={6} md={4} key={dept}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {dept} Department
                  </Typography>
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    Budget: ${deptData.total_budget?.toLocaleString() || 'N/A'}
                  </Typography>
                  
                  {categories.map(category => {
                    const usage = getCategoryUsage(dept, category);
                    return (
                      <Box key={category} sx={{ mt: 1 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Typography variant="caption">
                            {category}
                          </Typography>
                          <Chip 
                            size="small"
                            label={`${usage.usage.toFixed(1)}%`}
                            color={getStatusColor(usage.usage)}
                          />
                        </Box>
                        <Typography variant="caption" color="textSecondary">
                          ${usage.spent.toLocaleString()} / ${usage.limit.toLocaleString()}
                        </Typography>
                      </Box>
                    );
                  })}
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>

      {/* Recent Expenses Table */}
      <Paper sx={{ mb: 3 }}>
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Typography variant="h6">
            Recent Expenses
          </Typography>
        </Box>
        
        {loading && expenses.length === 0 ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : expenses.length === 0 ? (
          <Box sx={{ textAlign: 'center', p: 4 }}>
            <Typography variant="body1" color="textSecondary">
              No expenses tracked yet. Add your first expense to get started.
            </Typography>
          </Box>
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Date</TableCell>
                  <TableCell>Department</TableCell>
                  <TableCell>Category</TableCell>
                  <TableCell>Vendor</TableCell>
                  <TableCell>Amount</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Description</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {expenses.slice(0, 20).map((expense, index) => {
                  const usage = getCategoryUsage(expense.department, expense.category);
                  return (
                    <TableRow key={expense.id || index}>
                      <TableCell>
                        {new Date(expense.timestamp).toLocaleDateString()}
                      </TableCell>
                      <TableCell>{expense.department}</TableCell>
                      <TableCell>{expense.category}</TableCell>
                      <TableCell>{expense.vendor}</TableCell>
                      <TableCell>${expense.amount?.toLocaleString()}</TableCell>
                      <TableCell>
                        <Chip 
                          size="small"
                          label={getStatusText(usage.usage)}
                          color={getStatusColor(usage.usage)}
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" noWrap>
                          {expense.description}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Paper>

      {/* Add Expense Dialog */}
      <Dialog 
        open={dialogOpen} 
        onClose={() => setDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Add New Expense
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Amount"
                type="number"
                value={formData.amount}
                onChange={(e) => handleInputChange('amount', e.target.value)}
                error={!!formErrors.amount}
                helperText={formErrors.amount}
                InputProps={{
                  startAdornment: <AttachMoney />
                }}
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                select
                label="Department"
                value={formData.department}
                onChange={(e) => handleInputChange('department', e.target.value)}
                error={!!formErrors.department}
                helperText={formErrors.department}
                InputProps={{
                  startAdornment: <Business />
                }}
              >
                {getDepartments().map(dept => (
                  <MenuItem key={dept} value={dept}>
                    {dept}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                select
                label="Category"
                value={formData.category}
                onChange={(e) => handleInputChange('category', e.target.value)}
                error={!!formErrors.category}
                helperText={formErrors.category}
                disabled={!formData.department}
                InputProps={{
                  startAdornment: <Category />
                }}
              >
                {getCategories(formData.department).map(category => (
                  <MenuItem key={category} value={category}>
                    {category}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Vendor"
                value={formData.vendor}
                onChange={(e) => handleInputChange('vendor', e.target.value)}
                placeholder="e.g., Microsoft, Google, Amazon"
                InputProps={{
                  startAdornment: <Store />
                }}
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                multiline
                rows={2}
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                placeholder="Brief description of the expense"
              />
            </Grid>

            {/* Current Category Status */}
            {formData.department && formData.category && (
              <Grid item xs={12}>
                <Alert 
                  severity={
                    getCategoryUsage(formData.department, formData.category).usage >= 80 ? 'warning' : 'info'
                  }
                >
                  <Typography variant="body2">
                    <strong>{formData.department} - {formData.category}:</strong>
                    {' '}${getCategoryUsage(formData.department, formData.category).spent.toLocaleString()} 
                    {' '}/ ${getCategoryUsage(formData.department, formData.category).limit.toLocaleString()}
                    {' '}({getCategoryUsage(formData.department, formData.category).usage.toFixed(1)}% used)
                  </Typography>
                </Alert>
              </Grid>
            )}
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>
            Cancel
          </Button>
          <Button 
            variant="contained"
            onClick={handleSubmit}
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : <Send />}
          >
            {loading ? 'Tracking...' : 'Track Expense'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Floating Action Button for mobile */}
      <Fab
        color="primary"
        aria-label="add expense"
        sx={{ 
          position: 'fixed', 
          bottom: 16, 
          right: 16,
          display: { xs: 'flex', sm: 'none' }
        }}
        onClick={() => setDialogOpen(true)}
      >
        <Add />
      </Fab>
    </Box>
  );
};

export default ExpenseList;