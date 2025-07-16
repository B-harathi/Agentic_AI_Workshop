import json
from datetime import datetime
from typing import Dict, List, Any
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from base_agent import BaseAgent

class CorrectionRecommenderAgent(BaseAgent):
    def __init__(self):
        self.recommendations = []
        self.action_history = []
        super().__init__()
    
    def create_tools(self):
        return [
            Tool(
                name="analyze_breach_context",
                description="Analyze breach context and historical patterns for recommendation generation",
                func=self.analyze_breach_context
            ),
            Tool(
                name="generate_reallocation_strategies",
                description="Generate budget reallocation strategies from underused categories",
                func=self.generate_reallocation_strategies
            ),
            Tool(
                name="suggest_spending_pauses",
                description="Suggest strategic spending pauses for specific vendors or categories",
                func=self.suggest_spending_pauses
            ),
            Tool(
                name="recommend_vendor_renegotiation",
                description="Recommend vendor renegotiation strategies based on spending patterns",
                func=self.recommend_vendor_renegotiation
            )
        ]
    
    def create_prompt(self):
        return PromptTemplate(
            input_variables=["input", "agent_scratchpad", "tools", "tool_names"],
            template="""
            You are a Correction Recommender Agent that suggests strategic budget correction actions.
            
            Your mission: Suggest corrective strategies to regain control over breached budgets.
            
            Tasks:
            1. Analyze breach details and category history
            2. Generate actionable recommendations (reallocations, spending pauses, vendor renegotiation)
            3. Pull strategy from historical company budget responses
            4. Align suggestions with ongoing financial goals
            5. Provide at least two actionable suggestions per breach
            
            Available tools: {tool_names}
            Tools: {tools}
            
            Input: {input}
            
            Thought: I need to analyze the breach situation and generate practical corrective recommendations.
            {agent_scratchpad}
            """
        )
    
    def analyze_breach_context(self, breach_data: str) -> str:
        """Analyze breach context and historical patterns"""
        try:
            if isinstance(breach_data, str):
                breaches = json.loads(breach_data)
            else:
                breaches = breach_data
            
            context_analysis = []
            
            # Handle both single breach and breach list
            breach_list = breaches.get('linked_breaches', [breaches]) if 'linked_breaches' in breaches else [breaches]
            
            for breach in breach_list:
                department = breach.get('department', '')
                category = breach.get('category', '')
                overage = breach.get('overage', 0)
                severity = breach.get('severity_level', breach.get('severity', 'Medium'))
                
                context = {
                    'breach_id': breach.get('id', f"breach_{department}_{category}"),
                    'department': department,
                    'category': category,
                    'financial_impact': {
                        'overage_amount': overage,
                        'percentage_over': breach.get('overage_percent', 0),
                        'severity_level': severity
                    },
                    'pattern_analysis': {
                        'is_recurring': breach.get('is_recurring', False),
                        'recurrence_count': breach.get('recurrence_count', 0),
                        'trend': 'Increasing' if breach.get('recurrence_count', 0) > 1 else 'First Time'
                    },
                    'urgency_level': self._determine_urgency(severity, breach.get('recurrence_count', 0)),
                    'recommendation_focus': self._determine_focus_area(category, severity)
                }
                
                context_analysis.append(context)
            
            return json.dumps({
                'context_analysis': context_analysis,
                'analysis_timestamp': datetime.now().isoformat(),
                'total_breaches_analyzed': len(context_analysis)
            }, indent=2)
            
        except Exception as e:
            return f"Error analyzing breach context: {str(e)}"
    
    def generate_reallocation_strategies(self, context_data: str) -> str:
        """Generate budget reallocation strategies from underused categories"""
        try:
            if isinstance(context_data, str):
                context = json.loads(context_data)
            else:
                context = context_data
            
            reallocation_strategies = []
            
            contexts = context.get('context_analysis', [context])
            
            for ctx in contexts:
                department = ctx.get('department', '')
                category = ctx.get('category', '')
                overage = ctx['financial_impact']['overage_amount']
                
                strategy = {
                    'strategy_id': f"realloc_{datetime.now().timestamp()}_{department}_{category}",
                    'type': 'Budget_Reallocation',
                    'target_breach': {
                        'department': department,
                        'category': category,
                        'required_amount': overage
                    },
                    'reallocation_options': [
                        {
                            'source_category': f"{department}_Contingency",
                            'available_amount': overage * 1.2,  # Mock: assume 20% buffer available
                            'transfer_amount': overage,
                            'impact': 'Low',
                            'approval_required': 'Manager',
                            'timeline': '1-2 days'
                        },
                        {
                            'source_category': f"Other_Department_Surplus",
                            'available_amount': overage * 0.8,
                            'transfer_amount': overage * 0.8,
                            'impact': 'Medium',
                            'approval_required': 'Director',
                            'timeline': '3-5 days'
                        }
                    ],
                    'recommended_action': f"Transfer ${overage:.2f} from {department} contingency fund",
                    'priority': 'High' if ctx['urgency_level'] == 'Critical' else 'Medium'
                }
                
                reallocation_strategies.append(strategy)
            
            return json.dumps({
                'reallocation_strategies': reallocation_strategies,
                'total_strategies': len(reallocation_strategies),
                'generated_at': datetime.now().isoformat()
            }, indent=2)
            
        except Exception as e:
            return f"Error generating reallocation strategies: {str(e)}"
    
    def suggest_spending_pauses(self, context_data: str) -> str:
        """Suggest strategic spending pauses for specific vendors or categories"""
        try:
            if isinstance(context_data, str):
                context = json.loads(context_data)
            else:
                context = context_data
            
            pause_suggestions = []
            
            contexts = context.get('context_analysis', [context])
            
            for ctx in contexts:
                department = ctx.get('department', '')
                category = ctx.get('category', '')
                severity = ctx['financial_impact']['severity_level']
                
                suggestion = {
                    'suggestion_id': f"pause_{datetime.now().timestamp()}_{department}_{category}",
                    'type': 'Spending_Pause',
                    'target': {
                        'department': department,
                        'category': category,
                        'severity': severity
                    },
                    'pause_recommendations': []
                }
                
                # Different pause strategies based on severity
                if severity in ['Critical', 'High']:
                    suggestion['pause_recommendations'].extend([
                        {
                            'action': 'Immediate freeze on all non-essential spending',
                            'scope': f'All {category} purchases over $500',
                            'duration': '30 days',
                            'exceptions': 'Emergency purchases only',
                            'approval_level': 'Director approval required',
                            'expected_savings': '60-80% reduction'
                        },
                        {
                            'action': 'Vendor payment terms extension',
                            'scope': f'All {category} vendors',
                            'duration': '45 days',
                            'details': 'Negotiate extended payment terms to improve cash flow',
                            'expected_impact': '15-20% budget relief'
                        }
                    ])
                
                if severity in ['Medium', 'High']:
                    suggestion['pause_recommendations'].append({
                        'action': 'Selective vendor pause',
                        'scope': f'Top 3 {category} vendors by spend',
                        'duration': '14 days',
                        'details': 'Pause orders from highest-cost vendors while maintaining essential services',
                        'expected_savings': '30-40% reduction'
                    })
                
                pause_suggestions.append(suggestion)
            
            return json.dumps({
                'pause_suggestions': pause_suggestions,
                'total_suggestions': len(pause_suggestions),
                'suggested_at': datetime.now().isoformat()
            }, indent=2)
            
        except Exception as e:
            return f"Error suggesting spending pauses: {str(e)}"
    
    def recommend_vendor_renegotiation(self, context_data: str) -> str:
        """Recommend vendor renegotiation strategies based on spending patterns"""
        try:
            if isinstance(context_data, str):
                context = json.loads(context_data)
            else:
                context = context_data
            
            renegotiation_recommendations = []
            
            contexts = context.get('context_analysis', [context])
            
            for ctx in contexts:
                department = ctx.get('department', '')
                category = ctx.get('category', '')
                overage = ctx['financial_impact']['overage_amount']
                
                recommendation = {
                    'recommendation_id': f"nego_{datetime.now().timestamp()}_{department}_{category}",
                    'type': 'Vendor_Renegotiation',
                    'target_category': category,
                    'department': department,
                    'financial_goal': f"Reduce {category} costs by ${overage:.2f} monthly",
                    'negotiation_strategies': [
                        {
                            'strategy': 'Volume discount renegotiation',
                            'approach': f'Leverage current {category} spending volume for better rates',
                            'target_savings': f'{overage * 0.15:.2f}',
                            'timeline': '2-3 weeks',
                            'success_probability': '70%',
                            'negotiation_points': [
                                'Annual spending commitment',
                                'Multi-year contract terms',
                                'Payment terms optimization'
                            ]
                        },
                        {
                            'strategy': 'Service scope adjustment',
                            'approach': f'Reduce {category} service levels or features',
                            'target_savings': f'{overage * 0.25:.2f}',
                            'timeline': '1-2 weeks',
                            'success_probability': '85%',
                            'negotiation_points': [
                                'Remove premium features',
                                'Reduce service frequency',
                                'Minimize customizations'
                            ]
                        },
                        {
                            'strategy': 'Competitive bidding',
                            'approach': f'Request quotes from alternative {category} vendors',
                            'target_savings': f'{overage * 0.30:.2f}',
                            'timeline': '3-4 weeks',
                            'success_probability': '60%',
                            'negotiation_points': [
                                'Market rate comparison',
                                'Switching cost analysis',
                                'Trial period negotiation'
                            ]
                        }
                    ],
                    'recommended_priority': self._prioritize_negotiation(ctx['urgency_level']),
                    'escalation_path': ['Department Manager', 'Procurement Team', 'Director']
                }
                
                renegotiation_recommendations.append(recommendation)
            
            return json.dumps({
                'renegotiation_recommendations': renegotiation_recommendations,
                'total_recommendations': len(renegotiation_recommendations),
                'recommended_at': datetime.now().isoformat()
            }, indent=2)
            
        except Exception as e:
            return f"Error recommending vendor renegotiation: {str(e)}"
    
    def _determine_urgency(self, severity: str, recurrence_count: int) -> str:
        """Determine urgency level based on severity and recurrence"""
        if severity == 'Critical' or recurrence_count > 2:
            return 'Critical'
        elif severity == 'High' or recurrence_count > 1:
            return 'High'
        elif severity == 'Medium':
            return 'Medium'
        else:
            return 'Low'
    
    def _determine_focus_area(self, category: str, severity: str) -> str:
        """Determine the focus area for recommendations"""
        if severity in ['Critical', 'High']:
            return 'Immediate_Cost_Reduction'
        else:
            return 'Process_Optimization'
    
    def _prioritize_negotiation(self, urgency: str) -> str:
        """Prioritize negotiation strategies based on urgency"""
        if urgency == 'Critical':
            return 'Immediate - Start within 24 hours'
        elif urgency == 'High':
            return 'High - Start within 3 days'
        else:
            return 'Medium - Start within 1 week'
    
    def get_all_recommendations(self):
        """Return all generated recommendations for other agents"""
        return self.recommendations