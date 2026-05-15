"""agent/graph.py — LangGraph StateGraph definition for the AI election agent."""

from __future__ import annotations

from typing import Any

try:
    from langgraph.graph import StateGraph, END
    _langgraph_available = True
except ImportError:
    _langgraph_available = False

from agent.nodes import State, fetch_news_node, summarise_node, generate_followups_node, answer_question_node


def _build_graph():
    if not _langgraph_available:
        return None
    graph = StateGraph(State)
    graph.add_node("fetch_news", fetch_news_node)
    graph.add_node("summarise", summarise_node)
    graph.add_node("generate_followups", generate_followups_node)
    graph.add_node("answer_question", answer_question_node)

    graph.set_entry_point("fetch_news")
    graph.add_edge("fetch_news", "summarise")
    graph.add_edge("summarise", "generate_followups")
    graph.add_edge("generate_followups", END)
    graph.add_edge("answer_question", END)

    return graph.compile()


compiled_graph = _build_graph()


def run_research(alerts: list, selected_index: int) -> State:
    """Run the research pipeline for a selected alert."""
    initial_state: State = {
        "alerts": alerts,
        "selected_alert_index": selected_index,
        "search_query": "",
        "raw_news": [],
        "raw_videos": [],
        "summary": "",
        "follow_up_questions": [],
        "user_question": "",
        "answer": "",
        "messages": [],
    }
    if compiled_graph is None:
        # Fallback: run nodes manually if langgraph unavailable
        state = fetch_news_node(initial_state)
        state = summarise_node(state)
        state = generate_followups_node(state)
        return state
    return compiled_graph.invoke(initial_state)


def run_qa(state: State, question: str) -> State:
    """Run the Q&A node for a user question."""
    state = dict(state)
    state["user_question"] = question
    if compiled_graph is None:
        return answer_question_node(state)

    # Build a minimal graph for the Q&A path
    if not _langgraph_available:
        return answer_question_node(state)

    qa_graph = StateGraph(State)
    qa_graph.add_node("answer_question", answer_question_node)
    qa_graph.set_entry_point("answer_question")
    qa_graph.add_edge("answer_question", END)
    compiled_qa = qa_graph.compile()
    return compiled_qa.invoke(state)
