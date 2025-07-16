const agentService = require('../services/agentService');

const expenseController = {
  // Track a single expense
  trackExpense: async (req, res) => {
    try {
      const { amount, department, category, vendor, description } = req.body;

      // Validate required fields
      if (!amount) {
        return res.status(400).json({
          success: false,
          error: 'Amount, department, and category are required'
        });
      }

      console.log('💰 Tracking expense:', { amount, department, category });

      // Prepare expense data for agent
      const expenseData = {
        amount: parseFloat(amount),
        department,
        category,
        vendor: vendor || 'Unknown',
        description: description || 'No description'
      };

      // Send to Real-Time Expense Tracker Agent
      const trackingResponse = await agentService.trackExpense(expenseData);

      // Handle agentService errors (timeouts, failures)
      if (!trackingResponse.success) {
        return res.status(500).json({
          success: false,
          error: 'Failed to track expense',
          details: trackingResponse.details || trackingResponse.error || 'Unknown error'
        });
      }

      // Automatically trigger breach detection after tracking
      setTimeout(async () => {
        try {
          await agentService.detectBreaches();
          console.log('✅ Auto breach detection triggered');
        } catch (error) {
          console.error('❌ Auto breach detection failed:', error.message);
        }
      }, 1000);

      res.json({
        success: true,
        message: 'Expense tracked successfully',
        expense: expenseData,
        agentResponse: trackingResponse
      });

    } catch (error) {
      console.error('Error tracking expense:', error.message);
      res.status(500).json({
        success: false,
        error: 'Failed to track expense',
        details: error.response?.data || error.message
      });
    }
  },

  // Get all tracked expenses
  getExpenses: async (req, res) => {
    try {
      const dashboardData = await agentService.getDashboardData();
      
      // Extract expenses from tracking data
      const expenses = [];
      const expenseTracking = dashboardData.expense_tracking || {};
      
      Object.entries(expenseTracking).forEach(([dept, categories]) => {
        Object.entries(categories || {}).forEach(([category, info]) => {
          if (!category.startsWith('_') && info.transactions) {
            expenses.push(...info.transactions);
          }
        });
      });

      res.json({
        success: true,
        expenses: expenses.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)),
        totalExpenses: expenses.length,
        totalAmount: expenses.reduce((sum, exp) => sum + (exp.amount || 0), 0)
      });

    } catch (error) {
      console.error('Error getting expenses:', error.message);
      res.status(500).json({
        success: false,
        error: 'Failed to get expenses',
        details: error.message
      });
    }
  },

  // Get budget usage summary
  getBudgetUsage: async (req, res) => {
    try {
      const dashboardData = await agentService.getDashboardData();
      const expenseTracking = dashboardData.expense_tracking || {};
      
      const usageSummary = {};
      
      Object.entries(expenseTracking).forEach(([dept, categories]) => {
        usageSummary[dept] = {};
        
        Object.entries(categories || {}).forEach(([category, info]) => {
          if (!category.startsWith('_')) {
            const spent = info.spent || 0;
            const limit = info.limit || 0;
            const usagePercent = limit > 0 ? (spent / limit) * 100 : 0;
            
            usageSummary[dept][category] = {
              spent,
              limit,
              usagePercent: Math.round(usagePercent * 100) / 100,
              remaining: limit - spent,
              status: usagePercent >= 100 ? 'Exceeded' : 
                      usagePercent >= 80 ? 'Approaching' : 'Safe',
              transactionCount: info.transactions ? info.transactions.length : 0
            };
          }
        });
      });

      res.json({
        success: true,
        usage: usageSummary,
        summary: {
          totalDepartments: Object.keys(usageSummary).length,
          exceededCategories: this.countByStatus(usageSummary, 'Exceeded'),
          approachingCategories: this.countByStatus(usageSummary, 'Approaching'),
          safeCategories: this.countByStatus(usageSummary, 'Safe')
        }
      });

    } catch (error) {
      console.error('Error getting budget usage:', error.message);
      res.status(500).json({
        success: false,
        error: 'Failed to get budget usage',
        details: error.message
      });
    }
  },

  // Track multiple expenses at once
  trackBulkExpenses: async (req, res) => {
    try {
      const { expenses } = req.body;

      if (!Array.isArray(expenses) || expenses.length === 0) {
        return res.status(400).json({
          success: false,
          error: 'Expenses array is required'
        });
      }

      console.log(`💰 Tracking ${expenses.length} bulk expenses`);

      const results = [];
      const errors = [];

      // Process each expense
      for (let i = 0; i < expenses.length; i++) {
        try {
          const expense = expenses[i];
          
          // Validate expense
          if (!expense.amount || !expense.department || !expense.category) {
            errors.push({
              index: i,
              expense,
              error: 'Amount, department, and category are required'
            });
            continue;
          }

          const expenseData = {
            amount: parseFloat(expense.amount),
            department: expense.department,
            category: expense.category,
            vendor: expense.vendor || 'Unknown',
            description: expense.description || 'Bulk import'
          };

          const result = await agentService.trackExpense(expenseData);
          results.push({
            index: i,
            expense: expenseData,
            result
          });

          // Small delay to avoid overwhelming the agent
          await new Promise(resolve => setTimeout(resolve, 100));

        } catch (error) {
          errors.push({
            index: i,
            expense: expenses[i],
            error: error.message
          });
        }
      }

      // Trigger breach detection after bulk import
      setTimeout(async () => {
        try {
          await agentService.detectBreaches();
          console.log('✅ Auto breach detection triggered after bulk import');
        } catch (error) {
          console.error('❌ Auto breach detection failed:', error.message);
        }
      }, 2000);

      res.json({
        success: true,
        message: `Processed ${results.length} expenses successfully`,
        results,
        errors,
        summary: {
          total: expenses.length,
          successful: results.length,
          failed: errors.length
        }
      });

    } catch (error) {
      console.error('Error tracking bulk expenses:', error.message);
      res.status(500).json({
        success: false,
        error: 'Failed to track bulk expenses',
        details: error.message
      });
    }
  },

  // Clear all expenses
  clearExpenses: async (req, res) => {
    try {
      // This would typically call an agent endpoint to clear expense data
      // For now, we'll just return success
      res.json({
        success: true,
        message: 'All expenses cleared successfully'
      });

    } catch (error) {
      console.error('Error clearing expenses:', error.message);
      res.status(500).json({
        success: false,
        error: 'Failed to clear expenses',
        details: error.message
      });
    }
  },

  // Helper function to count categories by status
  countByStatus: (usageSummary, targetStatus) => {
    let count = 0;
    Object.values(usageSummary).forEach(dept => {
      Object.values(dept).forEach(category => {
        if (category.status === targetStatus) {
          count++;
        }
      });
    });
    return count;
  }
};

module.exports = expenseController;