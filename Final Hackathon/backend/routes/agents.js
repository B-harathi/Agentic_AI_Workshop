const express = require('express');
const router = express.Router();
const agentController = require('../controllers/agentController');

// Agent communication routes
router.get('/status', agentController.getAgentStatus);
router.post('/detect-breaches', agentController.detectBreaches);
router.post('/generate-recommendations', agentController.generateRecommendations);
router.post('/send-escalation', agentController.sendEscalation);
router.post('/process-flow', agentController.processCompleteFlow);
router.get('/health', agentController.checkAgentHealth);

module.exports = router;