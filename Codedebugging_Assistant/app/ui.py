import sys
import os
import streamlit as st

# Ensure the parent directory is in sys.path for package imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core import run_code_review

st.set_page_config(page_title="Python Code Reviewer", page_icon="🧑‍💻", layout="wide")

with st.sidebar:
    st.title("🧑‍💻 Python Code Reviewer")
    st.markdown("""
    **Instructions:**
    - Paste your Python code in the main area.
    - Click **Analyze & Fix** to get instant feedback and corrections.
    - Powered by AI (CrewAI, Gemini).
    """)
    st.markdown("---")
    st.info("No code is executed. Only static analysis is performed.")

st.markdown("""
# 🔍 Python Code Debugging Assistant
---
""")

code_input = st.text_area("Paste your Python code here:", height=300, key="code_input")
col1, col2 = st.columns([1, 2])
with col1:
    analyze_btn = st.button("Analyze & Fix", use_container_width=True)
with col2:
    st.write("")

if analyze_btn:
    if not code_input.strip():
        st.warning("Please enter Python code.")
    else:
        with st.spinner("Analyzing and fixing your code..."):
            analysis_result, correction_result = run_code_review(code_input)
        st.success("Analysis complete!")
        with st.expander("🧐 Analysis Result", expanded=True):
            st.write(analysis_result)
        with st.expander("🔧 Fixed Code", expanded=True):
            st.code(correction_result, language="python")

st.markdown("---")
st.markdown("<div style='text-align:center; color: #888; font-size: 0.95rem;'>Made with ❤️ using Streamlit & CrewAI</div>", unsafe_allow_html=True) 