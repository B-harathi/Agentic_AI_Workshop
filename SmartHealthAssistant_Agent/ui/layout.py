import streamlit as st

def render_header():
    st.set_page_config(page_title="Smart Health Assistant", layout="wide")
    st.markdown("""
        <div style='display: flex; flex-direction: column; align-items: center; margin-bottom: 2rem;'>
            <h1 style='font-size: 2.2rem; margin-bottom: 0.2rem;'>🤖 Smart Health Assistant</h1>
            <span style='font-size: 1.1rem; opacity: 0.85;'>Your personalized AI-powered health, diet, and fitness planner</span>
        </div>
    """, unsafe_allow_html=True)

def render_form():
    st.markdown("""
    <div style='display: flex; justify-content: center; margin-bottom: 1.5rem;'>
        <div style='border-radius: 18px; box-shadow: 0 2px 12px rgba(44, 62, 80, 0.07); padding: 2.5rem 2.5rem 1.5rem 2.5rem; min-width: 350px; max-width: 480px; width: 100%; background: transparent;'>
    """, unsafe_allow_html=True)
    with st.form("health_form"):
        st.markdown("<h3 style='margin-bottom: 1.2rem;'>📝 Enter Your Health Details</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2, gap="large")
        with col1:
            weight = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=70.0, step=0.1, format="%.1f")
            height = st.number_input("Height (cm)", min_value=100, max_value=250, value=170)
            age = st.number_input("Age", min_value=18, max_value=100, value=30)
        with col2:
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            dietary_preference = st.selectbox("Dietary Preference", ["Veg", "Non-Veg", "Vegan"])
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            submit_btn = st.form_submit_button("Generate Health Plan")
    st.markdown("</div></div>", unsafe_allow_html=True)
    return weight, height, age, gender, dietary_preference, submit_btn

def render_results(conversation, final_plan):
    if conversation:
        st.markdown("---")
        st.markdown("### Health Plan Generation Process")
        for agent, message in conversation:
            with st.expander(f"{agent} says:"):
                st.markdown(message)
        st.markdown("---")
        st.markdown("## 🌟 Your Complete Health Plan")
        if final_plan:
            st.markdown(final_plan)
            st.download_button(
                label="⬇️ Download Health Plan",
                data=final_plan,
                file_name="personalized_health_plan.txt",
                mime="text/plain"
            )
        else:
            st.warning("Workout schedule not generated. Please try again.")
    else:
        st.markdown("---")
        st.info("""
        **Instructions:**
        1. Fill in your health details
        2. Click **Generate Health Plan**
        3. View your personalized recommendations
        """)

def render_error(message):
    st.markdown(f"<div style='color:#b94a48; background:#f8d7da; border-radius:8px; padding:0.8rem 1rem; margin-bottom:0.5rem;'><b>Error occurred:</b> {message}</div>", unsafe_allow_html=True)
    st.markdown("<div style='color:#555; background:#e2e3e5; border-radius:8px; padding:0.8rem 1rem;'><b>Please ensure:</b> 1) Valid API key in .env 2) Stable internet connection 3) Correct input values</div>", unsafe_allow_html=True) 