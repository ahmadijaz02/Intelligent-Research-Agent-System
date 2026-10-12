from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search, scrape_web_pages
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_cohere import ChatCohere

load_dotenv()

# ─────────── PROVIDER / KEY MAP ───────────
PROVIDER_ENV_KEY = {
    "Groq": "GROQ_API_KEY",
    "Google Gemini": "GOOGLE_API_KEY",
    "Cohere": "COHERE_API_KEY",
    "OpenAI": "OPENAI_API_KEY",
}

def provider_available(provider: str) -> bool:
    key = PROVIDER_ENV_KEY.get(provider)
    return bool(key and os.getenv(key))

def available_providers() -> list[str]:
    return [p for p in PROVIDER_ENV_KEY if provider_available(p)]

# ─────────── MODEL REGISTRY ───────────
# Keyed by provider → list of model ids users can pick from the UI.
MODEL_CATALOG = {
    "Groq": [
        "openai/gpt-oss-20b",
        "openai/gpt-oss-120b",
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
    ],
    "Google Gemini": [
        "gemini-flash-latest",
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-1.5-flash",
    ],
    "Cohere": [
        "command-a-03-2025",
        "command-r-plus-08-2024",
        "command-r-08-2024",
    ],
    "OpenAI": [
        "gpt-4o-mini",
        "gpt-4o",
        "gpt-4.1-mini",
    ],
}

# Default pick per stage: (provider, model)
DEFAULT_MODELS = {
    "search": ("Groq", "openai/gpt-oss-20b"),
    "reader": ("Cohere", "command-a-03-2025"),
    "writer": ("Cohere", "command-a-03-2025"),
    "critic": ("Groq", "openai/gpt-oss-20b"),
}


def make_llm(provider: str, model: str, *, temperature: float = 0.0, max_tokens: int | None = None):
    """Factory: returns a LangChain chat model for the given provider/model."""
    env_key = PROVIDER_ENV_KEY.get(provider)
    if env_key and not os.getenv(env_key):
        raise RuntimeError(
            f"Missing API key for {provider}. Set {env_key} in your .env file to use this provider."
        )
    kwargs = {"temperature": temperature}
    if provider == "Groq":
        if max_tokens:
            kwargs["max_tokens"] = max_tokens
        return ChatGroq(model=model, **kwargs)
    if provider == "Google Gemini":
        return ChatGoogleGenerativeAI(model=model, **kwargs)
    if provider == "Cohere":
        return ChatCohere(model=model, **kwargs)
    if provider == "OpenAI":
        if max_tokens:
            kwargs["max_tokens"] = max_tokens
        return ChatOpenAI(model=model, **kwargs)
    raise ValueError(f"Unknown provider: {provider}")


# ─────────── AGENT BUILDERS (now accept model selections) ───────────
def build_search_agent(provider: str | None = None, model: str | None = None):
    p, m = (provider, model) if provider and model else DEFAULT_MODELS["search"]
    llm = make_llm(p, m, temperature=0, max_tokens=512)
    return create_react_agent(
        model=llm,
        tools=[web_search],
        prompt="You are a search agent. Use the web_search tool EXACTLY 2 times with different queries, then STOP and return all results. Do NOT call web_search more than 2 times under any circumstances."
    )


def build_reader_agent(provider: str | None = None, model: str | None = None):
    p, m = (provider, model) if provider and model else DEFAULT_MODELS["reader"]
    llm = make_llm(p, m, temperature=0)
    return create_react_agent(
        model=llm,
        tools=[scrape_web_pages],
        prompt="You are a web scraper. Use scrape_web_pages tool ONCE on the single most relevant URL, then STOP immediately and return the content."
    )


# ─────────── WRITER / CRITIC PROMPTS ───────────
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer that writes a comprehensive research report based on the information provided by the search and reader agents. The report should be well-structured, clear, and concise."),
    ("human", """Write a detailed research report on the topic below.

     Topic: {topic}
     Research Gathered: {research}
     Feedback from previous draft (if any, please address this to improve): {feedback}

     Structure the report as:
     - Introduction
     - Key Findings
     - Conclusion
     - Sources (list all URLs found in the research)

     Be detailed, factual and professional.
     """)
])

critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

     Report: {report}

     Respond in this exact format:
     Score: X/10

     Strengths: List the strengths of the report.

     Areas to Improve: List the weaknesses and areas of improvement. Be specific and constructive.

     One Line Verdict: ..."""),
])


def build_writer_chain(provider: str | None = None, model: str | None = None):
    p, m = (provider, model) if provider and model else DEFAULT_MODELS["writer"]
    llm = make_llm(p, m, temperature=0.3)
    return writer_prompt | llm | StrOutputParser()


def build_critic_chain(provider: str | None = None, model: str | None = None):
    p, m = (provider, model) if provider and model else DEFAULT_MODELS["critic"]
    llm = make_llm(p, m, temperature=0, max_tokens=1024)
    return critic_prompt | llm | StrOutputParser()


# ─────────── BACK-COMPAT exported chains (default models) ───────────
writer_chain = build_writer_chain()
critic_chain = build_critic_chain()
