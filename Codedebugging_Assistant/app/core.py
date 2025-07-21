import os
import ast
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai_tools import CodeInterpreterTool

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Custom Python Analyzer (No ONNX)
def analyze_python_code(code: str) -> str:
    """Static analysis without executing code."""
    try:
        tree = ast.parse(code)
        issues = []
        if any(isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'print' 
               for node in ast.walk(tree)):
            issues.append("⚠️ Found `print()` - Use logging in production.")
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                issues.append("⚠️ Found bare `except:` - Specify exception types.")
        if issues:
            return "Found issues:\n" + "\n".join(issues)
        return "✅ No syntax errors found. Code looks good!"
    except SyntaxError as e:
        return f"❌ Syntax Error: {e.msg} (Line {e.lineno})"

llm = LLM(
    api_key=os.getenv("GEMINI_API_KEY"),
    model="gemini/gemini-2.5-flash"
)

code_analyzer = Agent(
    role="Python Static Analyzer",
    goal="Find issues in Python code WITHOUT executing it",
    backstory="Expert in static code analysis using AST parsing.",
    llm=llm,
    verbose=True,
    tools=[CodeInterpreterTool()]
)

code_corrector = Agent(
    role="Python Code Fixer",
    goal="Fix issues while keeping original functionality",
    backstory="Specializes in clean, PEP 8 compliant fixes.",
    llm=llm,
    verbose=True
)

manager = Agent(
    role="Code Review Manager",
    goal="Ensure smooth analysis & correction",
    backstory="Coordinates the review process.",
    llm=llm,
    verbose=True
)

def run_code_review(code_input):
    analysis_task = Task(
        description=f"Analyze this code:\n```python\n{code_input}\n```",
        agent=code_analyzer,
        expected_output="List of static analysis issues."
    )
    correction_task = Task(
        description="Fix all issues found.",
        agent=code_corrector,
        expected_output="Corrected Python code with explanations.",
        context=[analysis_task]
    )
    crew = Crew(
        agents=[code_analyzer, code_corrector, manager],
        tasks=[analysis_task, correction_task],
        verbose=True,
        process=Process.sequential,
        planning=True
    )
    results = crew.kickoff()
    if isinstance(results, (list, tuple)) and len(results) == 2:
        analysis_result, correction_result = results
    elif isinstance(results, dict):
        analysis_result = results.get('analysis', '')
        correction_result = results.get('correction', '')
    else:
        analysis_result = "(Could not extract analysis result)"
        correction_result = results
    return analysis_result, correction_result 