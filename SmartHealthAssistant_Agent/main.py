import streamlit as st
import os
from dotenv import load_dotenv
from src.agents import init_agents
from ui.layout import render_header, render_form, render_results, render_error

# === Streamlit UI ===
render_header()

load_dotenv()
default_api_key = os.getenv("GEMINI_API_KEY", "")
if not default_api_key:
    st.error("API key not found in environment. Please set GEMINI_API_KEY in your .env file.")

# === Session State ===
if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "final_plan" not in st.session_state:
    st.session_state.final_plan = ""

# === Health Form ===
weight, height, age, gender, dietary_preference, submit_btn = render_form()

# === Submit Handler ===
if submit_btn and default_api_key:
    try:
        user_proxy, bmi_agent, diet_agent, workout_agent, config_list = init_agents(default_api_key, dietary_preference, age, gender)
        from autogen import GroupChat, GroupChatManager
        groupchat = GroupChat(
            agents=[user_proxy, bmi_agent, diet_agent, workout_agent],
            messages=[],
            max_round=6,
            speaker_selection_method="round_robin"
        )
        manager = GroupChatManager(
            groupchat=groupchat,
            llm_config={"config_list": config_list, "cache_seed": None}
        )
        initial_message = f"""
        User Health Profile:
        - Basic Information:
          • Weight: {weight} kg
          • Height: {height} cm
          • Age: {age}
          • Gender: {gender}
        - Preferences:
          • Dietary Preference: {dietary_preference}

        Please proceed with the health assessment in this sequence:
        1. Calculate BMI using the 'calculate_bmi' function with weight={weight} and height={height}
        2. Analyze BMI and provide recommendations
        3. Create a meal plan based on BMI analysis and dietary preference
        4. Develop a workout schedule based on age, gender, and meal plan
        """
        with st.spinner("Generating your personalized health plan..."):
            user_proxy.initiate_chat(
                manager,
                message=initial_message,
                clear_history=True
            )
            st.session_state.conversation = []
            for msg in groupchat.messages:
                if msg['role'] != 'system' and msg['content'].strip():
                    st.session_state.conversation.append((msg['name'], msg['content']))
                    if msg['name'] == "Workout_Scheduler":
                        st.session_state.final_plan = msg['content']
        st.success("Health plan generated successfully! ✅")
    except Exception as e:
        render_error(str(e))

# === Results Display ===
render_results(st.session_state.conversation, st.session_state.final_plan)