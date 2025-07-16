import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List, Any
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from base_agent import BaseAgent
import config

class EscalationCommunicatorAgent(BaseAgent):
    def __init__(self):
        self.sent_notifications = []
        self.email_config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'email_user': config.EMAIL_USER,
            'email_pass': config.EMAIL_PASS
        }
        super().__init__()
    
    def create_tools(self):
        return [
            Tool(
                name="create_breach_notification",
                description="Create contextual breach notification with summary and recommendations",
                func=self.create_breach_notification
            ),
            Tool(
                name="send_email_alert",
                description="Send email notification to finance team with breach details",
                func=self.send_email_alert
            ),
            Tool(
                name="generate_escalation_summary",
                description="Generate executive summary for stakeholder escalation",
                func=self.generate_escalation_summary
            ),
            Tool(
                name="create_action_request",
                description="Create action request with specific next steps for stakeholders",
                func=self.create_action_request
            )
        ]
    
    def create_prompt(self):
        return PromptTemplate(
            input_variables=["input", "agent_scratchpad", "tools", "tool_names"],
            template="""
            You are an Escalation Communicator Agent that manages urgent budget breach communications.
            
            Your mission: Communicate urgent budget breaches to stakeholders with contextual summaries.
            
            Tasks:
            1. Create clear breach notifications with context and recommendations
            2. Send email alerts to finance team with priority tags
            3. Generate executive summaries for stakeholder escalation
            4. Include justification, triggering events, and recommended options
            5. Support multiple finance roles with appropriate priority levels
            
            Available tools: {tool_names}
            Tools: {tools}
            
            Input: {input}
            
            Thought: I need to communicate this breach situation effectively to the right stakeholders.
            {agent_scratchpad}
            """
        )
    
    def create_breach_notification(self, breach_and_recommendations: str) -> str:
        """Create contextual breach notification with summary and recommendations"""
        try:
            if isinstance(breach_and_recommendations, str):
                data = json.loads(breach_and_recommendations)
            else:
                data = breach_and_recommendations
            
            # Extract breach information
            breaches = data.get('breaches', [])
            recommendations = data.get('recommendations', [])
            
            notifications = []
            
            for breach in breaches:
                notification = {
                    'notification_id': f"notif_{datetime.now().timestamp()}_{breach.get('department', 'unknown')}",
                    'urgency_level': self._determine_notification_urgency(breach),
                    'breach_summary': {
                        'department': breach.get('department', 'Unknown'),
                        'category': breach.get('category', 'Unknown'),
                        'overage_amount': breach.get('overage', 0),
                        'severity': breach.get('severity_level', breach.get('severity', 'Medium')),
                        'detection_time': breach.get('detected_at', datetime.now().isoformat())
                    },
                    'contextual_details': {
                        'budget_limit': breach.get('limit', 0),
                        'total_spent': breach.get('spent', 0),
                        'percentage_over': breach.get('overage_percent', 0),
                        'triggering_transactions': breach.get('triggering_transactions', []),
                        'is_recurring': breach.get('is_recurring', False)
                    },
                    'business_impact': {
                        'financial_impact': f"${breach.get('overage', 0):.2f} over budget",
                        'operational_risk': self._assess_operational_risk(breach),
                        'compliance_concern': breach.get('overage_percent', 0) > 25
                    },
                    'recommended_actions': self._extract_relevant_recommendations(breach, recommendations),
                    'escalation_required': breach.get('severity_level', breach.get('severity', 'Medium')) in ['High', 'Critical'],
                    'stakeholders': self._identify_stakeholders(breach)
                }
                
                notifications.append(notification)
            
            return json.dumps({
                'notifications': notifications,
                'total_notifications': len(notifications),
                'created_at': datetime.now().isoformat()
            }, indent=2)
            
        except Exception as e:
            return f"Error creating breach notification: {str(e)}"
    
    def send_email_alert(self, notification_data: str) -> str:
        """Send email notification to finance team with breach details"""
        try:
            if isinstance(notification_data, str):
                notifications = json.loads(notification_data)
            else:
                notifications = notification_data
            
            sent_emails = []
            
            for notification in notifications.get('notifications', []):
                # Prepare email content
                subject = self._create_email_subject(notification)
                body = self._create_email_body(notification)
                recipients = self._get_email_recipients(notification)
                
                # Send email
                email_result = self._send_email(subject, body, recipients)
                
                sent_email = {
                    'notification_id': notification['notification_id'],
                    'subject': subject,
                    'recipients': recipients,
                    'sent_at': datetime.now().isoformat(),
                    'status': email_result['status'],
                    'urgency': notification['urgency_level']
                }
                
                sent_emails.append(sent_email)
                self.sent_notifications.append(sent_email)
            
            return json.dumps({
                'email_alerts_sent': len(sent_emails),
                'sent_details': sent_emails,
                'send_timestamp': datetime.now().isoformat()
            }, indent=2)
            
        except Exception as e:
            return f"Error sending email alerts: {str(e)}"
    
    def generate_escalation_summary(self, notification_data: str) -> str:
        """Generate executive summary for stakeholder escalation"""
        try:
            if isinstance(notification_data, str):
                notifications = json.loads(notification_data)
            else:
                notifications = notification_data
            
            # Aggregate data for executive summary
            total_overage = 0
            critical_breaches = 0
            departments_affected = set()
            
            breach_details = []
            
            for notification in notifications.get('notifications', []):
                breach_summary = notification['breach_summary']
                overage = breach_summary['overage_amount']
                severity = breach_summary['severity']
                
                total_overage += overage
                departments_affected.add(breach_summary['department'])
                
                if severity in ['Critical', 'High']:
                    critical_breaches += 1
                
                breach_details.append({
                    'department': breach_summary['department'],
                    'category': breach_summary['category'],
                    'overage': overage,
                    'severity': severity,
                    'requires_immediate_action': notification['escalation_required']
                })
            
            executive_summary = {
                'summary_id': f"exec_summary_{datetime.now().timestamp()}",
                'executive_overview': {
                    'total_budget_breach': total_overage,
                    'departments_affected': len(departments_affected),
                    'critical_breaches': critical_breaches,
                    'summary_date': datetime.now().isoformat()
                },
                'key_findings': [
                    f"${total_overage:.2f} in total budget overages detected",
                    f"{len(departments_affected)} departments affected: {', '.join(departments_affected)}",
                    f"{critical_breaches} critical breaches requiring immediate attention"
                ],
                'immediate_actions_required': [
                    breach for breach in breach_details 
                    if breach['requires_immediate_action']
                ],
                'financial_recommendations': [
                    "Implement immediate spending freeze on affected categories",
                    "Initiate budget reallocation from surplus categories",
                    "Schedule emergency budget review meeting within 48 hours"
                ],
                'next_steps': [
                    "Department managers to provide corrective action plans",
                    "Finance team to identify reallocation opportunities",
                    "Weekly monitoring until budgets are back on track"
                ],
                'escalation_timeline': "Immediate action required within 24 hours"
            }
            
            return json.dumps(executive_summary, indent=2)
            
        except Exception as e:
            return f"Error generating escalation summary: {str(e)}"
    
    def create_action_request(self, escalation_data: str) -> str:
        """Create action request with specific next steps for stakeholders"""
        try:
            if isinstance(escalation_data, str):
                escalation = json.loads(escalation_data)
            else:
                escalation = escalation_data
            
            action_requests = []
            
            # Create specific action requests for different roles
            roles = ['Department Manager', 'Finance Director', 'Procurement Team', 'Executive Team']
            
            for role in roles:
                action_request = {
                    'request_id': f"action_req_{datetime.now().timestamp()}_{role.replace(' ', '_')}",
                    'target_role': role,
                    'priority': 'High' if escalation.get('executive_overview', {}).get('critical_breaches', 0) > 0 else 'Medium',
                    'due_date': self._calculate_due_date(role),
                    'specific_actions': self._get_role_specific_actions(role, escalation),
                    'deliverables': self._get_role_deliverables(role),
                    'context': {
                        'total_overage': escalation.get('executive_overview', {}).get('total_budget_breach', 0),
                        'affected_departments': escalation.get('executive_overview', {}).get('departments_affected', 0),
                        'critical_breaches': escalation.get('executive_overview', {}).get('critical_breaches', 0)
                    },
                    'escalation_path': 'Executive Team' if role != 'Executive Team' else 'Board of Directors'
                }
                
                action_requests.append(action_request)
            
            return json.dumps({
                'action_requests': action_requests,
                'total_requests': len(action_requests),
                'created_at': datetime.now().isoformat(),
                'coordination_required': True
            }, indent=2)
            
        except Exception as e:
            return f"Error creating action requests: {str(e)}"
    
    def _send_email(self, subject: str, body: str, recipients: List[str]) -> Dict:
        """Send email using SMTP"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_config['email_user']
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['email_user'], self.email_config['email_pass'])
            text = msg.as_string()
            server.sendmail(self.email_config['email_user'], recipients, text)
            server.quit()
            
            return {'status': 'sent', 'message': 'Email sent successfully'}
            
        except Exception as e:
            return {'status': 'failed', 'message': f'Failed to send email: {str(e)}'}
    
    def _create_email_subject(self, notification: Dict) -> str:
        """Create email subject line"""
        urgency = notification['urgency_level']
        department = notification['breach_summary']['department']
        severity = notification['breach_summary']['severity']
        
        urgency_prefix = "🚨 CRITICAL" if urgency == 'Critical' else "⚠️ URGENT" if urgency == 'High' else "📊"
        
        return f"{urgency_prefix} Budget Breach Alert - {department} Department ({severity} Severity)"
    
    def _create_email_body(self, notification: Dict) -> str:
        """Create email body content"""
        breach = notification['breach_summary']
        details = notification['contextual_details']
        impact = notification['business_impact']
        actions = notification['recommended_actions']
        
        body = f"""
        <html>
        <body>
            <h2>Budget Breach Notification</h2>
            
            <h3>Breach Summary</h3>
            <ul>
                <li><strong>Department:</strong> {breach['department']}</li>
                <li><strong>Category:</strong> {breach['category']}</li>
                <li><strong>Overage Amount:</strong> ${breach['overage_amount']:.2f}</li>
                <li><strong>Severity:</strong> {breach['severity']}</li>
                <li><strong>Detection Time:</strong> {breach['detection_time']}</li>
            </ul>
            
            <h3>Financial Details</h3>
            <ul>
                <li><strong>Budget Limit:</strong> ${details['budget_limit']:.2f}</li>
                <li><strong>Total Spent:</strong> ${details['total_spent']:.2f}</li>
                <li><strong>Percentage Over:</strong> {details['percentage_over']:.1f}%</li>
                <li><strong>Recurring Issue:</strong> {'Yes' if details['is_recurring'] else 'No'}</li>
            </ul>
            
            <h3>Business Impact</h3>
            <ul>
                <li><strong>Financial Impact:</strong> {impact['financial_impact']}</li>
                <li><strong>Operational Risk:</strong> {impact['operational_risk']}</li>
                <li><strong>Compliance Concern:</strong> {'Yes' if impact['compliance_concern'] else 'No'}</li>
            </ul>
            
            <h3>Recommended Actions</h3>
            <ol>
        """
        
        for action in actions:
            body += f"<li>{action}</li>"
            
        body += """
            </ol>
            
            <h3>Next Steps</h3>
            <p>Please review the breach details and implement the recommended corrective actions immediately. 
            Contact the finance team if you need assistance with budget reallocation or vendor renegotiation.</p>
            
            <p><strong>This is an automated alert from the Smart Budget Enforcer system.</strong></p>
        </body>
        </html>
        """
        
        return body
    
    def _determine_notification_urgency(self, breach: Dict) -> str:
        """Determine notification urgency level"""
        severity = breach.get('severity_level', breach.get('severity', 'Medium'))
        overage_percent = breach.get('overage_percent', 0)
        is_recurring = breach.get('is_recurring', False)
        
        if severity == 'Critical' or overage_percent > 50 or is_recurring:
            return 'Critical'
        elif severity == 'High' or overage_percent > 25:
            return 'High'
        else:
            return 'Medium'
    
    def _assess_operational_risk(self, breach: Dict) -> str:
        """Assess operational risk level"""
        category = breach.get('category', '').lower()
        overage_percent = breach.get('overage_percent', 0)
        
        if 'critical' in category or 'infrastructure' in category or overage_percent > 50:
            return 'High'
        elif overage_percent > 25:
            return 'Medium'
        else:
            return 'Low'
    
    def _extract_relevant_recommendations(self, breach: Dict, recommendations: List) -> List[str]:
        """Extract relevant recommendations for the breach"""
        # Default recommendations if none provided
        default_actions = [
            f"Implement immediate spending freeze for {breach.get('category', 'this category')}",
            f"Review and approve all {breach.get('category', 'category')} purchases over $100",
            "Identify budget reallocation opportunities from other categories",
            "Schedule vendor renegotiation meeting within 5 business days"
        ]
        
        if not recommendations:
            return default_actions
        
        # Extract specific recommendations (this would be more sophisticated in practice)
        return default_actions[:2]  # Return top 2 for brevity
    
    def _identify_stakeholders(self, breach: Dict) -> List[str]:
        """Identify relevant stakeholders for the breach"""
        stakeholders = ['Finance Team']
        
        department = breach.get('department', '')
        severity = breach.get('severity_level', breach.get('severity', 'Medium'))
        
        if department:
            stakeholders.append(f"{department} Manager")
        
        if severity in ['High', 'Critical']:
            stakeholders.extend(['Finance Director', 'Executive Team'])
        
        return stakeholders
    
    def _get_email_recipients(self, notification: Dict) -> List[str]:
        """Get email recipients based on stakeholders"""
        # In a real implementation, this would map to actual email addresses
        return ['finance@company.com', 'manager@company.com']
    
    def _calculate_due_date(self, role: str) -> str:
        """Calculate due date based on role"""
        from datetime import timedelta
        
        if role == 'Department Manager':
            due_date = datetime.now() + timedelta(hours=24)
        elif role in ['Finance Director', 'Procurement Team']:
            due_date = datetime.now() + timedelta(hours=48)
        else:
            due_date = datetime.now() + timedelta(hours=72)
        
        return due_date.isoformat()
    
    def _get_role_specific_actions(self, role: str, escalation: Dict) -> List[str]:
        """Get specific actions for each role"""
        actions = {
            'Department Manager': [
                'Provide immediate spending freeze implementation plan',
                'Identify non-essential expenses that can be postponed',
                'Submit corrective action plan within 24 hours'
            ],
            'Finance Director': [
                'Approve emergency budget reallocation requests',
                'Review department budget allocations for Q4',
                'Coordinate with department managers on corrective actions'
            ],
            'Procurement Team': [
                'Initiate vendor renegotiation processes',
                'Review contract terms for cost reduction opportunities',
                'Provide alternative vendor recommendations'
            ],
            'Executive Team': [
                'Review overall budget strategy and controls',
                'Approve major budget reallocations',
                'Communicate with board if necessary'
            ]
        }
        
        return actions.get(role, ['Review breach details and provide feedback'])
    
    def _get_role_deliverables(self, role: str) -> List[str]:
        """Get expected deliverables for each role"""
        deliverables = {
            'Department Manager': [
                'Corrective action plan document',
                'List of postponed/cancelled expenses',
                'Updated spending forecast'
            ],
            'Finance Director': [
                'Budget reallocation approval decisions',
                'Updated budget monitoring procedures',
                'Risk assessment report'
            ],
            'Procurement Team': [
                'Vendor renegotiation timeline',
                'Cost reduction proposals',
                'Alternative vendor analysis'
            ],
            'Executive Team': [
                'Strategic budget review summary',
                'Governance improvement recommendations',
                'Communication plan for stakeholders'
            ]
        }
        
        return deliverables.get(role, ['Status update report'])
    
    def get_notification_history(self):
        """Return notification history for other agents"""
        return self.sent_notifications