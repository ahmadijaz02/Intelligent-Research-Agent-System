from langchain.tools import tool 
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
import asyncio
import aiohttp
from dotenv import load_dotenv

# Fix HF SSL Decryption errors on Windows
os.environ["HF_HUB_DISABLE_HTTP2"] = "1"

from rich import print
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

tavily = TavilyClient(api_key=os.getenv('TAVILY_API_KEY'))

@tool 
def web_search(query: str) -> str:
    """ Search the web for recent and reliable information on a topic. Return Titles, URL 
  and snippets of the search results. """
    search_results = tavily.search(query=query, num_results=2,max_results=2)
    formatted_results = []
    print(search_results)
    for result in search_results['results']:
        title = result['title']
        url = result['url']
        snippet = result['content'][:250]  # Truncate to avoid TPM limits
        formatted_results.append(f"Title: {title}\nURL: {url}\ncontent: {snippet}\n")
    return "\n".join(formatted_results)[:2000] # Final truncation

async def fetch_and_parse(url: str, session: aiohttp.ClientSession) -> str:
    try:
        async with session.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'}) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            paragraphs = soup.find_all('p')
            content = "\n".join([para.get_text() for para in paragraphs])
            return content if content.strip() else "No readable text found on the page."
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ""

async def scrape_multiple_concurrently(urls: list[str]) -> dict:
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_and_parse(url, session) for url in urls]
        results = await asyncio.gather(*tasks)
        return {url: result for url, result in zip(urls, results) if result}

@tool
def scrape_web_pages(urls: list[str], query: str = "") -> str:
    """ Scrape the content of multiple web pages concurrently given their URLs and an optional search query. 
    If a query is provided, it extracts the most relevant chunks using RAG (Vector Search) to avoid context limit overflow. """
    
    # Run async scraping loop
    scraped_data = asyncio.run(scrape_multiple_concurrently(urls))
    
    if not scraped_data:
        return "No readable text found on any of the provided pages."
        
    combined_results = []
    
    for url, content in scraped_data.items():
        if query:
            # Implement RAG (Chunking + Vector Store)
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
            docs = text_splitter.create_documents([content])
            
            # Using free HuggingFace embeddings
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            vectorstore = FAISS.from_documents(docs, embeddings)
            
            # Retrieve top 2 most relevant chunks per URL to save space
            docs_retrieved = vectorstore.similarity_search(query, k=2)
            retrieved_text = "\n\n...\n\n".join([doc.page_content for doc in docs_retrieved])
            combined_results.append(f"Relevant Extracts from {url}:\n{retrieved_text}")
        else:
            combined_results.append(f"Content from {url}:\n{content[:2000]}") # Return up to 2000 chars per url
            
    return "\n\n" + "="*40 + "\n\n".join(combined_results)

# Unittest 
if __name__ == "__main__":
    result = web_search.invoke("What is the latest research on multi-agent systems?")
    print(result)

    scrapper_result = scrape_web_pages.invoke({"urls": ["https://en.wikipedia.org/wiki/Multi-agent_system"], "query": "agent"})
    print(scrapper_result)


