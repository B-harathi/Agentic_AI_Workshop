const express = require('express');
const cors = require('cors');
const path = require('path');
const fs = require('fs');
const http = require('http');
const socketIo = require('socket.io');
require('dotenv').config();

// Import routes
const budgetRoutes = require('./routes/bugget');
const expenseRoutes = require('./routes/expenses');
const agentRoutes = require('./routes/agents');

// Import controllers for direct use
const budgetController = require('./controllers/budgetController');
const expenseController = require('./controllers/expenseController');
const agentController = require('./controllers/agentController');

// Import middleware
const upload = require('./middleware/upload');

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: process.env.FRONTEND_URL || "http://localhost:3000",
    methods: ["GET", "POST"]
  }
});

const PORT = process.env.PORT || 3002;
const AGENT_API_URL = process.env.AGENT_API_URL || 'http://localhost:8000';

// Middleware
app.use(cors({
  origin: [process.env.FRONTEND_URL || 'http://localhost:3000'],
  credentials: true
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Global state for dashboard
let dashboardState = {
  budgetLoaded: false,
  budgetData: {},
  expenseTracking: {},
  detectedBreaches: [],
  recommendations: [],
  notifications: [],
  lastUpdated: null
};

// Socket.io connection
io.on('connection', (socket) => {
  console.log('Client connected:', socket.id);
  
  // Send current dashboard state to new client
  socket.emit('dashboard-update', dashboardState);
  
  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
  });
});

// Helper function to update dashboard and notify clients
function updateDashboard(updates) {
  dashboardState = { ...dashboardState, ...updates, lastUpdated: new Date().toISOString() };
  io.emit('dashboard-update', dashboardState);
}

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    message: 'Smart Budget Enforcer Backend API',
    version: '1.0.0',
    status: 'Active',
    endpoints: {
      budget: '/api/budget',
      expenses: '/api/expenses',
      agents: '/api/agents',
      dashboard: '/api/dashboard'
    }
  });
});

// Health check
app.get('/health', async (req, res) => {
  try {
    const agentStatus = await agentController.checkAgentHealth();
    res.json({
      status: 'healthy',
      backend: 'running',
      agents: agentStatus,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(503).json({
      status: 'unhealthy',
      backend: 'running',
      agents: 'disconnected',
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

// API Routes
app.use('/api/budget', budgetRoutes);
app.use('/api/expenses', expenseRoutes);
app.use('/api/agents', agentRoutes);

// Direct endpoints for compatibility
app.post('/api/upload-budget', upload.single('budget'), async (req, res) => {
  try {
    await budgetController.uploadBudget(req, res);
    // Update dashboard after successful upload
    const dashboardData = await agentController.getDashboardData();
    if (dashboardData.success) {
      updateDashboard({
        budgetLoaded: true,
        budgetData: dashboardData.data.budgetData || {}
      });
    }
  } catch (error) {
    console.error('Error in upload-budget endpoint:', error);
    if (!res.headersSent) {
      res.status(500).json({ error: 'Internal server error' });
    }
  }
});

app.post('/api/track-expense', async (req, res) => {
  try {
    await expenseController.trackExpense(req, res);
    // Auto-trigger workflow after expense tracking
    setTimeout(async () => {
      try {
        await triggerWorkflowUpdates();
      } catch (error) {
        console.error('Auto workflow failed:', error.message);
      }
    }, 1000);
  } catch (error) {
    console.error('Error in track-expense endpoint:', error);
    if (!res.headersSent) {
      res.status(500).json({ error: 'Internal server error' });
    }
  }
});

app.post('/api/detect-breaches', async (req, res) => {
  try {
    await agentController.detectBreaches(req, res);
    await updateDashboardFromAgents();
  } catch (error) {
    console.error('Error in detect-breaches endpoint:', error);
    if (!res.headersSent) {
      res.status(500).json({ error: 'Internal server error' });
    }
  }
});

app.post('/api/generate-recommendations', async (req, res) => {
  try {
    await agentController.generateRecommendations(req, res);
    await updateDashboardFromAgents();
  } catch (error) {
    console.error('Error in generate-recommendations endpoint:', error);
    if (!res.headersSent) {
      res.status(500).json({ error: 'Internal server error' });
    }
  }
});

app.post('/api/send-escalation', async (req, res) => {
  try {
    await agentController.sendEscalation(req, res);
    await updateDashboardFromAgents();
  } catch (error) {
    console.error('Error in send-escalation endpoint:', error);
    if (!res.headersSent) {
      res.status(500).json({ error: 'Internal server error' });
    }
  }
});

app.get('/api/dashboard', async (req, res) => {
  try {
    await agentController.getDashboardData(req, res);
  } catch (error) {
    console.error('Error in dashboard endpoint:', error);
    if (!res.headersSent) {
      res.status(500).json({ error: 'Internal server error' });
    }
  }
});

// Helper functions
async function triggerWorkflowUpdates() {
  try {
    console.log('🔄 Triggering workflow updates...');
    
    // Detect breaches
    const breachReq = { body: {} };
    const breachRes = { 
      json: (data) => console.log('Breach detection result:', data.success),
      status: (code) => ({ json: (data) => console.log('Breach error:', data) })
    };
    await agentController.detectBreaches(breachReq, breachRes);
    
    // Update dashboard
    await updateDashboardFromAgents();
    
    console.log('✅ Workflow updates completed');
  } catch (error) {
    console.error('❌ Workflow update failed:', error.message);
  }
}

async function updateDashboardFromAgents() {
  try {
    const dashboardReq = { body: {} };
    const dashboardRes = {
      json: (data) => {
        if (data.success) {
          updateDashboard(data.data);
        }
      },
      status: (code) => ({
        json: (data) => console.warn('Dashboard update failed:', data)
      })
    };
    
    await agentController.getDashboardData(dashboardReq, dashboardRes);
  } catch (error) {
    console.warn('Dashboard update from agents failed:', error.message);
  }
}

// Create uploads directory
const uploadsDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir, { recursive: true });
}

// Error handling middleware
app.use((error, req, res, next) => {
  console.error('Server error:', error);
  res.status(500).json({
    error: 'Internal server error',
    message: error.message
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    error: 'Not Found',
    message: `Route ${req.method} ${req.url} not found`
  });
});

// Start server
server.listen(PORT, () => {
  console.log('\n🚀 Smart Budget Enforcer Backend Started');
  console.log(`📡 Server running on http://localhost:${PORT}`);
  console.log(`🤖 Python Agents API: ${AGENT_API_URL}`);
  console.log(`🔗 Frontend URL: ${process.env.FRONTEND_URL || 'http://localhost:3000'}`);
  console.log('\n📋 Available Endpoints:');
  console.log('   POST /api/upload-budget - Upload budget file');
  console.log('   POST /api/track-expense - Track new expense');
  console.log('   POST /api/detect-breaches - Detect budget breaches');
  console.log('   POST /api/generate-recommendations - Generate recommendations');
  console.log('   POST /api/send-escalation - Send escalation notifications');
  console.log('   GET  /api/dashboard - Get dashboard data');
  console.log('   GET  /health - Health check\n');
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  server.close(() => {
    console.log('Process terminated');
  });
});

process.on('SIGINT', () => {
  console.log('SIGINT received, shutting down gracefully');
  server.close(() => {
    console.log('Process terminated');
  });
});