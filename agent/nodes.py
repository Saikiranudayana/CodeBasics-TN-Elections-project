"""agent/nodes.py — LangGraph node functions for the AI election agent."""

from __future__ import annotations

import os
from typing import TypedDict, List, Any

from agent.tools import search_news, search_youtube
from agent.prompts import SUMMARISE_PROMPT, FOLLOWUP_PROMPT, ANSWER_PROMPT


class State(TypedDict, total=False):
    alerts: List[Any]
    selected_alert_index: int
    search_query: str
    raw_news: List[dict]
    raw_videos: List[dict]
    summary: str
    follow_up_questions: List[str]
    user_question: str
    answer: str
    messages: List[dict]


def _get_llm():
    """Return an Anthropic ChatAnthropic LLM instance."""
    try:
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model="claude-sonnet-4-20250514",
            api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
            max_tokens=1024,
        )
    except ImportError:
        raise ImportError("langchain-anthropic is not installed. Run: pip install langchain-anthropic")


def fetch_news_node(state: State) -> State:
    """Fetch news and videos for the selected alert."""
    alerts = state.get("alerts", [])
    idx = state.get("selected_alert_index", 0)
    if not alerts or idx >= len(alerts):
        state["raw_news"] = []
        state["raw_videos"] = []
        return state

    alert = alerts[idx]
    state["search_query"] = alert.search_query
    state["raw_news"] = search_news(alert.search_query, max_results=6)
    state["raw_videos"] = search_youtube(alert.search_query, max_results=3)
    return state


def summarise_node(state: State) -> State:
    """Generate a neutral factual summary using the LLM."""
    alerts = state.get("alerts", [])
    idx = state.get("selected_alert_index", 0)
    alert = alerts[idx] if alerts and idx < len(alerts) else None

    news_snippets = "\n\n".join(
        f"[{r.get('source', '')}] {r.get('title', '')}: {r.get('content', '')}"
        for r in state.get("raw_news", [])[:3]
    )

    if alert:
        prompt_text = SUMMARISE_PROMPT.format(
            title=alert.title,
            body=alert.body,
            metric_before=alert.metric_before,
            metric_after=alert.metric_after,
            change=alert.change,
            news_snippets=news_snippets or "No news articles found.",
        )
    else:
        state["summary"] = "No alert selected."
        return state

    try:
        llm = _get_llm()
        from langchain_core.messages import HumanMessage
        response = llm.invoke([HumanMessage(content=prompt_text)])
        state["summary"] = response.content
    except Exception as e:
        state["summary"] = f"[Summary unavailable: {e}]"

    return state


def generate_followups_node(state: State) -> State:
    """Generate 3 follow-up questions based on the summary."""
    summary = state.get("summary", "")
    if not summary or summary.startswith("["):
        state["follow_up_questions"] = []
        return state

    prompt_text = FOLLOWUP_PROMPT.format(summary=summary)
    try:
        llm = _get_llm()
        from langchain_core.messages import HumanMessage
        response = llm.invoke([HumanMessage(content=prompt_text)])
        lines = [l.strip() for l in response.content.split("\n") if l.strip()]
        questions = [l.lstrip("123. ").strip() for l in lines if l and l[0].isdigit()][:3]
        state["follow_up_questions"] = questions
    except Exception as e:
        state["follow_up_questions"] = [f"[Follow-ups unavailable: {e}]"]

    return state


def answer_question_node(state: State) -> State:
    """Answer a user question using the alert context and news."""
    user_question = state.get("user_question", "").strip()
    if not user_question:
        return state

    alerts = state.get("alerts", [])
    idx = state.get("selected_alert_index", 0)
    alert = alerts[idx] if alerts and idx < len(alerts) else None

    alert_context = (
        f"Alert: {alert.title}\n{alert.body}\n"
        f"Metric before: {alert.metric_before}, after: {alert.metric_after}"
        if alert else "No alert context."
    )

    news_snippets = "\n\n".join(
        f"[{r.get('source', '')}] {r.get('title', '')}: {r.get('content', '')}"
        for r in state.get("raw_news", [])[:5]
    )

    messages = state.get("messages", [])
    chat_history = "\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in messages[-6:]
    )

    prompt_text = ANSWER_PROMPT.format(
        alert_context=alert_context,
        news_snippets=news_snippets or "No news articles available.",
        chat_history=chat_history or "No prior messages.",
        user_question=user_question,
    )

    try:
        llm = _get_llm()
        from langchain_core.messages import HumanMessage
        response = llm.invoke([HumanMessage(content=prompt_text)])
        answer = response.content
    except Exception as e:
        answer = f"[Answer unavailable: {e}]"

    messages = list(messages)
    messages.append({"role": "user", "content": user_question})
    messages.append({"role": "assistant", "content": answer})

    state["messages"] = messages
    state["answer"] = answer
    state["user_question"] = ""
    return state
