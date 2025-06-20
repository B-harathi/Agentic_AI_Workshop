import json
from datetime import datetime
from typing import Dict, List, Any
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from base_agent import BaseAgent

class BreachDetectorAgent(BaseAgent):
    def __init__(self):
        self.detected_breaches = []
        self.breach_history = []
        super().__init__()
    
    def create_tools(self):
        return [
            Tool(
                name="analyze_expense_data",
                description="Analyze expense tracking data to identify budget breaches",
                func=self.analyze_expense_data
            ),
            Tool(
                name="detect_overspending_events",
                description="Detect overspending events and categorize by severity",
                func=self.detect_overspending_events
            ),
            Tool(
                name="score_breach_severity",
                description="Score breaches by overage percentage and recurrence",
                func=self.score_breach_severity
            ),
            Tool(
                name="link_triggering_transactions",
                description="Link breaches to specific triggering transactions for traceability",
                func=self.link_triggering_transactions
            )
        ]
    
    def create_prompt(self):
        return PromptTemplate(
            input_variables=["input", "agent_scratchpad", "tools", "tool_names"],
            template="""
            You are a Breach Detector Agent that identifies budget violations with precision.
            
            Your mission: Detect overspending events and categorize them based on severity.
            
            Tasks:
            1. Analyze real-time expense data from Expense Tracker Agent
            2. Detect 100% breaches against set thresholds
            3. Score breaches by overage percentage and recurrence
            4. Link to triggering transactions for traceability
            5. Categorize severity as Low/Medium/High/Critical
            
            Available tools: {tool_names}
            Tools: {tools}
            
            Input: {input}
            
            Thought: I need to analyze the expense data for budget violations.
            {agent_scratchpad}
            """
        )
    
    def analyze_expense_data(self, tracking_data: str) -> str:
        """Analyze expense tracking data to identify budget breaches"""
        try:
            if isinstance(tracking_data, str):
                data = json.loads(tracking_data)
            else:
                data = tracking_data
            
            breaches_found = []
            analysis_summary = {
                'total_departments': 0,
                'total_categories': 0,
                'breached_categories': 0,
                'approaching_categories': 0,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            for dept, categories in data.items():
                if dept.startswith('_'):  # Skip summary fields
                    continue
                    
                analysis_summary['total_departments'] += 1
                
                for category, info in categories.items():
                    if category.startswith('_'):  # Skip summary fields
                        continue
                        
                    analysis_summary['total_categories'] += 1
                    
                    usage_percent = info.get('usage_percent', 0)
                    spent = info.get('spent', 0)
                    limit = info.get('limit', 0)
                    
                    if usage_percent >= 100:
                        # Breach detected
                        breach = {
                            'id': f"breach_{datetime.now().timestamp()}_{dept}_{category}",
                            'department': dept,
                            'category': category,
                            'limit': limit,
                            'spent': spent,
                            'overage': spent - limit,
                            'usage_percent': usage_percent,
                            'overage_percent': usage_percent - 100,
                            'detected_at': datetime.now().isoformat(),
                            'status': 'Active',
                            'severity': self._calculate_severity(usage_percent)
                        }
                        breaches_found.append(breach)
                        analysis_summary['breached_categories'] += 1
                        
                    elif usage_percent >= 80:
                        analysis_summary['approaching_categories'] += 1
            
            # Store detected breaches
            self.detected_breaches.extend(breaches_found)
            
            result = {
                'analysis_summary': analysis_summary,
                'breaches_detected': len(breaches_found),
                'breach_details': breaches_found
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Error analyzing expense data: {str(e)}"
    
    def detect_overspending_events(self, expense_status: str) -> str:
        """Detect overspending events and categorize by severity"""
        try:
            if isinstance(expense_status, str):
                status_data = json.loads(expense_status)
            else:
                status_data = expense_status
            
            overspending_events = []
            
            # Check each department and category for overspending
            departments = status_data.get('departments', {})
            
            for dept, dept_info in departments.items():
                categories = dept_info.get('categories', {})
                
                for category, cat_info in categories.items():
                    usage_percent = cat_info.get('usage_percent', 0)
                    status = cat_info.get('status', 'Safe')
                    
                    if status == 'Exceeded':
                        event = {
                            'event_id': f"event_{datetime.now().timestamp()}_{dept}_{category}",
                            'type': 'Budget_Overspend',
                            'department': dept,
                            'category': category,
                            'current_spend': cat_info.get('spent', 0),
                            'budget_limit': cat_info.get('limit', 0),
                            'usage_percent': usage_percent,
                            'severity': self._calculate_severity(usage_percent),
                            'detected_timestamp': datetime.now().isoformat(),
                            'requires_action': True
                        }
                        
                        # Check for recurrence (if this category has been breached before)
                        previous_breaches = [b for b in self.breach_history 
                                           if b['department'] == dept and b['category'] == category]
                        event['recurrence_count'] = len(previous_breaches)
                        event['is_recurring'] = len(previous_breaches) > 0
                        
                        overspending_events.append(event)
            
            return json.dumps({
                'total_events': len(overspending_events),
                'events': overspending_events,
                'detection_timestamp': datetime.now().isoformat()
            }, indent=2)
            
        except Exception as e:
            return f"Error detecting overspending events: {str(e)}"
    
    def score_breach_severity(self, breach_data: str) -> str:
        """Score breaches by overage percentage and recurrence"""
        try:
            if isinstance(breach_data, str):
                breaches = json.loads(breach_data)
            else:
                breaches = breach_data
            
            scored_breaches = []
            
            # Handle both single breach and multiple breaches
            breach_list = breaches if isinstance(breaches, list) else [breaches]
            
            for breach in breach_list:
                overage_percent = breach.get('overage_percent', breach.get('usage_percent', 100) - 100)
                recurrence_count = breach.get('recurrence_count', 0)
                
                # Calculate severity score
                base_score = min(overage_percent / 10, 10)  # 0-10 based on overage
                recurrence_multiplier = 1 + (recurrence_count * 0.2)  # 20% increase per recurrence
                final_score = base_score * recurrence_multiplier
                
                # Determine severity level
                if final_score >= 8:
                    severity = "Critical"
                elif final_score >= 5:
                    severity = "High"  
                elif final_score >= 3:
                    severity = "Medium"
                else:
                    severity = "Low"
                
                scored_breach = {
                    **breach,
                    'severity_score': round(final_score, 2),
                    'severity_level': severity,
                    'scoring_factors': {
                        'overage_percent': overage_percent,
                        'recurrence_count': recurrence_count,
                        'base_score': round(base_score, 2),
                        'recurrence_multiplier': round(recurrence_multiplier, 2)
                    }
                }
                
                scored_breaches.append(scored_breach)
            
            return json.dumps({
                'scored_breaches': scored_breaches,
                'scoring_completed': datetime.now().isoformat()
            }, indent=2)
            
        except Exception as e:
            return f"Error scoring breach severity: {str(e)}"
    
    def link_triggering_transactions(self, breach_data: str) -> str:
        """Link breaches to specific triggering transactions for traceability"""
        try:
            if isinstance(breach_data, str):
                breach_info = json.loads(breach_data)
            else:
                breach_info = breach_data
            
            # This would typically integrate with the expense tracker to get transaction details
            # For now, we'll create a mock linkage structure
            
            linked_breaches = []
            breaches = breach_info.get('scored_breaches', [breach_info])
            
            for breach in breaches:
                department = breach.get('department', '')
                category = breach.get('category', '')
                
                # Mock transaction linking (in real implementation, this would query actual transactions)
                triggering_transactions = [
                    {
                        'transaction_id': f"txn_{datetime.now().timestamp()}",
                        'amount': breach.get('spent', 0) * 0.3,  # Mock: assume last transaction was 30% of total
                        'timestamp': datetime.now().isoformat(),
                        'vendor': f"Vendor_{category}",
                        'description': f"Purchase that triggered {category} budget breach",
                        'is_triggering': True
                    }
                ]
                
                linked_breach = {
                    **breach,
                    'triggering_transactions': triggering_transactions,
                    'transaction_count': len(triggering_transactions),
                    'traceability_score': 'High',
                    'linked_timestamp': datetime.now().isoformat()
                }
                
                linked_breaches.append(linked_breach)
            
            return json.dumps({
                'linked_breaches': linked_breaches,
                'total_linked': len(linked_breaches),
                'linking_completed': datetime.now().isoformat()
            }, indent=2)
            
        except Exception as e:
            return f"Error linking triggering transactions: {str(e)}"
    
    def _calculate_severity(self, usage_percent: float) -> str:
        """Calculate severity based on usage percentage"""
        if usage_percent >= 150:
            return "Critical"
        elif usage_percent >= 125:
            return "High"
        elif usage_percent >= 110:
            return "Medium"
        else:
            return "Low"
    
    def get_detected_breaches(self):
        """Return detected breaches for other agents"""
        return self.detected_breaches