import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.tools import DuckDuckGoSearchRun
from src.workflow import run_langgraph

load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3, google_api_key=GOOGLE_API_KEY)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
search = DuckDuckGoSearchRun()

# --- Custom CSS for modern look ---
st.markdown(
    """
    <style>
    .main {
        background-color: #f7f9fa;
        border-radius: 18px;
        padding: 2rem 2rem 1rem 2rem;
        box-shadow: 0 2px 16px rgba(0,0,0,0.07);
    }
    .stButton>button {
        background: linear-gradient(90deg, #4f8cff 0%, #6edb8f 100%);
        color: white;
        border-radius: 8px;
        font-weight: bold;
        font-size: 1.1rem;
        padding: 0.5rem 2rem;
        margin-top: 1rem;
    }
    .stTextInput>div>div>input {
        border-radius: 8px;
        border: 1.5px solid #4f8cff;
        font-size: 1.1rem;
        padding: 0.5rem 1rem;
    }
    .stAlert {
        border-radius: 8px;
    }
    footer {
        visibility: hidden;
    }
    .custom-footer {
        position: fixed;
        left: 0; right: 0; bottom: 0;
        width: 100%;
        background: #e9ecef;
        color: #333;
        text-align: center;
        padding: 0.5rem 0;
        font-size: 0.95rem;
        z-index: 100;
        border-top: 1px solid #d1d5db;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Sidebar ---
st.sidebar.title("ℹ️ About")
st.sidebar.markdown(
    """
    **Multi-Agent RAG System**
    
    - Combines Web Search, RAG, and LLM
    - Powered by LangGraph, Gemini, and FAISS
    - Upload your own documents to the `my_docs` folder
    """
)

st.sidebar.markdown("---")

# Document status in sidebar
if os.path.exists("my_docs"):
    doc_files = [f for f in os.listdir("my_docs") if f.lower().endswith((".pdf", ".txt", ".docx"))]
    st.sidebar.success(f"📂 {len(doc_files)} document(s) found in 'my_docs'.")
else:
    st.sidebar.info("No 'my_docs' folder found. Using fallback knowledge base.")

st.sidebar.markdown("---")
st.sidebar.markdown("Created by [Your Name] · Powered by Streamlit & LangChain")

# --- Main UI ---
st.markdown("""
<div class="main">
    <h1 style="text-align:center; font-size:2.5rem; margin-bottom:0.2em;">🧠 Multi-Agent RAG System</h1>
    <p style="text-align:center; color:#4f8cff; font-size:1.2rem; margin-bottom:2em;">
        <b>LangGraph + Web + RAG + LLM</b> — Your fully agentic research assistant
    </p>
</div>
""", unsafe_allow_html=True)

# --- Columns for input/output ---
col1, col2 = st.columns([1,2])

with col1:
    st.markdown("#### 💬 Ask your question")
    query = st.text_input("", placeholder="e.g. What is LangGraph?", key="user_query")
    submit = st.button("Submit")

with col2:
    if submit:
        if not query.strip():
            st.warning("⚠️ Please enter a question.")
        else:
            with st.spinner("🤖 Thinking..."):
                try:
                    # You may need to define or import a retriever here
                    retriever = None  # TODO: Replace with actual retriever logic
                    answer = run_langgraph(query, retriever, llm, search)
                    st.success("✅ Done!")
                    st.subheader("📘 Answer:")
                    st.write(answer)
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    else:
        st.info("Enter a question and click Submit to get started.")

# --- Footer ---
st.markdown(
    """
    <div class="custom-footer">
        &copy; 2024 Multi-Agent RAG System &mdash; <a href="https://streamlit.io/" target="_blank">Streamlit</a> + <a href="https://python.langchain.com/" target="_blank">LangChain</a> + <a href="https://ai.google.dev/gemini-api/docs" target="_blank">Gemini</a>
    </div>
    """,
    unsafe_allow_html=True,
) 