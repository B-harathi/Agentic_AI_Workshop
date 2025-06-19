from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, Tool
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()

# Tool for parsing expenses

def parse_expenses(raw_text: str):
    # For demo: parse CSV-like text to DataFrame
    try:
        df = pd.read_csv(pd.compat.StringIO(raw_text))
        return df.to_dict(orient='records')
    except Exception as e:
        return f"Parsing error: {e}"

parse_tool = Tool(
    name="ExpenseParser",
    func=parse_expenses,
    description="Parses raw expense data (CSV or text) into structured records."
)

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=os.getenv("GEMINI_API_KEY"))

parsing_agent = initialize_agent(
    tools=[parse_tool],
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True
)

def run_parsing_agent(raw_text):
    return parsing_agent.run(raw_text) 