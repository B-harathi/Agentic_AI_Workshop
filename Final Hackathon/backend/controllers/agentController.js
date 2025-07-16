const agentService = require('../services/agentService');
const axios = require('axios');

const agentController = {
  // Get status of all AI agents
  getAgentStatus: async (req, res) => {
    try {
      const agentStatus = await agentService.getAgentStatus();
      
      res.json({
        success: true,
        agents: agentStatus.agents,
        globalState: agentStatus.global_state,
        timestamp: new Date().toISOString()
      });

    } catch (error) {
      console.error('Error getting agent status:', error.message);
      res.status(503).json({
        success: false,
        error: 'Failed to get agent status',
        agents: 'disconnected',
        details: error.message
      });
    }
  },

  // Trigger breach detection across all agents
  detectBreaches: async (req, res) => {
    try {
      console.log('🚨 Triggering breach detection...');

      const breachResults = await agentService.detectBreaches();

      // Automatically trigger recommendations if breaches found
      if (breachResults.analysis_result?.breach_details?.length > 0) {
        console.log('🔍 Breaches detected, triggering recommendations...');
        
        setTimeout(async () => {
          try {
            await agentService.generateRecommendations();
            console.log('✅ Auto recommendations triggered');
          } catch (error) {
            console.error('❌ Auto recommendations failed:', error.message);
          }
        }, 1000);
      }

      res.json({
        success: true,
        message: 'Breach detection completed',
        breaches: breachResults.analysis_result?.breach_details || [],
        agentResponse: breachResults
      });

    } catch (error) {
      console.error('Error detecting breaches:', error.message);
      res.status(500).json({
        success: false,
        error: 'Failed to detect breaches',
        details: error.response?.data || error.message
      });
    }
  },

  // Generate corrective recommendations
  generateRecommendations: async (req, res) => {
    try {
      console.log('💡 Generating recommendations...');

      const recommendations = await agentService.generateRecommendations();

      // Check if we should auto-escalate based on severity
      const hasHighSeverityBreaches = await agentService.checkHighSeverityBreaches();
      
      if (hasHighSeverityBreaches) {
        console.log('⚠️ High severity breaches detected, triggering escalation...');
        
        setTimeout(async () => {
          try {
            await agentService.sendEscalation();
            console.log('✅ Auto escalation triggered');
          } catch (error) {
            console.error('❌ Auto escalation failed:', error.message);
          }
        }, 1000);
      }

      res.json({
        success: true,
        message: 'Recommendations generated successfully',
        recommendations: {
          reallocations: recommendations.reallocation_strategies?.reallocation_strategies || [],
          spendingPauses: recommendations.spending_pauses?.pause_suggestions || [],
          vendorNegotiations: recommendations.vendor_negotiations?.renegotiation_recommendations || []
        },
        agentResponse: recommendations
      });

    } catch (error) {
      console.error('Error generating recommendations:', error.message);
      res.status(500).json({
        success: false,
        error: 'Failed to generate recommendations',
        details: error.response?.data || error.message
      });
    }
  },

  // Send escalation notifications
  sendEscalation: async (req, res) => {
    try {
      console.log('📧 Sending escalation notifications...');

      const escalationResults = await agentService.sendEscalation();

      res.json({
        success: true,
        message: 'Escalation notifications sent successfully',
        notifications: escalationResults.email_alerts?.sent_details || [],
        executiveSummary: escalationResults.executive_summary || {},
        actionRequests: escalationResults.action_requests?.action_requests || [],
        agentResponse: escalationResults
      });

    } catch (error) {
      console.error('Error sending escalation:', error.message);
      res.status(500).json({
        success: false,
        error: 'Failed to send escalation notifications',
        details: error.response?.data || error.message
      });
    }
  },

  // Process complete workflow
  processCompleteFlow: async (req, res) => {
    try {
      console.log('🔄 Processing complete agent workflow...');

      const flowResults = await agentService.processCompleteFlow(req.body);

      res.json({
        success: true,
        message: 'Complete workflow processed successfully',
        workflow: flowResults.workflow_results,
        agentResponse: flowResults
      });

    } catch (error) {
      console.error('Error processing complete flow:', error.message);
      res.status(500).json({
        success: false,
        error: 'Failed to process complete workflow',
        details: error.response?.data || error.message
      });
    }
  },

  // Check agent health
  checkAgentHealth: async (req, res) => {
    try {
      const healthStatus = await agentService.checkHealth();
      
      res.json({
        success: true,
        status: 'healthy',
        agents: healthStatus,
        timestamp: new Date().toISOString()
      });

    } catch (error) {
      console.error('Agent health check failed:', error.message);
      res.status(503).json({
        success: false,
        status: 'unhealthy',
        error: 'Agent health check failed',
        details: error.message,
        timestamp: new Date().toISOString()
      });
    }
  },

  // Get dashboard data with agent state - FIXED VERSION
  getDashboardData: async (req, res) => {
    try {
      // Try to get data from agents, but don't fail if agents are unavailable
      let dashboardData = {
        budget_loaded: false,
        budget_data: {},
        expense_tracking: {},
        detected_breaches: [],
        recommendations: [],
        notifications: [],
        last_updated: new Date().toISOString()
      };

      try {
        dashboardData = await agentService.getDashboardData();
      } catch (agentError) {
        console.warn('⚠️ Agents unavailable, using default dashboard data:', agentError.message);
      }
      
      res.json({
        success: true,
        data: {
          budgetLoaded: dashboardData.budget_loaded || false,
          budgetData: dashboardData.budget_data || {},
          expenseTracking: dashboardData.expense_tracking || {},
          detectedBreaches: dashboardData.detected_breaches || [],
          recommendations: dashboardData.recommendations || [],
          notifications: dashboardData.notifications || [],
          lastUpdated: dashboardData.last_updated || new Date().toISOString(),
          summary: {
            totalDepartments: Object.keys(dashboardData.budget_data?.departments || {}).length,
            totalBreaches: (dashboardData.detected_breaches || []).length,
            totalRecommendations: (dashboardData.recommendations || []).length,
            criticalBreaches: (dashboardData.detected_breaches || []).filter(b => 
              b.severity === 'Critical' || b.severity === 'High'
            ).length
          }
        }
      });

    } catch (error) {
      console.error('Error getting dashboard data:', error.message);
      res.status(500).json({
        success: false,
        error: 'Failed to get dashboard data',
        details: error.message,
        data: {
          budgetLoaded: false,
          budgetData: {},
          expenseTracking: {},
          detectedBreaches: [],
          recommendations: [],
          notifications: [],
          lastUpdated: new Date().toISOString()
        }
      });
    }
  },

  // Manual workflow trigger
  triggerWorkflow: async (req, res) => {
    try {
      const { workflowType, data } = req.body;
      
      console.log(`🔧 Triggering manual workflow: ${workflowType}`);

      let result = {};

      switch (workflowType) {
        case 'full_detection':
          result.breaches = await agentService.detectBreaches();
          result.recommendations = await agentService.generateRecommendations();
          result.escalation = await agentService.sendEscalation();
          break;
          
        case 'recommendations_only':
          result.recommendations = await agentService.generateRecommendations();
          break;
          
        case 'escalation_only':
          result.escalation = await agentService.sendEscalation();
          break;
          
        default:
          return res.status(400).json({
            success: false,
            error: 'Invalid workflow type',
            validTypes: ['full_detection', 'recommendations_only', 'escalation_only']
          });
      }

      res.json({
        success: true,
        message: `Workflow ${workflowType} completed successfully`,
        results: result
      });

    } catch (error) {
      console.error('Error triggering workflow:', error.message);
      res.status(500).json({
        success: false,
        error: 'Failed to trigger workflow',
        details: error.message
      });
    }
  }
};

module.exports = agentController;