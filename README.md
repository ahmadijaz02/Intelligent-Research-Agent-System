# Intelligent Research Agent System

A multi-agent AI research application that searches the web, extracts relevant information, generates a structured report, and evaluates the report through a critic-and-revision loop.

**Maintainer:** [Muhammad Ahmad Ijaz](https://github.com/ahmadijaz02)  
**Repository:** [ahmadijaz02/Intelligent-Research-Agent-System](https://github.com/ahmadijaz02/Intelligent-Research-Agent-System)

> **Attribution:** This project is adapted from [aura-research-agents](https://github.com/NadeemAhmad3/aura-research-agents), originally created by Nadeem Ahmad. The original MIT license is retained. This repository's name and documentation have been updated; the attribution does not imply that the original implementation was written from scratch by this repository's maintainer.

## Overview

Researching a topic often involves searching multiple sources, reading relevant pages, combining findings, and checking the quality of a draft. This project brings those steps together in a LangGraph workflow using specialized AI components.

### Workflow

1. **Search** — runs web searches through Tavily to gather source URLs and snippets.
2. **Read** — selects relevant search results, scrapes page content, and uses vector similarity search to extract relevant passages.
3. **Write** — creates a structured report with an introduction, key findings, conclusion, and sources.
4. **Critique** — scores the report and provides improvement feedback.
5. **Revise** — routes the draft back to the writer when the score is below the configured threshold, up to the maximum revision count.

## Key Features

- Multi-step research workflow orchestrated with **LangGraph**
- Web search using **Tavily**
- Asynchronous page retrieval with **aiohttp** and HTML parsing with **BeautifulSoup**
- Retrieval-augmented extraction using **Hugging Face embeddings** and **FAISS**
- Report generation and quality review using multiple LLM providers
- Conditional feedback loop for report revision
- Streamlit-based interface in `app.py`
- Environment-based API key configuration

## Technology Stack

| Area | Technologies |
|---|---|
| Language | Python |
| Workflow orchestration | LangGraph |
| LLM integrations | Groq, Google Gemini, Cohere |
| Web search | Tavily |
| Page extraction | aiohttp, BeautifulSoup |
| Retrieval | LangChain text splitters, Hugging Face embeddings, FAISS |
| User interface | Streamlit |
| Configuration | python-dotenv |

Model names and provider availability can change; check the configuration in `agents.py` and the relevant provider documentation if you need to update them.

## Project Structure

```text
Intelligent-Research-Agent-System/
├── app.py             # Streamlit user interface
├── agents.py          # Search and reader agents, writer and critic chains
├── pipeline.py        # LangGraph workflow and revision routing
├── tools.py           # Web search, scraping, and retrieval utilities
├── requirements.txt   # Python dependencies
├── .env               # Local API keys (create this yourself)
├── .gitignore
├── LICENSE            # Original MIT license and attribution
└── README.md
```

## Getting Started

### 1. Requirements

- Python 3.10 or newer recommended
- API keys for the services you intend to use:
  - Tavily
  - Groq
  - Google AI Studio
  - Cohere

### 2. Clone the repository

```bash
git clone https://github.com/ahmadijaz02/Intelligent-Research-Agent-System.git
cd Intelligent-Research-Agent-System
```

### 3. Create and activate a virtual environment

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a file named `.env` in the project root. Add your own API keys; do not commit this file.

```env
TAVILY_API_KEY=your_tavily_api_key
GROQ_API_KEY=your_groq_api_key
GOOGLE_API_KEY=your_google_api_key
COHERE_API_KEY=your_cohere_api_key
```

Use the variable names expected by the code and consult each provider's official dashboard to create keys. Never put real credentials in the README or source control.

### 6. Run the application

Start the Streamlit interface:

```bash
streamlit run app.py
```

To run the pipeline from the command line with the example topic configured in `pipeline.py`:

```bash
python pipeline.py
```

## How the Revision Loop Works

The graph in `pipeline.py` runs the search and reader steps, sends gathered material to the writer, and then passes the draft to the critic. The critic's feedback is inspected for a score in the expected `Score: X/10` format. A score of 8 or above ends the loop; otherwise, the draft can return to the writer until the configured revision limit is reached.

## Configuration Notes

- Provider models and generation settings are configured in `agents.py`.
- Search, scraping, chunking, embeddings, and FAISS retrieval are implemented in `tools.py`.
- The current implementation uses a 1,000-character chunk size, 150-character overlap, and retrieves the two most relevant chunks for a supplied query.
- External websites may block scraping or return little readable text. Search results and generated reports should be checked against the linked sources.
- LLM-generated reports can contain errors or unsupported claims. Treat the critic score as an automated signal, not a guarantee of factual correctness.

## Known Limitations

- Results depend on external APIs, their quotas, and model availability.
- Some websites cannot be scraped reliably.
- The current critic relies on parsing a textual score, so a response that does not follow the expected format may trigger another revision.
- The repository should be tested in your own environment before production use.

## Potential Improvements

- Add automated tests for tools, graph routing, and error handling.
- Improve URL validation, scraping timeouts, retries, and provider error messages.
- Add report export options and research history.
- Add stronger source verification and structured critic output.
- Add Docker support and a reproducible deployment configuration.

## Author

**Muhammad Ahmad Ijaz**  
Software Engineering graduate, National University of Computer and Emerging Sciences (FAST-NUCES).

- GitHub: [@ahmadijaz02](https://github.com/ahmadijaz02)

## License

This project retains the original MIT license and attribution. See [LICENSE](LICENSE) for the full license text and original copyright notice.
