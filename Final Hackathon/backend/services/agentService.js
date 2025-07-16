const axios = require('axios');
const config = require('./config');

const AGENT_BASE_URL = process.env.AGENT_BASE_URL || 'http://localhost:8000';

const agentService = {
  // Check agent health
  checkHealth: async () => {
    try {
      const response = await axios.get(`${AGENT_BASE_URL}/agents/status`, {
        timeout: 5000
      });
      return response.data;
    } catch (error) {
      return { success: false, error: 'Agent health check failed', details: error.message };
    }
  },

  // Upload budget file
  uploadBudgetFile: async (formData) => {
    try {
      const response = await axios.post(`${AGENT_BASE_URL}/upload-budget`, formData, {
        headers: formData.getHeaders(),
        timeout: 30000
      });
      return response.data;
    } catch (error) {
      return { success: false, error: 'Budget upload failed', details: error.message };
    }
  },

  // Track expense
  trackExpense: async (expenseData) => {
    try {
      const response = await axios.post(`${AGENT_BASE_URL}/track-expense`, expenseData, {
        timeout: 10000
      });
      return response.data;
    } catch (error) {
      return { success: false, error: 'Expense tracking failed', details: error.message };
    }
  },

  // Detect breaches
  detectBreaches: async () => {
    try {
      const response = await axios.post(`${AGENT_BASE_URL}/detect-breaches`, {}, {
        timeout: 15000
      });
      return response.data;
    } catch (error) {
      return { success: false, error: 'Breach detection failed', details: error.message };
    }
  },

  // Generate recommendations
  generateRecommendations: async () => {
    try {
      const response = await axios.post(`${AGENT_BASE_URL}/generate-recommendations`, {}, {
        timeout: 15000
      });
      return response.data;
    } catch (error) {
      return { success: false, error: 'Recommendation generation failed', details: error.message };
    }
  },

  // Send escalation
  sendEscalation: async () => {
    try {
      const response = await axios.post(`${AGENT_BASE_URL}/send-escalation`, {}, {
        timeout: 10000
      });
      return response.data;
    } catch (error) {
      return { success: false, error: 'Escalation failed', details: error.message };
    }
  },

  // Get dashboard data
  getDashboardData: async () => {
    try {
      const response = await axios.get(`${AGENT_BASE_URL}/dashboard-data`, {
        timeout: 10000
      });
      return response.data.dashboard_data;
    } catch (error) {
      return { success: false, error: 'Dashboard data retrieval failed', details: error.message };
    }
  },

  // Process complete flow
  processCompleteFlow: async (data) => {
    try {
      const response = await axios.post(`${AGENT_BASE_URL}/process-complete-flow`, data, {
        timeout: 30000
      });
      return response.data;
    } catch (error) {
      return { success: false, error: 'Complete flow processing failed', details: error.message };
    }
  },

  // Get agent status
  getAgentStatus: async () => {
    try {
      const response = await axios.get(`${AGENT_BASE_URL}/agents/status`, {
        timeout: 5000
      });
      return response.data;
    } catch (error) {
      return { success: false, error: 'Agent status retrieval failed', details: error.message };
    }
  },

  // Check high severity breaches
  checkHighSeverityBreaches: async () => {
    try {
      const dashboardData = await this.getDashboardData();
      const breaches = dashboardData.detected_breaches || [];
      return breaches.some(breach => 
        breach.severity === 'Critical' || breach.severity === 'High'
      );
    } catch (error) {
      return false;
    }
  }
};

module.exports = agentService;