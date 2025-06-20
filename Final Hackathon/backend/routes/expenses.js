const express = require('express');
const router = express.Router();
const expenseController = require('../controllers/expenseController');

// Expense routes
router.post('/track', expenseController.trackExpense);
router.get('/list', expenseController.getExpenses);
router.get('/usage', expenseController.getBudgetUsage);
router.post('/bulk', expenseController.trackBulkExpenses);
router.delete('/clear', expenseController.clearExpenses);

module.exports = router;