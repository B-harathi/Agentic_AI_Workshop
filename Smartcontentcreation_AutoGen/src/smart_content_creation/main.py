import streamlit as st
import time
import google.generativeai as genai
from autogen import AssistantAgent, UserProxyAgent
from langchain_google_genai import ChatGoogleGenerativeAI
import copy
import os

# Configure Gemini API
api_key = "AIzaSyDG-0xIaprzdT70VTf-LnMt62_s-F8SJqA"
genai.configure(api_key=api_key)

# System messages
CREATOR_SYSTEM_MESSAGE = """
You are a Content Creator Agent specializing in Generative AI. Your role is to:
1. Draft clear, concise, and technically accurate content
2. Revise content based on constructive feedback
3. Structure output in markdown format
4. Focus exclusively on content creation (no commentary)
"""

CRITIC_SYSTEM_MESSAGE = """
You are a Content Critic Agent evaluating Generative AI content. Your role is to:
1. Analyze technical accuracy and language clarity
2. Provide specific, constructive feedback
3. Identify both strengths and areas for improvement
4. Maintain professional, objective tone
"""

# Custom wrapper for deepcopy compatibility
class GeminiAgent:
    def __init__(self, model, system_message):
        self.model = model
        self.system_message = system_message
    
    def generate(self, prompt):
        full_prompt = self.system_message + "\n\n" + prompt
        try:
            response = self.model.invoke(full_prompt)
            return response.content
        except Exception as e:
            return f"Error: {str(e)}"
    
    def __deepcopy__(self, memo):
        # Create a new instance with same configuration
        return GeminiAgent(
            model=ChatGoogleGenerativeAI(model=self.model.model, google_api_key=api_key),
            system_message=self.system_message
        )

# Initialize Gemini models through LangChain
creator_model = GeminiAgent(
    model=ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key),
    system_message=CREATOR_SYSTEM_MESSAGE
)

critic_model = GeminiAgent(
    model=ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key),
    system_message=CRITIC_SYSTEM_MESSAGE
)

# Streamlit UI
st.set_page_config(page_title="Agentic AI Content Refinement", page_icon="🤖", layout="wide")

# Modern Header
st.markdown("""
<div style='background-color:#22223b;padding:32px 0 16px 0;border-radius:16px;margin-bottom:24px;'>
    <h1 style='color:#f2e9e4;text-align:center;margin-bottom:0;'>🤖 Agentic AI Content Refinement</h1>
    <p style='color:#c9ada7;text-align:center;font-size:1.2rem;margin-top:8px;'>Simulated reflection-based conversation between Content Creator and Content Critic agents</p>
</div>
""", unsafe_allow_html=True)

