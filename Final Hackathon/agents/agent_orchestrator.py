import json
import os
from datetime import datetime
from typing import Dict, Any, List
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import all agents
from budget_policy_loader import BudgetPolicyLoaderAgent
from expense_tracker import ExpenseTrackerAgent
from breach_detector import BreachDetectorAgent
from correction_recommender import CorrectionRecommenderAgent
from escalation_communicator import EscalationCommunicatorAgent
import config

# FastAPI app
app = FastAPI(title="Smart Budget Enforcer - AI Agents", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
budget_loader = BudgetPolicyLoaderAgent()
expense_tracker = ExpenseTrackerAgent()
breach_detector = BreachDetectorAgent()
correction_recommender = CorrectionRecommenderAgent()
escalation_communicator = EscalationCommunicatorAgent()

# Data models
class ExpenseData(BaseModel):
    amount: float
    department: str
    category: str
    vendor: str = "Unknown"
    description: str = "No description"

class ProcessFlowRequest(BaseModel):
    trigger_type: str  # "file_upload" or "expense_entry"
    data: Dict[str, Any]

# Global state storage
global_state = {
    "budget_data": {},
    "expense_tracking": {},
    "detected_breaches": [],
    "recommendations": [],
    "notifications": []
}

@app.get("/")
async def root():
    return {
        "message": "Smart Budget Enforcer AI Agents",
        "agents": [
            "Budget Policy Loader (RAG)",
            "Expense Tracker", 
            "Breach Detector",
            "Correction Recommender",
            "Escalation Communicator"
        ],
        "status": "Active"
    }

@app.get("/agents/status")
async def get_agents_status():
    return {
        "agents": {
            "budget_policy_loader": "Active",
            "expense_tracker": "Active", 
            "breach_detector": "Active",
            "correction_recommender": "Active",
            "escalation_communicator": "Active"
        },
        "global_state": {
            "budget_loaded": bool(global_state["budget_data"]),
            "expenses_tracked": len(global_state["expense_tracking"]),
            "breaches_detected": len(global_state["detected_breaches"]),
            "recommendations_generated": len(global_state["recommendations"]),
            "notifications_sent": len(global_state["notifications"])
        }
    }

@app.post("/upload-budget")
async def upload_budget_file(file: UploadFile = File(...)):
    try:
        # Save uploaded file
        os.makedirs(config.UPLOAD_PATH, exist_ok=True)
        file_path = f"{config.UPLOAD_PATH}/{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Step 1: Extract and structure budget
        extract_result = budget_loader.execute(f"extract_budget_from_file:{file_path}")
        structure_result = budget_loader.execute("structure_budget_rules:extracted_content")
        rag_result = budget_loader.execute("create_rag_vectorstore:extracted_content")
        global_state["budget_data"] = budget_loader.get_budget_data()

        # Step 2: Load budget thresholds into Expense Tracker
        if global_state["budget_data"]:
            expense_tracker.execute(f"load_budget_thresholds:{json.dumps(global_state['budget_data'])}")

        # Step 3: (Optional) Track initial expenses if present in the file
        # (Add logic here if your file contains expenses)

        # Step 4: Run expense tracking and breach detection
        if global_state["budget_data"]:
            expense_tracker.execute("calculate_budget_usage:all")
            global_state["expense_tracking"] = expense_tracker.get_current_usage_data()
            breach_detector.execute(f"analyze_expense_data:{json.dumps(global_state['expense_tracking'])}")
            global_state["detected_breaches"] = breach_detector.get_detected_breaches()

        # Step 5: Run recommendations
        if global_state["detected_breaches"]:
            correction_recommender.execute(f"analyze_breach_context:{json.dumps(global_state['detected_breaches'])}")
            global_state["recommendations"] = correction_recommender.get_all_recommendations()

        # Step 6: Run escalation
        if global_state["detected_breaches"]:
            escalation_data = {
                "breaches": global_state["detected_breaches"],
                "recommendations": global_state["recommendations"]
            }
            escalation_communicator.execute(f"create_breach_notification:{json.dumps(escalation_data)}")
            global_state["notifications"] = escalation_communicator.get_notification_history()

        return {
            "success": True,
            "message": "Budget file processed and full workflow executed.",
            "budget_data": global_state["budget_data"],
            "expense_tracking": global_state["expense_tracking"],
            "detected_breaches": global_state["detected_breaches"],
            "recommendations": global_state["recommendations"],
            "notifications": global_state["notifications"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing budget file: {str(e)}")

@app.post("/track-expense")
async def track_expense(expense: ExpenseData):
    """
    Step 2: Real-Time Expense Tracker Agent 
    → Monitors transactions and maps against budget usage
    """
    try:
        # Load budget thresholds first
        if global_state["budget_data"]:
            load_result = expense_tracker.execute(f"load_budget_thresholds:{json.dumps(global_state['budget_data'])}")
        
        # Track the new expense
        expense_json = json.dumps(expense.dict())
        track_result = expense_tracker.execute(f"track_new_expense:{expense_json}")
        
        # Calculate current usage
        usage_result = expense_tracker.execute("calculate_budget_usage:all")
        
        # Get real-time status
        status_result = expense_tracker.execute("get_real_time_status:all")
        
        # Store tracking data globally
        global_state["expense_tracking"] = expense_tracker.get_current_usage_data()
        
        return {
            "success": True,
            "message": "Expense tracked successfully",
            "expense": expense.dict(),
            "tracking_result": track_result,
            "usage_result": json.loads(usage_result["result"]) if usage_result["success"] else {},
            "status_result": json.loads(status_result["result"]) if status_result["success"] else {}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tracking expense: {str(e)}")

@app.post("/detect-breaches")
async def detect_breaches():
    """
    Step 3: Breach Detector Agent 
    → Detects overspending events and scores by severity
    """
    try:
        if not global_state["expense_tracking"]:
            raise HTTPException(status_code=400, detail="No expense tracking data available")
        
        # Analyze expense data for breaches
        tracking_data = json.dumps(global_state["expense_tracking"])
        analysis_result = breach_detector.execute(f"analyze_expense_data:{tracking_data}")
        
        # Get current expense status
        status_data = expense_tracker.execute("get_real_time_status:all")
        if status_data["success"]:
            # Detect overspending events
            overspend_result = breach_detector.execute(f"detect_overspending_events:{status_data['result']}")
            
            # Score breach severity
            if analysis_result["success"]:
                breach_data = json.loads(analysis_result["result"])
                if breach_data.get("breach_details"):
                    severity_result = breach_detector.execute(f"score_breach_severity:{json.dumps(breach_data['breach_details'])}")
                    
                    # Link triggering transactions
                    if severity_result["success"]:
                        link_result = breach_detector.execute(f"link_triggering_transactions:{severity_result['result']}")
        
        # Store detected breaches globally
        global_state["detected_breaches"] = breach_detector.get_detected_breaches()
        
        return {
            "success": True,
            "message": "Breach detection completed",
            "analysis_result": json.loads(analysis_result["result"]) if analysis_result["success"] else {},
            "overspend_result": json.loads(overspend_result["result"]) if 'overspend_result' in locals() and overspend_result["success"] else {},
            "severity_result": json.loads(severity_result["result"]) if 'severity_result' in locals() and severity_result["success"] else {},
            "link_result": json.loads(link_result["result"]) if 'link_result' in locals() and link_result["success"] else {}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting breaches: {str(e)}")

@app.post("/generate-recommendations")
async def generate_recommendations():
    """
    Step 4: Correction Recommender Agent 
    → Suggests reallocations, spending pauses, or vendor renegotiation
    """
    try:
        if not global_state["detected_breaches"]:
            raise HTTPException(status_code=400, detail="No breaches detected to generate recommendations for")
        
        breach_data = json.dumps(global_state["detected_breaches"])
        
        # Analyze breach context
        context_result = correction_recommender.execute(f"analyze_breach_context:{breach_data}")
        
        if context_result["success"]:
            context_data = context_result["result"]
            
            # Generate reallocation strategies
            realloc_result = correction_recommender.execute(f"generate_reallocation_strategies:{context_data}")
            
            # Suggest spending pauses
            pause_result = correction_recommender.execute(f"suggest_spending_pauses:{context_data}")
            
            # Recommend vendor renegotiation
            negotiation_result = correction_recommender.execute(f"recommend_vendor_renegotiation:{context_data}")
        
        # Store recommendations globally
        global_state["recommendations"] = correction_recommender.get_all_recommendations()
        
        return {
            "success": True,
            "message": "Recommendations generated successfully",
            "context_analysis": json.loads(context_result["result"]) if context_result["success"] else {},
            "reallocation_strategies": json.loads(realloc_result["result"]) if 'realloc_result' in locals() and realloc_result["success"] else {},
            "spending_pauses": json.loads(pause_result["result"]) if 'pause_result' in locals() and pause_result["success"] else {},
            "vendor_negotiations": json.loads(negotiation_result["result"]) if 'negotiation_result' in locals() and negotiation_result["success"] else {}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@app.post("/send-escalation")
async def send_escalation():
    """
    Step 5: Escalation Communicator Agent 
    → Sends breach notification to finance team with contextual breakdown
    """
    try:
        if not global_state["detected_breaches"]:
            raise HTTPException(status_code=400, detail="No breaches to escalate")
        
        # Prepare data for escalation
        escalation_data = {
            "breaches": global_state["detected_breaches"],
            "recommendations": global_state["recommendations"]
        }
        
        # Create breach notification
        notification_result = escalation_communicator.execute(f"create_breach_notification:{json.dumps(escalation_data)}")
        
        if notification_result["success"]:
            notification_data = notification_result["result"]
            
            # Send email alerts
            email_result = escalation_communicator.execute(f"send_email_alert:{notification_data}")
            
            # Generate escalation summary
            summary_result = escalation_communicator.execute(f"generate_escalation_summary:{notification_data}")
            
            # Create action requests
            action_result = escalation_communicator.execute(f"create_action_request:{summary_result['result'] if summary_result['success'] else notification_data}")
        
        # Store notifications globally
        global_state["notifications"] = escalation_communicator.get_notification_history()
        
        return {
            "success": True,
            "message": "Escalation communication completed",
            "notifications": json.loads(notification_result["result"]) if notification_result["success"] else {},
            "email_alerts": json.loads(email_result["result"]) if 'email_result' in locals() and email_result["success"] else {},
            "executive_summary": json.loads(summary_result["result"]) if 'summary_result' in locals() and summary_result["success"] else {},
            "action_requests": json.loads(action_result["result"]) if 'action_result' in locals() and action_result["success"] else {}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending escalation: {str(e)}")

@app.post("/process-complete-flow")
async def process_complete_flow(request: ProcessFlowRequest):
    """
    Complete workflow: Upload Budget → Track Expense → Detect Breaches → Generate Recommendations → Send Escalation
    """
    try:
        results = {
            "workflow_started": datetime.now().isoformat(),
            "steps_completed": [],
            "final_dashboard_data": {}
        }
        
        if request.trigger_type == "expense_entry":
            # Simulate the complete flow with a new expense
            expense_data = ExpenseData(**request.data)
            
            # Step 1: Track expense (assumes budget is already loaded)
            track_result = await track_expense(expense_data)
            results["steps_completed"].append("expense_tracked")
            
            # Step 2: Detect breaches
            breach_result = await detect_breaches()
            results["steps_completed"].append("breaches_detected")
            
            # Step 3: Generate recommendations (if breaches found)
            if global_state["detected_breaches"]:
                rec_result = await generate_recommendations()
                results["steps_completed"].append("recommendations_generated")
                
                # Step 4: Send escalation
                escalation_result = await send_escalation()
                results["steps_completed"].append("escalation_sent")
        
        # Prepare final dashboard data
        results["final_dashboard_data"] = {
            "budget_status": global_state["expense_tracking"],
            "active_breaches": global_state["detected_breaches"],
            "recommended_actions": global_state["recommendations"],
            "notifications_sent": global_state["notifications"],
            "overall_status": "Critical" if global_state["detected_breaches"] else "Safe",
            "last_updated": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "message": "Complete workflow processed successfully",
            "workflow_results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing complete flow: {str(e)}")

@app.get("/dashboard-data")
async def get_dashboard_data():
    """
    Get current dashboard data for UI display
    """
    return {
        "success": True,
        "dashboard_data": {
            "budget_loaded": bool(global_state["budget_data"]),
            "budget_data": global_state["budget_data"],
            "expense_tracking": global_state["expense_tracking"],
            "detected_breaches": global_state["detected_breaches"],
            "recommendations": global_state["recommendations"],
            "notifications": global_state["notifications"],
            "summary": {
                "total_departments": len(global_state["budget_data"].get("departments", {})),
                "total_breaches": len(global_state["detected_breaches"]),
                "total_recommendations": len(global_state["recommendations"]),
                "last_updated": datetime.now().isoformat()
            }
        }
    }

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs(config.UPLOAD_PATH, exist_ok=True)
    os.makedirs(config.VECTOR_STORE_PATH, exist_ok=True)
    
    print("🤖 Starting Smart Budget Enforcer AI Agents...")
    print("📋 Available Agents:")
    print("   1. Budget Policy Loader (RAG)")
    print("   2. Real-Time Expense Tracker") 
    print("   3. Breach Detector")
    print("   4. Correction Recommender")
    print("   5. Escalation Communicator")
    print(f"🌐 API Server running on http://localhost:{config.AGENT_PORT}")
    
    uvicorn.run(app, host="0.0.0.0", port=config.AGENT_PORT)