const axios = require('axios');

// Agent API configuration
const AGENT_API_URL = process.env.AGENT_API_URL || 'http://localhost:8000';

// Create axios instance for agent communication
const agentClient = axios.create({
  baseURL: AGENT_API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
agentClient.interceptors.request.use(
  (config) => {
    console.log(`🤖 Agent API: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Agent request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
agentClient.interceptors.response.use(
  (response) => {
    console.log(`✅ Agent API response: ${response.status}`);
    return response;
  },
  (error) => {
    console.error('❌ Agent API error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

const agentService = {
  // Budget Policy Loader Agent - Upload and process budget file
  uploadBudgetFile: async (formData) => {
    try {
      const response = await agentClient.post('/upload-budget', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error uploading budget file to agent:', error.message);
      throw error;
    }
  },

  // Real-Time Expense Tracker Agent - Track expense
  trackExpense: async (expenseData) => {
    try {
      const response = await agentClient.post('/track-expense', expenseData);
      return response.data;
    } catch (error) {
      console.error('Error tracking expense with agent:', error.message);
      throw error;
    }
  },

  // Breach Detector Agent - Detect budget breaches
  detectBreaches: async () => {
    try {
      const response = await agentClient.post('/detect-breaches');
      return response.data;
    } catch (error) {
      console.error('Error detecting breaches with agent:', error.message);
      throw error;
    }
  },

  // Correction Recommender Agent - Generate recommendations
  generateRecommendations: async () => {
    try {
      const response = await agentClient.post('/generate-recommendations');
      return response.data;
    } catch (error) {
      console.error('Error generating recommendations with agent:', error.message);
      throw error;
    }
  },

  // Escalation Communicator Agent - Send escalation notifications
  sendEscalation: async () => {
    try {
      const response = await agentClient.post('/send-escalation');
      return response.data;
    } catch (error) {
      console.error('Error sending escalation with agent:', error.message);
      throw error;
    }
  },

  // Get dashboard data from agents
  getDashboardData: async () => {
    try {
      const response = await agentClient.get('/dashboard-data');
      if (!response || !response.data) {
        throw new Error('No data received from agent');
      }
      // Defensive: ensure dashboard_data is an object
      const data = response.data.dashboard_data || response.data;
      return typeof data === 'object' && data !== null ? data : {};
    } catch (error) {
      console.error('Error getting dashboard data from agent:', error.message);
      // Return empty dashboard data if agents are unavailable
      return {
        budget_loaded: false,
        budget_data: {},
        expense_tracking: {},
        detected_breaches: [],
        recommendations: [],
        notifications: [],
        last_updated: new Date().toISOString()
      };
    }
  },

  // Get agent status
  getAgentStatus: async () => {
    try {
      const response = await agentClient.get('/agents/status');
      return response.data;
    } catch (error) {
      console.error('Error getting agent status:', error.message);
      throw error;
    }
  },

  // Process complete workflow
  processCompleteFlow: async (flowData) => {
    try {
      const response = await agentClient.post('/process-complete-flow', flowData);
      return response.data;
    } catch (error) {
      console.error('Error processing complete flow with agent:', error.message);
      throw error;
    }
  },

  // Check agent health
  checkHealth: async () => {
    try {
      const response = await agentClient.get('/');
      return {
        status: 'healthy',
        agents: response.data.agents || [],
        message: response.data.message
      };
    } catch (error) {
      console.error('Agent health check failed:', error.message);
      throw error;
    }
  },

  // Helper method to check if there are high severity breaches
  checkHighSeverityBreaches: async () => {
    try {
      const dashboardData = await agentService.getDashboardData();
      const breaches = dashboardData.detected_breaches || [];
      
      return breaches.some(breach => 
        breach.severity === 'Critical' || 
        breach.severity === 'High' ||
        breach.severity_level === 'Critical' ||
        breach.severity_level === 'High'
      );
    } catch (error) {
      console.error('Error checking high severity breaches:',error)
    }
}
}

module.exports = agentService;