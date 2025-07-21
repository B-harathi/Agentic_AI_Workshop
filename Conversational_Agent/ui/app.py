import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
from core.logic import generate_competitor_report

st.set_page_config(
    page_title="Retail Competitor Insights Dashboard",
    page_icon="🛍️",
    layout="wide"
)

# --- Modern UI Layout ---
# (Custom CSS removed to allow Streamlit theme to work)

col1, col2 = st.columns([1, 2])
with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/892/892458.png", width=120)
    st.markdown("""
    ## Welcome to Retail Insights
    Unlock actionable intelligence on clothing store competitors in your area. Configure your analysis and get a business-ready report instantly!
    """)
    st.info("All data is generated using advanced AI agents and the Gemini LLM.")

with st.sidebar:
    st.markdown("# ⚙️ Analysis Settings")
    with st.expander("Location & Scope", expanded=True):
        city_area = st.text_input("Target Area", "Koramangala, Bangalore", help="Specify the location for analysis.")
        num_competitors = st.select_slider("Competitor Count", options=list(range(3, 11)), value=5)
    with st.expander("Report Customization", expanded=True):
        detail_mode = st.selectbox("Report Depth", ["Brief", "Standard", "In-depth"], index=1)
        theme = st.radio("Theme", ["Light", "Dark", "Business"], index=2)
    st.markdown("---")
    st.success("Ready to analyze your market!")
    go_btn = st.button("🚀 Run Competitor Analysis", use_container_width=True)

with col2:
    if go_btn:
        st.info(f"**Analyzing competitors in:** {city_area}")
        st.info(f"**Number of competitors:** {num_competitors}")
        st.info(f"**Report style:** {detail_mode} | **Theme:** {theme}")
        with st.spinner("Gathering market intelligence..."):
            try:
                report, messages = generate_competitor_report(city_area, num_competitors, detail_mode)
                if report:
                    st.success("Report Ready!")
                    st.divider()
                    st.markdown(report)
                    st.download_button(
                        label="Download Markdown Report",
                        data=report,
                        file_name=f"retail_competition_{city_area.replace(' ', '_')}.md",
                        mime="text/markdown"
                    )
                else:
                    st.warning("No final report found. Displaying conversation log:")
                    for m in messages:
                        st.write(f"**{m['name']}:**")
                        st.markdown(m["content"])
                        st.divider()
            except Exception as err:
                st.error(f"Error: {err}")
                st.info("Check your API key and try again.") 