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

# Change llm_search from llama-3.1-8b-instant to:
llm_search = ChatGroq(model="llama-3.3-70b-versatile", temperature=0, max_tokens=512)
llm_reader = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
llm_writer = ChatCohere(model="command-a-03-2025", temperature=0.3)
llm_critic = ChatGroq(model="llama-3.1-8b-instant", temperature=0, max_tokens=1024)

def build_search_agent():
    return create_react_agent(
        model=llm_search, 
        tools=[web_search], 
        prompt="You are a search agent. Use the web_search tool EXACTLY 2 times with different queries, then STOP and return all results. Do NOT call web_search more than 2 times under any circumstances."
    )

def build_reader_agent():
    return create_react_agent(
        model=llm_reader, 
        tools=[scrape_web_pages], 
        prompt="You are a web scraper. Use scrape_web_pages tool ONCE on the single most relevant URL, then STOP immediately and return the content."
    )

# Writer Chain 
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

writer_chain = writer_prompt | llm_writer | StrOutputParser()

# Critic Chain 
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

critic_chain = critic_prompt | llm_critic | StrOutputParser()