# Input Card
with st.container():
    st.markdown("""
    <div style='background-color:#f2e9e4;padding:24px 32px 16px 32px;border-radius:14px;margin-bottom:24px;'>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([3, 2, 2])
    with col1:
        topic = st.text_input("Discussion Topic", "Agentic AI")
    with col2:
        turns = st.slider("Conversation Turns", 3, 5, 3)
    with col3:
        generate_btn = st.button("Start Simulation", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

if generate_btn:
    # Create AutoGen agents with proper configuration
    creator = AssistantAgent(
        name="Creator",
        system_message=CREATOR_SYSTEM_MESSAGE,
        llm_config={
            "config_list": [
                {
                    "model": "gemini-1.5-flash",
                    "api_key": api_key,
                    "base_url": "https://generativelanguage.googleapis.com/v1beta/models/"
                }
            ],
            "timeout": 120
        },
        human_input_mode="NEVER",
        is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
    )
    
    critic = AssistantAgent(
        name="Critic",
        system_message=CRITIC_SYSTEM_MESSAGE,
        llm_config={
            "config_list": [
                {
                    "model": "gemini-1.5-flash",
                    "api_key": api_key,
                    "base_url": "https://generativelanguage.googleapis.com/v1beta/models/"
                }
            ],
            "timeout": 120
        },
        human_input_mode="NEVER",
        is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
    )
    
    # User proxy agent with Docker disabled
    user_proxy = UserProxyAgent(
        name="User_Proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=0,
        code_execution_config=False,
    )
    
    # Initialize conversation state
    conversation_history = []
    creator_output = ""
    critic_feedback = ""
    reflections = []

    st.markdown("<div style='margin-bottom:16px'></div>", unsafe_allow_html=True)
    progress = st.progress(0, text="Starting conversation...")
    
    # Start conversation
    for turn in range(1, turns + 1):
        progress.progress(turn/turns, text=f"Turn {turn} of {turns}")
        if turn % 2 == 1:
            # Content Creator Turn
            st.markdown(f"""
            <div style='background:linear-gradient(90deg,#e3f2fd 60%,#bcdffb 100%);padding:20px 24px 12px 24px;border-radius:14px;margin-bottom:12px;'>
                <b>📝 Content Creator (Turn {turn})</b>
                <div style='margin-top:8px;font-size:0.95rem;'>
            """, unsafe_allow_html=True)
            if turn == 1:
                prompt = f"Draft comprehensive content about {topic} in markdown format covering:\n- Key concepts\n- Technical foundations\n- Real-world applications\n- Future implications"
            else:
                prompt = f"Revise this content based on the critic's feedback:\n\n{critic_feedback}\n\nCurrent content:\n{creator_output}\n\nProvide improved markdown content:"
            st.markdown("**Prompt:**", unsafe_allow_html=True)
            st.code(prompt, language="markdown")
            creator_output = creator_model.generate(prompt)
            st.markdown("**Generated Content:**", unsafe_allow_html=True)
            st.markdown(creator_output)
            conversation_history.append((f"Creator (Turn {turn})", creator_output))
            # Reflection after revision (not on first turn)
            if turn > 1:
                reflection_prompt = f"Summarize in 1-2 sentences how you improved the content based on the critic's feedback."
                reflection = creator_model.generate(reflection_prompt + "\n\nFeedback received:\n" + critic_feedback + "\n\nRevised content:\n" + creator_output)
                st.info(f"**Creator's Reflection:** {reflection}")
                reflections.append((f"Creator Reflection (Turn {turn})", reflection))
            st.markdown("</div></div>", unsafe_allow_html=True)
        else:
            # Content Critic Turn
            st.markdown(f"""
            <div style='background:linear-gradient(90deg,#fff3e0 60%,#ffe0b2 100%);padding:20px 24px 12px 24px;border-radius:14px;margin-bottom:12px;'>
                <b>🧐 Content Critic (Turn {turn})</b>
                <div style='margin-top:8px;font-size:0.95rem;'>
            """, unsafe_allow_html=True)
            prompt = f"Evaluate this content on:\n1. Technical accuracy\n2. Clarity of explanations\n3. Depth of coverage\n4. Improvement suggestions\n\nContent:\n{creator_output}"
            st.markdown("**Prompt:**", unsafe_allow_html=True)
            st.code(prompt, language="markdown")
            critic_feedback = critic_model.generate(prompt)
            st.markdown("**Critical Feedback:**", unsafe_allow_html=True)
            st.write(critic_feedback)
            conversation_history.append((f"Critic (Turn {turn})", critic_feedback))
            # Critic reflection: did the creator address previous feedback?
            if turn > 2:
                critic_reflection_prompt = f"Did the creator address your previous feedback? Summarize in 1-2 sentences."
                critic_reflection = critic_model.generate(critic_reflection_prompt + "\n\nPrevious feedback:\n" + conversation_history[-3][1] + "\n\nCurrent content:\n" + creator_output)
                st.info(f"**Critic's Reflection:** {critic_reflection}")
                reflections.append((f"Critic Reflection (Turn {turn})", critic_reflection))
            st.markdown("</div></div>", unsafe_allow_html=True)
        time.sleep(1)

    progress.empty()
    st.markdown("<div style='margin:24px 0'></div>", unsafe_allow_html=True)
    st.markdown("<hr style='border:1px solid #c9ada7;margin:32px 0;'>", unsafe_allow_html=True)
    # Unique Result Section
    st.markdown("""
    <div style='background:linear-gradient(90deg,#f7cac9 60%,#92a8d1 100%);padding:36px 36px 28px 36px;border-radius:20px;margin-bottom:32px;box-shadow:0 4px 24px rgba(146,168,209,0.15);border:2px solid #b56576;'>
        <h2 style='color:#22223b;text-align:center;margin-bottom:18px;'>🎉 Final Refined Content</h2>
        <div style='margin-top:12px;font-size:1.15rem;color:#22223b;'>
    """, unsafe_allow_html=True)
    st.markdown(creator_output)
    st.markdown("""
        </div>
        <div style='text-align:center;margin-top:18px;'>
            <button onclick="navigator.clipboard.writeText(document.getElementById('final-content').innerText)" style='background:#b56576;color:#fff;padding:10px 24px;border:none;border-radius:8px;font-size:1rem;cursor:pointer;'>Copy to Clipboard</button>
        </div>
    </div>
    <script>
    // Add an id to the content for copying
    var contentDiv = window.parent.document.querySelector('section.main div[data-testid="stMarkdownContainer"] div[style*="linear-gradient"] > div');
    if(contentDiv) contentDiv.id = 'final-content';
    </script>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border:1px solid #c9ada7;margin:32px 0;'>", unsafe_allow_html=True)
    st.subheader("🗨️ Full Conversation Trace")
    for i, (role, content) in enumerate(conversation_history, 1):
        with st.expander(f"{role}"):
            st.write(content)
    if reflections:
        st.markdown("<hr style='border:1px solid #c9ada7;margin:32px 0;'>", unsafe_allow_html=True)
        st.subheader("🔎 Agent Reflections")
        for i, (role, reflection) in enumerate(reflections, 1):
            with st.expander(f"{role}"):
                st.write(reflection)