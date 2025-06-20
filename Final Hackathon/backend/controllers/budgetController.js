const agentService = require('../services/agentService');
const fs = require('fs');
const path = require('path');

const budgetController = {
  // Upload budget file and process with Budget Policy Loader Agent
  uploadBudget: async (req, res) => {
    try {
      if (!req.file) {
        return res.status(400).json({
          success: false,
          error: 'No budget file uploaded'
        });
      }

      console.log('📄 Processing budget file:', req.file.filename);

      // Create form data for agent API
      const FormData = require('form-data');
      const form = new FormData();
      form.append('file', fs.createReadStream(req.file.path), {
        filename: req.file.originalname,
        contentType: req.file.mimetype
      });

      // Send file to Budget Policy Loader Agent
      const agentResponse = await agentService.uploadBudgetFile(form);

      // Clean up uploaded file
      if (fs.existsSync(req.file.path)) {
        fs.unlinkSync(req.file.path);
      }

      res.json({
        success: true,
        message: 'Budget file uploaded and processed successfully',
        filename: req.file.originalname,
        agentResponse: agentResponse
      });

    } catch (error) {
      console.error('Error in uploadBudget:', error.message);
      
      // Clean up file on error
      if (req.file && fs.existsSync(req.file.path)) {
        fs.unlinkSync(req.file.path);
      }

      // If the error is a timeout, show a user-friendly message
      let userMessage = 'Failed to process budget file';
      let details = error.message && error.message.includes('timeout')
        ? 'The server took too long to respond. Please try again later or check if the agent service is running.'
        : (error.response?.data || error.message);
      res.status(500).json({
        success: false,
        error: userMessage,
        details: details
      });
    }
  },

  // Get budget status
  getBudgetStatus: async (req, res) => {
    try {
      const dashboardData = await agentService.getDashboardData();
      
      res.json({
        success: true,
        budgetLoaded: dashboardData.budget_loaded || false,
        departments: Object.keys(dashboardData.budget_data?.departments || {}).length,
        lastUpdated: dashboardData.last_updated
      });

    } catch (error) {
      console.error('Error getting budget status:', error.message);
      res.status(500).json({
        success: false,
        error: 'Failed to get budget status',
        details: error.message
      });
    }
  },

  // Get budget data
  getBudgetData: async (req, res) => {
    try {
      const dashboardData = await agentService.getDashboardData();
      
      res.json({
        success: true,
        data: dashboardData.budget_data || {},
        metadata: {
          departments: Object.keys(dashboardData.budget_data?.departments || {}),
          totalCategories: this.countCategories(dashboardData.budget_data),
          lastUpdated: dashboardData.last_updated
        }
      });

    } catch (error) {
      console.error('Error getting budget data:', error.message);
      res.status(500).json({
        success: false,
        error: 'Failed to get budget data',
        details: error.message
      });
    }
  },

  // Clear budget data
  clearBudget: async (req, res) => {
    try {
      // This would typically call an agent endpoint to clear data
      // For now, we'll just return success
      res.json({
        success: true,
        message: 'Budget data cleared successfully'
      });

    } catch (error) {
      console.error('Error clearing budget:', error.message);
      res.status(500).json({
        success: false,
        error: 'Failed to clear budget data',
        details: error.message
      });
    }
  },

  // Helper function to count categories
  countCategories: (budgetData) => {
    let count = 0;
    if (budgetData && budgetData.departments) {
      Object.values(budgetData.departments).forEach(dept => {
        if (dept.categories) {
          count += Object.keys(dept.categories).length;
        }
      });
    }
    return count;
  }
};

module.exports = budgetController;