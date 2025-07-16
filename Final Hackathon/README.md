# Final Hackathon - AI Budget Management System

An intelligent budget management system powered by AI agents that automatically processes budget files, tracks expenses, detects policy breaches, and provides real-time recommendations for corrective actions.

## 🏗️ Project Structure

```
Final Hackathon/
├── agents/      # Python AI agents (FastAPI)
├── backend/     # Node.js/Express backend API
└── frontend/    # React Material-UI frontend
```

## 🧩 Key Libraries & Technologies

### Frontend (`frontend/package.json`)
- **React** (^18.2.0) - Core UI framework
- **Material-UI** (@mui/material, @mui/icons-material, @mui/lab, @mui/x-charts) - UI components
- **Recharts** - Data visualization
- **Socket.io-client** - Real-time updates
- **Axios** - API requests
- **React Router DOM** - Client-side routing
- **Date-fns** - Date utilities

### Backend (`backend/package.json`)
- **Express** - Web server framework
- **Socket.io** - WebSocket server for real-time communication
- **Axios** - HTTP requests to AI agents
- **Multer** - File upload handling
- **Cors, Helmet, Morgan** - Security & logging middleware
- **dotenv** - Environment variable management
- **Jest, Nodemon** - Testing & development tools

### Python Agents (`agents/requirements.txt`)
- **FastAPI** - API server framework
- **Uvicorn** - ASGI server
- **LangChain** - AI agent framework
- **faiss-cpu** - Vector search for RAG (Retrieval-Augmented Generation)
- **pandas, numpy** - Data processing
- **PyPDF2, openpyxl, python-docx** - File parsing capabilities
- **pydantic, requests, python-dotenv** - Validation, HTTP requests, environment management

## 🛠️ Main Features & Components

### Frontend Components
- **Dashboard** - Visualizes budget status, breaches, and recommendations with real-time data
- **BudgetUpload** - File upload interface with processing status indicators
- **ExpenseList** - Expense tracking and viewing interface
- **BreachAlerts** - Active budget breach notifications and alerts
- **Recommendations** - AI-generated corrective action suggestions
- **WebSocket Integration** - Real-time updates across all dashboard components

### Backend 
- **WebSocket Server** - Real-time dashboard updates
- **File Upload Handling** - Processes and forwards files to AI agents
- **Agent Orchestration** - Coordinates communication with Python AI agents

### Python AI Agents
- **Budget Policy Loader** - Extracts and structures budget rules from uploaded documents
- **Expense Tracker** - Analyzes and categorizes expenses against policies
- **Breach Detector** - Identifies policy violations and spending threshold breaches
- **Correction Recommender** - Generates intelligent corrective actions and budget reallocation suggestions
- **Escalation Communicator** - Automated notifications and critical issue escalation

## ⚙️ Installation & Setup

### Prerequisites
- Node.js (v14 or higher)
- Python (v3.8 or higher)
- npm or yarn package manager

### Installation Steps

1. **Install Python Agent Dependencies**
   ```bash
   cd agents
   pip install -r requirements.txt
   ```

2. **Install Backend Dependencies**
   ```bash
   cd backend
   npm install
   ```

3. **Install Frontend Dependencies**
   ```bash
   cd frontend
   npm install
   ```

## 🚀 Running the Application

### Start the AI Agents Server
```bash
cd agents
python agent_orchestrator.py
```

### Start the Backend API Server
```bash
cd backend
npm start
```

### Start the Frontend Development Server
```bash
cd frontend
npm start
```

### Access the Application
Open your browser and navigate to: `http://localhost:3000`

## 📂 Example Workflow

1. **Upload Budget File** - Upload budget documents (Excel, PDF, DOCX, CSV) through the dashboard interface
2. **AI Processing** - AI agents extract and structure budget rules using RAG and NLP techniques
3. **Expense Tracking** - Track expenses in real-time with automatic policy comparison
4. **Breach Detection** - Receive instant alerts for policy violations and spending breaches
5. **AI Recommendations** - View intelligent suggestions for corrective actions and budget reallocation
6. **Automated Escalation** - Critical issues are automatically escalated to relevant stakeholders

## 📚 Technical Notes

### Architecture Highlights
- **Microservices Design** - Separate concerns across frontend, backend, and AI agents
- **Real-time Communication** - WebSocket integration for live dashboard updates
- **AI-Powered Intelligence** - Advanced NLP and RAG capabilities for document processing
- **Extensible Framework** - Easy to add new agents, endpoints, and features

### Development Considerations
- **Extensible Architecture** - Add new agents or API endpoints as business requirements evolve
- **Production Readiness** - For production deployment, consider adding:
  - Authentication and authorization systems
  - HTTPS encryption
  - Persistent vector storage solutions
  - Comprehensive error handling and logging
  - Database integration for data persistence
- **Customization** - Easily adaptable to different budget formats and business rules

## 🛡️ Security & Performance

- CORS protection enabled
- Helmet middleware for security headers
- File upload validation and sanitization
- Vector-based search optimization with FAISS
- Real-time data synchronization

## 🔗 Additional Resources

- **Documentation**: [View Project Documentation](https://drive.google.com/file/d/1plHZZwofup90ymIV_HGV4SVhoo2FmuGs/view?usp=sharing)
- **Demo Video**: [Watch Application Demo](https://drive.google.com/file/d/1bqjpPK07ntaH7Sr-av-911eT5cFdGnAD/view?usp=sharing)


## 🤝 Contributing

This project was developed as part of a hackathon. For questions or contributions, please refer to the documentation and demo video linked above.

---

*Built with ❤️ using React, Node.js, Python, and AI technologies*