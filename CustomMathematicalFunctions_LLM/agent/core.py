from langgraph.graph import StateGraph, END
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import TypedDict, List, Optional, Annotated, Union
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
import operator

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY"), temperature=0)

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    user_input: str
    agent_outcome: Optional[Union[BaseMessage, List[tuple]]]
    intermediate_steps: List

@tool
def plus(a: float, b: float) -> float:
    """Add two numbers together. Use for addition problems."""
    return a + b

@tool
def sub(a: float, b: float) -> float:
    """Subtract b from a. Use for subtraction problems."""
    return a - b

@tool
def mul(a: float, b: float) -> float:
    """Multiply two numbers. Use for multiplication problems."""
    return a * b

@tool
def divide(a: float, b: float) -> float:
    """Divide a by b. Use for division problems. Returns error if dividing by zero."""
    if b == 0:
        return "Error: Cannot divide by zero"
    return a / b

tools = [plus, sub, mul, divide]

system_prompt = """You are a helpful assistant that can:
- Answer general knowledge questions
- Perform math calculations when requested

For math operations, always use the appropriate tools.
For all other questions, respond using your knowledge.

Format all responses clearly and helpfully."""

agent = create_tool_calling_agent(
    llm=llm,
    tools=tools,
    prompt=ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ]),
)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

def agent_node(state: AgentState):
    result = agent_executor.invoke({
        "input": state["user_input"],
        "chat_history": state["messages"]
    })
    return {
        "messages": [AIMessage(content=result["output"])],
        "agent_outcome": result["output"]
    }

workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.set_entry_point("agent")
workflow.add_edge("agent", END)
app = workflow.compile()

def run_agent(query: str, chat_history: List[BaseMessage] = []):
    try:
        inputs = {
            "messages": chat_history,
            "user_input": query
        }
        response = app.invoke(inputs)
        return response["agent_outcome"]
    except Exception as e:
        return f"Error: {str(e)}" 