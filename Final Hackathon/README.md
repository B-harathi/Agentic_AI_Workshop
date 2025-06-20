Final Hackathon/
  agents/      # Python AI agents (FastAPI)
  backend/     # Node.js/Express backend API
  frontend/    # React Material-UI frontend


🧩 Key Libraries Used
Frontend (frontend/package.json)
React (^18.2.0)
Material-UI (@mui/material, @mui/icons-material, @mui/lab, @mui/x-charts)
Recharts (data visualization)
Socket.io-client (real-time updates)
Axios (API requests)
React Router DOM (routing)
Date-fns (date utilities)
Backend (backend/package.json)
Express (web server)
Socket.io (WebSocket server)
Axios (HTTP requests to agents)
Multer (file uploads)
Cors, Helmet, Morgan (security & logging)
dotenv (environment variables)
Jest, Nodemon (testing & dev tools)
Python Agents (agents/requirements.txt)
FastAPI (API server)
Uvicorn (ASGI server)
LangChain (AI agent framework)
faiss-cpu (vector search for RAG)
pandas, numpy (data processing)
PyPDF2, openpyxl, python-docx (file parsing)
pydantic, requests, python-dotenv (validation, HTTP, env)

🛠️ Main Features & Components
Frontend
Dashboard: Visualizes budget status, breaches, and recommendations.
BudgetUpload: Uploads budget files and shows processing status.
ExpenseList: Track and view expenses.
BreachAlerts: Shows active budget breaches and alerts.
Recommendations: Displays AI-generated corrective actions.
WebSocket Integration: Real-time updates for all dashboard data.
Backend
API Endpoints: 
/api/upload-budget, 
/api/track-expense, 
/api/detect-breaches, 
/api/generate-recommendations, 
/api/send-escalation, /api/dashboard
WebSocket Server: Pushes live dashboard updates to frontend.
File Upload Handling: Receives and forwards budget files to Python agents.
Agent Orchestration: Communicates with Python agents for all AI tasks.

Python Agents
Budget Policy Loader: Extracts and structures budget rules from uploaded files.
Expense Tracker: Tracks and analyzes expenses.
Breach Detector: Detects policy violations and spending breaches.
Correction Recommender: Suggests corrective actions and reallocation.
Escalation Communicator: Sends notifications and escalates critical issues.

⚙️ How to Run
Install dependencies for each part:
cd agents && pip install -r requirements.txt
cd backend && npm install
cd frontend && npm install

Start the Python agents:
cd agents
python agent_orchestrator.py

Start the backend:
cd backend
npm start

Start the frontend:
cd frontend
npm start

Open the app:
Go to http://localhost:3000 in your browser.

📂 Example Workflow
Upload a budget file (Excel, PDF, DOCX, CSV) via the dashboard.
AI agents extract and structure budget rules using RAG and NLP.
Track expenses and see them compared to policy in real time.
Get instant alerts for any breaches or policy violations.
View AI recommendations for corrective actions and reallocation.
Escalate critical issues automatically to stakeholders.

📚 Further Notes
Extensible: Add new agents or endpoints as needed.
Production-Ready: For production, add authentication, HTTPS, persistent vector storage, and robust error handling.
Customizable: Easily adapt to different budget formats and business rules.

Document link : - https://docs.google.com/document/d/1bmDeO8BIS23Kqm-7NaFgUkoCHzs-6B8O1HZMNORB7z8/edit?usp=sharing
Video Link -