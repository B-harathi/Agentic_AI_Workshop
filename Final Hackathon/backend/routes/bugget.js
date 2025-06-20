const express = require('express');
const router = express.Router();
const budgetController = require('../controllers/budgetController');
const upload = require('../middleware/upload');

// Budget routes
router.post('/upload', upload.single('budget'), budgetController.uploadBudget);
router.get('/status', budgetController.getBudgetStatus);
router.get('/data', budgetController.getBudgetData);
router.delete('/clear', budgetController.clearBudget);

module.exports = router;