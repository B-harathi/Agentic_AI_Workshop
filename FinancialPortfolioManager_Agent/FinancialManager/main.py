import streamlit as st
import json
import autogen
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
from typing import Dict, Any
import asyncio

import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')  
if not api_key:
    st.error("""
    ❌ **Google API Key Missing!**
    
    Please follow these steps to set up your API key:
    
    1. **Get a Google API Key:**
       - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
       - Create a new API key
    
    2. **Create a .env file:**
       - Create a file named `.env` in the same directory as this script
       - Add this line to the file: `GOOGLE_API_KEY=your_actual_api_key_here`
       - Replace `your_actual_api_key_here` with your real API key
    
    3. **Restart the application**
    
    **Example .env file content:**
    ```
    GOOGLE_API_KEY=AIzaSyC...your_actual_key_here
    ```
    """)
    st.stop()

config_list_gemini = [{
    "model": "gemini-1.5-flash",
    "api_key": api_key,
    "api_type": "google"
}]

# Custom CSS for modern UI
st.set_page_config(
    page_title="Financial Portfolio Manager",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    
    .form-container {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #e9ecef;
        margin: 1rem 0;
    }
    
    .section-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: bold;
        font-size: 1.1rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .report-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #e9ecef;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .status-indicator {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        margin: 0.5rem;
    }
    
    .status-processing {
        background: #ffc107;
        color: #000;
    }
    
    .status-success {
        background: #28a745;
        color: white;
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.8;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>💼 AI Financial Portfolio Manager</h1>
    <p style="font-size: 1.2rem; opacity: 0.9;">Intelligent Investment Analysis with Multi-Agent Collaboration</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for quick info
with st.sidebar:
    st.markdown("### 📊 Portfolio Overview")
    st.markdown("""
    This AI-powered tool analyzes your financial profile and provides personalized investment recommendations using advanced multi-agent collaboration.
    
    **Features:**
    - 🤖 Multi-Agent Analysis
    - 📈 Personalized Strategy
    - 💡 Smart Recommendations
    - 🔄 StateFlow Management
    """)
    
    st.markdown("### 🎯 How it Works")
    st.markdown("""
    1. **Input Your Data** - Financial profile & current portfolio
    2. **AI Analysis** - Multi-agent collaboration analyzes your situation
    3. **Strategy Selection** - Growth vs Value investment approach
    4. **Recommendations** - Personalized investment suggestions
    5. **Comprehensive Report** - Detailed financial roadmap
    """)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-header"><h3>👤 Personal Financial Profile</h3></div>', unsafe_allow_html=True)
    
    with st.form("financial_form"):
        # Personal Information
        col1_1, col1_2 = st.columns(2)
        with col1_1:
            salary = st.text_input("💰 Annual Salary (₹)", placeholder="1200000", help="Enter your annual salary in rupees")
            age = st.number_input("🎂 Your Age", min_value=18, max_value=100, step=1, help="Your current age")
        with col1_2:
            expenses = st.text_input("💸 Annual Expenses (₹)", placeholder="500000", help="Your annual expenses in rupees")
            risk = st.selectbox("⚖️ Risk Tolerance", ["Conservative", "Moderate", "Aggressive"], help="Your investment risk preference")
        
        goals = st.text_area("🎯 Financial Goals", placeholder="Retirement in 20 years, buying a home in 5 years", help="Describe your financial goals and timeline")
        
        # Portfolio Details
        st.markdown('<div class="section-header"><h3>💼 Current Portfolio Details</h3></div>', unsafe_allow_html=True)
        
        col2_1, col2_2 = st.columns(2)
        with col2_1:
            mutual_funds = st.text_area("📈 Mutual Funds", placeholder="Axis Bluechip - Equity - ₹2L\nHDFC Mid-Cap - ₹1.5L", help="List your mutual fund investments")
            stocks = st.text_area("📊 Stocks", placeholder="Infosys - 10 shares - ₹1500\nTCS - 5 shares - ₹2000", help="List your stock holdings")
        with col2_2:
            real_estate = st.text_area("🏠 Real Estate", placeholder="Residential Apartment - Mumbai - ₹10L\nCommercial Property - Delhi - ₹15L", help="List your real estate investments")
            fixed_deposit = st.text_input("🏦 Fixed Deposit (₹)", placeholder="500000", help="Total fixed deposit amount")
        
        # Submit button
        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("🚀 Generate AI Financial Report")
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Quick Metrics")
    st.markdown("""
    <div class="metric-label">Portfolio Status</div>
    <div class="metric-value">Ready for Analysis</div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown("### 🤖 AI Agents")
    st.markdown("""
    - 📊 Portfolio Analyst
    - 📈 Growth Strategist  
    - 💎 Value Strategist
    - 💼 Financial Advisor
    """)
    st.markdown("</div>", unsafe_allow_html=True)

# Imports for new structure
from app.ui import run_ui

if __name__ == "__main__":
    run_ui()