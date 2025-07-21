from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
import json
from app.state import state_flow
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

config_list_gemini = [{
    "model": "gemini-1.5-flash",
    "api_key": api_key,
    "api_type": "google"
}]

user_proxy = UserProxyAgent(
    name="UserProxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: "TERMINATE" in x.get("content", ""),
    code_execution_config=False
)

portfolio_analyst = AssistantAgent(
    name="PortfolioAnalyst",
    llm_config={"config_list": config_list_gemini},
    system_message="""
    You are a Portfolio Analysis Agent. Analyze the user's portfolio and determine investment strategy.
    Your task:
    1. Analyze the user's current portfolio, salary, age, expenses, and risk tolerance
    2. Determine if they should pursue Growth or Value investment strategy
    3. Provide a brief explanation for your recommendation
    Output ONLY in JSON format: {"strategy": "Growth" or "Value", "reason": "brief explanation"}
    After analysis, mention "ANALYSIS_COMPLETE" to trigger next agent.
    """
)

growth_strategist = AssistantAgent(
    name="GrowthStrategist",
    llm_config={"config_list": config_list_gemini},
    system_message="""
    You are a Growth Investment Agent. Suggest high-growth investments for maximizing portfolio growth.
    Your task:
    1. Analyze the user's profile and current portfolio
    2. Suggest high-growth investment options (mid-cap mutual funds, global ETFs, tech stocks, etc.)
    3. Provide rationale for each recommendation
    Output: {"recommendations": ["item1", "item2", ...], "rationale": "brief explanation"}
    After recommendations, mention "RECOMMENDATIONS_READY" to trigger next agent.
    """
)

value_strategist = AssistantAgent(
    name="ValueStrategist",
    llm_config={"config_list": config_list_gemini},
    system_message="""
    You are a Value Investment Agent. Suggest stable investments for long-term value.
    Your task:
    1. Analyze the user's profile and current portfolio
    2. Suggest stable, long-term investment options (bonds, blue-chip stocks, government schemes)
    3. Provide rationale for each recommendation
    Output: {"recommendations": ["item1", "item2", ...], "rationale": "brief explanation"}
    After recommendations, mention "RECOMMENDATIONS_READY" to trigger next agent.
    """
)

financial_advisor = AssistantAgent(
    name="FinancialAdvisor",
    llm_config={"config_list": config_list_gemini},
    system_message="""
    You are an Investment Advisor Agent. Compile a comprehensive financial report.
    Your task:
    1. Review all previous agent outputs
    2. Generate a detailed, personalized financial report including:
       - Portfolio Analysis Summary
       - Recommended Strategy
       - Specific Investment Recommendations
       - Implementation Plan
       - Risk Assessment
    3. Format the report in Markdown with clear sections
    Add "TERMINATE" at the end when the report is complete.
    """
)

def create_group_chat():
    groupchat = GroupChat(
        agents=[user_proxy, portfolio_analyst, growth_strategist, value_strategist, financial_advisor],
        messages=[],
        max_round=50
    )
    manager = GroupChatManager(
        groupchat=groupchat,
        llm_config={"config_list": config_list_gemini}
    )
    return manager

def extract_strategy(content):
    try:
        start = content.find('{')
        end = content.rfind('}') + 1
        if start != -1 and end != 0:
            json_str = content[start:end]
            data = json.loads(json_str)
            return data.get("strategy", "Growth")
    except:
        pass
    return "Growth"

def manage_investment_portfolio(age, salary, expenses, goals, risk, mutual_funds, stocks, real_estate, fixed_deposit):
    user_data = {
        "age": age,
        "salary": salary,
        "expenses": expenses,
        "goals": goals,
        "risk": risk,
        "mutual_funds": mutual_funds,
        "stocks": stocks,
        "real_estate": real_estate,
        "fixed_deposit": fixed_deposit
    }
    state_flow.set_user_data(user_data)
    initial_message = f"""
User Profile:
- Age: {age}
- Annual Salary: ₹{salary}
- Annual Expenses: ₹{expenses}
- Risk Tolerance: {risk}
- Financial Goals: {goals}

Current Portfolio:
- Mutual Funds: {mutual_funds or 'None'}
- Stocks: {stocks or 'None'}
- Real Estate: {real_estate or 'None'}
- Fixed Deposit: ₹{fixed_deposit or '0'}

Please analyze this portfolio and determine the investment strategy.
"""
    manager = create_group_chat()
    chat_result = user_proxy.initiate_chat(
        manager,
        message=initial_message,
        summary_method="last_msg",
        silent=True
    )
    final_message = chat_result.chat_history[-1]["content"]
    if "TERMINATE" in final_message:
        return final_message.split("TERMINATE")[0].strip()
    return final_message 