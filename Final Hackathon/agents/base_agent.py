from abc import ABC, abstractmethod
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate
import config

class BaseAgent(ABC):
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=config.GEMINI_API_KEY,
            temperature=0.1
        )
        self.agent_executor = None
        self.setup_agent()
    
    @abstractmethod
    def create_tools(self):
        pass
    
    @abstractmethod
    def create_prompt(self):
        pass
    
    def setup_agent(self):
        tools = self.create_tools()
        prompt = self.create_prompt()
        agent = create_react_agent(self.llm, tools, prompt)
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3
        )
    
    def execute(self, input_data):
        try:
            result = self.agent_executor.invoke({"input": input_data})
            return {
                "success": True,
                "result": result["output"],
                "agent": self.__class__.__name__
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent": self.__class__.__name__
            }