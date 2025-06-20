import json
from datetime import datetime
from typing import Dict, List, Any
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from base_agent import BaseAgent

class ExpenseTrackerAgent(BaseAgent):
    def __init__(self):
        self.expenses = []
        self.budget_thresholds = {}
        self.current_usage = {}
        super().__init__()
    
    def create_tools(self):
        return [
            Tool(
                name="load_budget_thresholds",
                description="Load budget thresholds from Budget Policy Loader Agent",
                func=self.load_budget_thresholds
            ),
            Tool(
                name="track_new_expense",
                description="Track a new expense transaction against budget limits",
                func=self.track_new_expense
            ),
            Tool(
                name="calculate_budget_usage",
                description="Calculate current budget usage percentages for all departments/categories",
                func=self.calculate_budget_usage
            ),
            Tool(
                name="get_real_time_status",
                description="Get real-time budget status with flags (Safe/Approaching/Exceeded)",
                func=self.get_real_time_status
            )
        ]
    
    def create_prompt(self):
        return PromptTemplate(
            input_variables=["input", "agent_scratchpad", "tools", "tool_names"],
            template="""
            You are a Real-Time Expense Tracker Agent that monitors transactions continuously.
            
            Your mission: Monitor live transactional data against predefined budget plans and thresholds.
            
            Tasks:
            1. Load budget thresholds from Budget Policy Loader Agent
            2. Track incoming expense entries in real-time
            3. Calculate usage percentages against budget limits
            4. Maintain department-wise and vendor-wise running totals
            5. Flag status as "Safe", "Approaching", or "Exceeded"
            
            Available tools: {tool_names}
            Tools: {tools}
            
            Input: {input}
            
            Thought: I need to monitor this expense transaction and update budget tracking.
            {agent_scratchpad}
            """
        )
    
    def load_budget_thresholds(self, budget_data: str) -> str:
        """Load budget thresholds from Budget Policy Loader Agent output"""
        try:
            if isinstance(budget_data, str):
                budget_info = json.loads(budget_data)
            else:
                budget_info = budget_data
                
            self.budget_thresholds = budget_info
            
            # Initialize usage tracking
            for dept, dept_info in budget_info.get('departments', {}).items():
                self.current_usage[dept] = {}
                for category in dept_info.get('categories', {}):
                    self.current_usage[dept][category] = {
                        'spent': 0,
                        'limit': dept_info['categories'][category]['limit'],
                        'transactions': []
                    }
            
            return f"Budget thresholds loaded successfully for {len(budget_info.get('departments', {}))} departments"
            
        except Exception as e:
            return f"Error loading budget thresholds: {str(e)}"
    
    def track_new_expense(self, expense_data: str) -> str:
        """Track new expense transaction and map against budget usage"""
        try:
            # Parse expense data
            if isinstance(expense_data, str):
                expense = json.loads(expense_data)
            else:
                expense = expense_data
            
            # Required fields: amount, department, category, vendor, description
            amount = expense['amount']
            department = expense['department']
            category = expense['category']
            vendor = expense.get('vendor', 'Unknown')
            description = expense.get('description', 'No description')
            
            # Create expense record
            expense_record = {
                'id': f"exp_{datetime.now().timestamp()}",
                'amount': amount,
                'department': department,
                'category': category,
                'vendor': vendor,
                'description': description,
                'timestamp': datetime.now().isoformat(),
                'status': 'pending'
            }
            
            # Update current usage
            if department in self.current_usage and category in self.current_usage[department]:
                self.current_usage[department][category]['spent'] += amount
                self.current_usage[department][category]['transactions'].append(expense_record)
                
                # Determine status
                spent = self.current_usage[department][category]['spent']
                limit = self.current_usage[department][category]['limit']
                usage_percent = (spent / limit) * 100
                
                if usage_percent >= 100:
                    status = "Exceeded"
                elif usage_percent >= 80:
                    status = "Approaching"
                else:
                    status = "Safe"
                    
                expense_record['status'] = status
                expense_record['usage_percent'] = usage_percent
            
            self.expenses.append(expense_record)
            
            return json.dumps({
                'message': f'Expense tracked: ${amount} for {department}/{category}',
                'expense_id': expense_record['id'],
                'status': expense_record['status'],
                'usage_percent': expense_record.get('usage_percent', 0),
                'total_expenses_tracked': len(self.expenses)
            })
            
        except Exception as e:
            return f"Error tracking expense: {str(e)}"
    
    def calculate_budget_usage(self, input_data: str) -> str:
        """Calculate current budget usage percentages for all departments/categories"""
        try:
            usage_report = {}
            
            for dept, categories in self.current_usage.items():
                usage_report[dept] = {}
                dept_total_spent = 0
                dept_total_limit = 0
                
                for category, info in categories.items():
                    spent = info['spent']
                    limit = info['limit']
                    usage_percent = (spent / limit) * 100 if limit > 0 else 0
                    
                    usage_report[dept][category] = {
                        'spent': spent,
                        'limit': limit,
                        'usage_percent': round(usage_percent, 2),
                        'remaining': limit - spent,
                        'transaction_count': len(info['transactions'])
                    }
                    
                    dept_total_spent += spent
                    dept_total_limit += limit
                
                # Department total
                dept_usage_percent = (dept_total_spent / dept_total_limit) * 100 if dept_total_limit > 0 else 0
                usage_report[dept]['_department_total'] = {
                    'spent': dept_total_spent,
                    'limit': dept_total_limit,
                    'usage_percent': round(dept_usage_percent, 2)
                }
            
            return json.dumps(usage_report, indent=2)
            
        except Exception as e:
            return f"Error calculating budget usage: {str(e)}"
    
    def get_real_time_status(self, input_data: str) -> str:
        """Get real-time budget status with status flags"""
        try:
            status_report = {
                'timestamp': datetime.now().isoformat(),
                'overall_status': 'Safe',
                'departments': {},
                'alerts': [],
                'summary': {
                    'total_expenses': len(self.expenses),
                    'departments_monitored': len(self.current_usage),
                    'breached_categories': 0,
                    'approaching_categories': 0
                }
            }
            
            breached_count = 0
            approaching_count = 0
            
            for dept, categories in self.current_usage.items():
                dept_status = {
                    'categories': {},
                    'status': 'Safe'
                }
                
                for category, info in categories.items():
                    spent = info['spent']
                    limit = info['limit']
                    usage_percent = (spent / limit) * 100 if limit > 0 else 0
                    
                    # Determine status
                    if usage_percent >= 100:
                        category_status = "Exceeded"
                        breached_count += 1
                        dept_status['status'] = 'Exceeded'
                        status_report['overall_status'] = 'Critical'
                        status_report['alerts'].append(f"{dept}/{category}: Budget exceeded by {usage_percent-100:.1f}%")
                    elif usage_percent >= 80:
                        category_status = "Approaching"
                        approaching_count += 1
                        if dept_status['status'] == 'Safe':
                            dept_status['status'] = 'Warning'
                        if status_report['overall_status'] == 'Safe':
                            status_report['overall_status'] = 'Warning'
                        status_report['alerts'].append(f"{dept}/{category}: Approaching limit at {usage_percent:.1f}%")
                    else:
                        category_status = "Safe"
                    
                    dept_status['categories'][category] = {
                        'spent': spent,
                        'limit': limit,
                        'usage_percent': round(usage_percent, 2),
                        'status': category_status,
                        'last_transaction': info['transactions'][-1]['timestamp'] if info['transactions'] else None
                    }
                
                status_report['departments'][dept] = dept_status
            
            status_report['summary']['breached_categories'] = breached_count
            status_report['summary']['approaching_categories'] = approaching_count
            
            return json.dumps(status_report, indent=2)
            
        except Exception as e:
            return f"Error getting real-time status: {str(e)}"
    
    def get_current_usage_data(self):
        """Return current usage data for other agents"""
        return self.current_usage