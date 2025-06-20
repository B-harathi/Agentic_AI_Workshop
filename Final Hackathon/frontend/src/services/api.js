import axios from 'axios';

// Configure axios defaults
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3002/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    console.log(`Response from ${response.config.url}:`, response.status);
    return response;
  },
  (error) => {
    console.error('Response error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const apiService = {
  // Budget endpoints
  uploadBudget: async (file) => {
    const formData = new FormData();
    formData.append('budget', file);
    
    const response = await apiClient.post('/upload-budget', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  getBudgetStatus: async () => {
    const response = await apiClient.get('/budget/status');
    return response.data;
  },

  getBudgetData: async () => {
    const response = await apiClient.get('/budget/data');
    return response.data;
  },

  // Expense endpoints
  trackExpense: async (expenseData) => {
    const response = await apiClient.post('/track-expense', expenseData);
    return response.data;
  },

  getExpenses: async () => {
    const response = await apiClient.get('/expenses/list');
    return response.data;
  },

  getBudgetUsage: async () => {
    const response = await apiClient.get('/expenses/usage');
    return response.data;
  },

  trackBulkExpenses: async (expenses) => {
    const response = await apiClient.post('/expenses/bulk', { expenses });
    return response.data;
  },

  // Breach detection endpoints
  detectBreaches: async () => {
    const response = await apiClient.post('/detect-breaches');
    return response.data;
  },

  // Recommendations endpoints
  generateRecommendations: async () => {
    const response = await apiClient.post('/generate-recommendations');
    return response.data;
  },

  // Escalation endpoints
  sendEscalation: async () => {
    const response = await apiClient.post('/send-escalation');
    return response.data;
  },

  // Agent endpoints
  getAgentStatus: async () => {
    const response = await apiClient.get('/agents/status');
    return response.data;
  },

  checkAgentHealth: async () => {
    const response = await apiClient.get('/agents/health');
    return response.data;
  },

  processCompleteFlow: async (flowData) => {
    const response = await apiClient.post('/agents/process-flow', flowData);
    return response.data;
  },

  // Dashboard endpoints
  getDashboard: async () => {
    const response = await apiClient.get('/dashboard');
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },

  // Manual workflow triggers
  triggerWorkflow: async (workflowType, data = {}) => {
    const response = await apiClient.post('/agents/trigger-workflow', {
      workflowType,
      data
    });
    return response.data;
  }
};

export default apiService;