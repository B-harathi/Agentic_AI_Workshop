import google.generativeai as genai
from autogen import AssistantAgent, UserProxyAgent
from .utils import calculate_bmi
import os

# === Gemini Config Wrapper ===
def get_gemini_config(api_key: str, model: str = "gemini-1.5-flash"):
    return [{
        "model": model,
        "api_key": api_key,
        "api_type": "google",
        "base_url": "https://generativelanguage.googleapis.com/v1beta"
    }]

# === Agent Initialization ===
def init_agents(api_key, dietary_preference, age, gender):
    genai.configure(api_key=api_key)
    config_list = get_gemini_config(api_key)

    bmi_agent = AssistantAgent(
        name="BMI_Agent",
        llm_config={"config_list": config_list, "cache_seed": None},
        system_message="""You are a BMI specialist. Analyze BMI results and:
        1. Calculate BMI from weight (kg) and height (cm)
        2. Categorize (underweight, normal, overweight, obese)
        3. Provide health recommendations
        Always include the exact BMI value in your response."""
    )

    diet_agent = AssistantAgent(
        name="Diet_Planner",
        llm_config={"config_list": config_list, "cache_seed": None},
        system_message=f"""You are a nutritionist. Create meal plans based on:
        1. BMI analysis from BMI_Agent
        2. Dietary preference ({dietary_preference})
        Include breakfast, lunch, dinner, and snacks with portions."""
    )

    workout_agent = AssistantAgent(
        name="Workout_Scheduler",
        llm_config={"config_list": config_list, "cache_seed": None},
        system_message=f"""You are a fitness trainer. Create weekly workout plans based on:
        1. Age ({age}) and gender ({gender})
        2. BMI recommendations
        3. Meal plan from Diet_Planner
        Include cardio, strength training with duration and intensity."""
    )

    user_proxy = UserProxyAgent(
        name="User_Proxy",
        human_input_mode="NEVER",
        code_execution_config=False,
        llm_config={"config_list": config_list, "cache_seed": None},
        system_message="Collects and shares user data with other agents."
    )

    user_proxy.register_function(function_map={"calculate_bmi": calculate_bmi})

    return user_proxy, bmi_agent, diet_agent, workout_agent, config_list 