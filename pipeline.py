from typing import TypedDict
from langgraph.graph import StateGraph, END
from agents import build_search_agent, build_reader_agent, writer_chain, critic_chain
from rich import print
import re

class AgentState(TypedDict):
    topic: str
    search_results: str
    reader_results: str
    report: str
    feedback: str
    revision_count: int

def search_node(state: AgentState):
    print("\n" + "="*20 + " Search Agent " + "="*20)
    topic = state["topic"]
    search_agent = build_search_agent()
    search_results = search_agent.invoke(
        {"messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]}
    )
    result_text = search_results['messages'][-1].content
    print("Search Agent Results: " + result_text[:200] + "...")
    return {"search_results": result_text}

def reader_node(state: AgentState):
    print("\n" + "="*20 + " Reader Agent " + "="*20)
    topic = state["topic"]
    search_results = state["search_results"]
    reader_agent = build_reader_agent()
    reader_results = reader_agent.invoke(
        {"messages":[("user", f"Based on the following search result about '{topic}', pick the most relevant URLs (you can pick multiple!) and use the scrape_web_pages tool to scrape them concurrently. Make sure to provide the specific '{topic}' as the query argument to the scraper tool so it can extract the most relevant chunks.\n\n Search Result: \n{search_results[:800]}")]}
    )
    result_text = reader_results['messages'][-1].content
    print("Reader Agent Results: " + result_text[:200] + "...")
    return {"reader_results": result_text}

def writer_node(state: AgentState):
    print("\n" + "="*20 + f" Writer Chain (Revision {state.get('revision_count', 0)}) " + "="*20)
    research_combined = (f"SEARCH RESULTS:\n{state['search_results']}\n\n"
                         f"DETAILED SCRAPED CONTENT:\n{state['reader_results']}")
    
    writer_result = writer_chain.invoke(
        {
            "topic": state["topic"],
            "research": research_combined,
            "feedback": state.get("feedback", "None")
        }
    )
    print("Writer Chain Result: " + writer_result[:200] + "...")
    return {"report": writer_result}

def critic_node(state: AgentState):
    print("\n" + "="*20 + " Critic Chain " + "="*20)
    feedback = critic_chain.invoke({"report": state['report']})
    print("Critic Feedback:\n" + feedback)
    return {"feedback": feedback, "revision_count": state.get("revision_count", 0) + 1}

def should_continue(state: AgentState):
    feedback = state.get("feedback", "")
    revision_count = state.get("revision_count", 0)
    
    if revision_count >= 1:
        print("\nMax revisions reached. Ending pipeline.")
        return "end"

    match = re.search(r'Score\s*:\s*(\d+)/10', feedback)
    if match:
        score = int(match.group(1))
        if score >= 8:
            print(f"\nScore is {score}/10. Report approved! Ending pipeline.")
            return "end"
        else:
            print(f"\nScore is {score}/10. Returning to Writer for improvements...")
            return "writer"
            
    # Default to writer if format fails
    return "writer"

# Build the Graph
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("search", search_node)
workflow.add_node("reader", reader_node)
workflow.add_node("writer", writer_node)
workflow.add_node("critic", critic_node)

# Add Edges
workflow.set_entry_point("search")
workflow.add_edge("search", "reader")
workflow.add_edge("reader", "writer")
workflow.add_edge("writer", "critic")

# Add Conditional Edges from Critic
workflow.add_conditional_edges(
    "critic",
    should_continue,
    {
        "end": END,
        "writer": "writer"
    }
)

app_graph = workflow.compile()

def run_research_pipeline(topic: str) -> dict:
    initial_state = {
        "topic": topic,
        "search_results": "",
        "reader_results": "",
        "report": "",
        "feedback": "",
        "revision_count": 0
    }
    
    final_state = app_graph.invoke(initial_state)
    return final_state

if __name__ == "__main__":
    topic = "Traditional RAG vs Agentic RAG"
    final_state = run_research_pipeline(topic)
    print("\n" + "="*20 + " Final Research Report " + "="*20)
    print(final_state['report'])
