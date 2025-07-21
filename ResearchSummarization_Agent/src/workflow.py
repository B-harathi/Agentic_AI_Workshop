from langgraph.graph import StateGraph
from langchain_core.runnables import RunnableLambda
from src.agents import router_agent, web_agent, rag_agent, llm_agent, summarizer_agent

def run_langgraph(user_query, retriever, llm, search):
    workflow = StateGraph(dict)
    workflow.set_entry_point("router")

    workflow.add_node("router", RunnableLambda(lambda state: router_agent(state, llm)))
    workflow.add_node("web", RunnableLambda(lambda state: web_agent(state, search)))
    workflow.add_node("rag", RunnableLambda(lambda state: rag_agent(state, llm)))
    workflow.add_node("llm", RunnableLambda(lambda state: llm_agent(state, llm)))
    workflow.add_node("summarizer", RunnableLambda(lambda state: summarizer_agent(state, llm)))

    def router_logic(state): return state["route"]
    workflow.add_conditional_edges("router", router_logic, {
        "web": "web",
        "rag": "rag",
        "llm": "llm"
    })

    for node in ["web", "rag", "llm"]:
        workflow.add_edge(node, "summarizer")

    workflow.set_finish_point("summarizer")
    app = workflow.compile()
    return app.invoke({"query": user_query, "retriever": retriever})["final"] 