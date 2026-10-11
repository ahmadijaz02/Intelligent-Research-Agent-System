import streamlit as st
import time
from agents import build_search_agent, build_reader_agent, writer_chain, critic_chain
import re

st.set_page_config(
    page_title="Aura Research",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
@import url('https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.11.0/dist/tabler-icons.min.css');

*{box-sizing:border-box;margin:0;padding:0}

html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"]{
    font-family:'Inter',sans-serif;
    background:#050508 !important;
    color:#e8e8ef;
    min-height:100vh;
}
[data-testid="stAppViewContainer"]>.main{padding:0!important}
[data-testid="stMain"]>div:first-child{padding:0!important}
.block-container{padding:0!important;max-width:100%!important}
section[data-testid="stSidebar"]{display:none}
[data-testid="stDecoration"]{display:none}

/* NAV */
.aura-nav{
    display:flex;align-items:center;justify-content:space-between;
    padding:0 56px;height:64px;
    background:rgba(5,5,8,0.92);
    border-bottom:1px solid rgba(52,211,153,0.12);
    position:sticky;top:0;z-index:100;
    backdrop-filter:blur(16px);
}
.aura-logo{
    display:flex;align-items:center;gap:10px;
    font-family:'Space Grotesk',sans-serif;
    font-size:1.15rem;font-weight:700;
    color:#34d399;letter-spacing:-0.02em;
}
.logo-mark{
    width:32px;height:32px;border-radius:8px;
    background:linear-gradient(135deg,#059669,#10b981);
    display:flex;align-items:center;justify-content:center;
    font-size:0.85rem;color:#fff;font-weight:800;
    box-shadow:0 0 16px rgba(52,211,153,0.3);
}
.nav-pills{display:flex;gap:8px}
.nav-pill{
    font-size:0.72rem;font-weight:600;letter-spacing:0.06em;text-transform:uppercase;
    padding:4px 12px;border-radius:999px;
    background:rgba(52,211,153,0.08);color:#34d399;
    border:1px solid rgba(52,211,153,0.2);
}
.nav-pill.gray{background:rgba(255,255,255,0.04);color:#6b7280;border-color:rgba(255,255,255,0.08)}

/* HERO */
.hero-section{
    min-height:calc(100vh - 64px);
    display:flex;flex-direction:column;align-items:center;justify-content:center;
    padding:60px 24px 80px;
    background:radial-gradient(ellipse 900px 600px at 50% 40%, rgba(16,185,129,0.06) 0%, transparent 70%),
               radial-gradient(ellipse 600px 400px at 20% 80%, rgba(6,95,70,0.04) 0%, transparent 60%),
               #050508;
    position:relative;overflow:hidden;
}
.hero-grid-bg{
    position:absolute;inset:0;
    background-image:
        linear-gradient(rgba(52,211,153,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(52,211,153,0.03) 1px, transparent 1px);
    background-size:60px 60px;
    mask-image:radial-gradient(ellipse 800px 500px at 50% 50%, black 0%, transparent 80%);
}
.hero-eyebrow{
    display:inline-flex;align-items:center;gap:6px;
    font-size:0.75rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;
    color:#34d399;padding:6px 14px;border-radius:999px;
    background:rgba(52,211,153,0.08);border:1px solid rgba(52,211,153,0.2);
    margin-bottom:28px;
}
.hero-title{
    font-family:'Space Grotesk',sans-serif;
    font-size:clamp(2.8rem,6vw,5rem);
    font-weight:700;letter-spacing:-0.04em;
    text-align:center;line-height:1.08;
    margin-bottom:24px;max-width:820px;
}
.hero-title .t-white{color:#f0f0f6}
.hero-title .t-green{
    background:linear-gradient(135deg,#34d399 0%,#6ee7b7 50%,#10b981 100%);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
}
.hero-sub{
    font-size:1.1rem;color:#6b7280;text-align:center;
    max-width:520px;line-height:1.65;margin-bottom:56px;font-weight:400;
}
.hero-stats{
    display:flex;gap:40px;align-items:center;margin-bottom:56px;
}
.stat-item{text-align:center}
.stat-num{
    font-family:'Space Grotesk',sans-serif;
    font-size:1.8rem;font-weight:700;color:#34d399;
    letter-spacing:-0.03em;
}
.stat-label{font-size:0.75rem;color:#4b5563;text-transform:uppercase;letter-spacing:0.07em;margin-top:3px}
.stat-div{width:1px;height:36px;background:rgba(255,255,255,0.06)}

/* PIPELINE ARCHITECTURE */
.arch-section{
    padding:80px 56px;
    background:#050508;
    border-top:1px solid rgba(255,255,255,0.04);
}
.section-label{
    font-size:0.72rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;
    color:#34d399;margin-bottom:16px;
}
.section-title{
    font-family:'Space Grotesk',sans-serif;
    font-size:1.8rem;font-weight:700;color:#f0f0f6;
    letter-spacing:-0.03em;margin-bottom:8px;
}
.section-sub{font-size:0.9rem;color:#4b5563;margin-bottom:48px}

.pipeline-arch{
    display:grid;grid-template-columns:repeat(4,1fr);gap:1px;
    background:rgba(52,211,153,0.08);
    border-radius:16px;overflow:hidden;
    border:1px solid rgba(52,211,153,0.12);
}
.arch-node{
    background:#080810;padding:28px 24px;position:relative;
    transition:background 0.2s;
}
.arch-node:hover{background:#0c0c18}
.arch-node-num{
    font-size:0.7rem;font-weight:700;letter-spacing:0.08em;
    color:#34d399;margin-bottom:16px;font-family:'JetBrains Mono',monospace;
}
.arch-node-icon{
    width:40px;height:40px;border-radius:10px;
    background:rgba(52,211,153,0.1);border:1px solid rgba(52,211,153,0.2);
    display:flex;align-items:center;justify-content:center;
    font-size:18px;margin-bottom:16px;color:#34d399;
}
.arch-node-name{
    font-family:'Space Grotesk',sans-serif;
    font-size:1rem;font-weight:600;color:#f0f0f6;margin-bottom:6px;
}
.arch-node-model{
    font-size:0.72rem;font-family:'JetBrains Mono',monospace;
    color:#059669;margin-bottom:10px;
    background:rgba(5,150,105,0.1);padding:3px 8px;border-radius:4px;
    display:inline-block;
}
.arch-node-desc{font-size:0.8rem;color:#4b5563;line-height:1.5}
.arch-arrow{
    position:absolute;right:-1px;top:50%;transform:translateY(-50%);
    color:#34d399;font-size:14px;z-index:2;opacity:0.4;
}

/* INPUT SECTION */
.input-wrap{width:100%;max-width:680px;margin:0 auto;}
.input-box{
    background:rgba(10,12,20,0.8);
    border:1px solid rgba(52,211,153,0.2);
    border-radius:14px;padding:24px;
    backdrop-filter:blur(8px);
}
.input-label{
    font-size:0.72rem;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;
    color:#34d399;margin-bottom:12px;display:flex;align-items:center;gap:6px;
}

div[data-testid="stTextInput"] input{
    background:#07090f!important;
    border:1px solid rgba(52,211,153,0.2)!important;
    border-radius:10px!important;
    color:#f0f0f6!important;
    font-size:1rem!important;
    padding:14px 16px!important;
    width:100%!important;
    font-family:'Inter',sans-serif!important;
    transition:border-color 0.15s,box-shadow 0.15s!important;
}
div[data-testid="stTextInput"] input:focus{
    border-color:#34d399!important;
    box-shadow:0 0 0 3px rgba(52,211,153,0.12)!important;
    outline:none!important;
}
div[data-testid="stTextInput"] input::placeholder{color:#374151!important}

div[data-testid="stButton"] button[kind="primary"]{
    background:linear-gradient(135deg,#059669,#10b981)!important;
    color:#fff!important;border:none!important;
    border-radius:10px!important;font-weight:600!important;
    font-size:0.95rem!important;padding:14px 28px!important;
    width:100%!important;cursor:pointer!important;
    transition:opacity 0.15s,transform 0.1s!important;
    letter-spacing:-0.01em!important;
    box-shadow:0 0 24px rgba(52,211,153,0.2)!important;
    font-family:'Space Grotesk',sans-serif!important;
}
div[data-testid="stButton"] button[kind="primary"]:hover{opacity:0.9!important;transform:translateY(-1px)!important}
div[data-testid="stButton"] button[kind="primary"]:active{transform:translateY(0)!important}

/* RESEARCH SECTION */
.research-wrap{max-width:880px;margin:0 auto;padding:0 24px 80px;}

/* PIPELINE TRACKER */
.tracker{
    display:flex;align-items:center;
    background:#08080f;border:1px solid rgba(52,211,153,0.1);
    border-radius:12px;padding:16px 24px;margin-bottom:24px;gap:0;
}
.tr-step{flex:1;display:flex;align-items:center;gap:8px}
.tr-step:not(:last-child){flex:1}
.tr-connector{flex:1;height:1px;background:rgba(52,211,153,0.08);margin:0 8px}
.tr-dot{
    width:28px;height:28px;border-radius:50%;
    display:flex;align-items:center;justify-content:center;
    font-size:0.7rem;font-weight:700;flex-shrink:0;
    background:#12121e;color:#374151;
    border:1px solid rgba(255,255,255,0.06);
    transition:all 0.3s;
}
.tr-dot.active{background:#059669;color:#fff;border-color:#34d399;box-shadow:0 0 12px rgba(52,211,153,0.35)}
.tr-dot.done{background:rgba(52,211,153,0.1);color:#34d399;border-color:rgba(52,211,153,0.3)}
.tr-label{font-size:0.75rem;color:#374151;font-weight:500;white-space:nowrap}
.tr-label.active{color:#34d399;font-weight:600}
.tr-label.done{color:#059669}

/* AGENT CARDS */
.agent-card{
    background:#08080f;border:1px solid rgba(255,255,255,0.05);
    border-radius:12px;margin-bottom:12px;overflow:hidden;
}
.agent-card-head{
    display:flex;align-items:center;gap:12px;padding:16px 20px;
    border-bottom:1px solid rgba(255,255,255,0.04);
}
.agent-icon-wrap{
    width:34px;height:34px;border-radius:8px;
    background:rgba(52,211,153,0.08);border:1px solid rgba(52,211,153,0.15);
    display:flex;align-items:center;justify-content:center;font-size:15px;color:#34d399;
}
.agent-name{font-size:0.9rem;font-weight:600;color:#e8e8ef}
.agent-model-tag{
    font-size:0.68rem;font-family:'JetBrains Mono',monospace;
    color:#059669;background:rgba(5,150,105,0.1);
    padding:2px 8px;border-radius:4px;margin-left:4px;
}
.agent-badge{
    margin-left:auto;font-size:0.68rem;font-weight:700;
    padding:3px 10px;border-radius:999px;letter-spacing:0.04em;
}
.badge-run{background:rgba(251,191,36,0.1);color:#fbbf24;border:1px solid rgba(251,191,36,0.2)}
.badge-ok{background:rgba(52,211,153,0.1);color:#34d399;border:1px solid rgba(52,211,153,0.2)}
.agent-body{padding:16px 20px}
.agent-status-text{font-size:0.82rem;color:#374151}

/* SOURCE CARDS */
.source-item{
    display:flex;gap:12px;align-items:flex-start;
    padding:12px 14px;background:#0c0c18;border-radius:8px;
    margin-bottom:8px;border:1px solid rgba(255,255,255,0.04);
    transition:border-color 0.15s;
}
.source-item:hover{border-color:rgba(52,211,153,0.15)}
.src-num{
    font-size:0.68rem;font-weight:700;font-family:'JetBrains Mono',monospace;
    color:#059669;background:rgba(5,150,105,0.1);
    padding:3px 7px;border-radius:4px;flex-shrink:0;margin-top:1px;
}
.src-content{flex:1;min-width:0}
.src-title{font-size:0.88rem;font-weight:500;color:#d1d5db;margin-bottom:4px}
.src-url{
    font-size:0.72rem;font-family:'JetBrains Mono',monospace;
    color:#34d399;word-break:break-all;margin-bottom:6px;
    display:flex;align-items:center;gap:4px;
}
.src-snippet{font-size:0.8rem;color:#4b5563;line-height:1.5}

/* SCRAPE PREVIEW */
.scrape-preview{
    background:#0c0c18;border-radius:8px;padding:14px 16px;
    border:1px solid rgba(255,255,255,0.04);
}
.scrape-url-row{
    display:flex;align-items:center;gap:6px;
    font-size:0.72rem;font-family:'JetBrains Mono',monospace;
    color:#34d399;margin-bottom:10px;word-break:break-all;
}
.scrape-text{font-size:0.82rem;color:#4b5563;line-height:1.6}

/* METRICS */
.metrics-grid{
    display:grid;grid-template-columns:repeat(4,1fr);gap:12px;
    margin-bottom:28px;
}
.metric-c{
    background:#08080f;border:1px solid rgba(255,255,255,0.05);
    border-radius:10px;padding:18px 20px;
}
.metric-lbl{
    font-size:0.7rem;font-weight:600;text-transform:uppercase;
    letter-spacing:0.07em;color:#374151;margin-bottom:10px;
    display:flex;align-items:center;gap:6px;
}
.metric-val{
    font-family:'Space Grotesk',sans-serif;
    font-size:1.9rem;font-weight:700;color:#34d399;
    letter-spacing:-0.04em;line-height:1;
}
.metric-unit{font-size:0.72rem;color:#374151;margin-top:4px}

/* RESULTS TABS */
div[data-testid="stTabs"] [data-baseweb="tab-list"]{
    background:#08080f!important;
    border-bottom:1px solid rgba(255,255,255,0.05)!important;
    gap:0!important;padding:0 4px!important;
}
div[data-testid="stTabs"] [data-baseweb="tab"]{
    background:transparent!important;
    color:#4b5563!important;
    border-radius:0!important;padding:12px 18px!important;
    font-size:0.83rem!important;font-weight:500!important;
    border-bottom:2px solid transparent!important;
    transition:color 0.15s,border-color 0.15s!important;
}
div[data-testid="stTabs"] [aria-selected="true"][data-baseweb="tab"]{
    color:#34d399!important;border-bottom-color:#34d399!important;
}
div[data-testid="stTabs"] [data-baseweb="tab-panel"]{
    background:#08080f!important;border-radius:0 0 12px 12px!important;
    border:1px solid rgba(255,255,255,0.05)!important;border-top:none!important;
    padding:24px!important;
}

.report-body{font-size:0.92rem;color:#9ca3af;line-height:1.78}
.report-body h1,.report-body h2,.report-body h3{
    color:#e8e8ef;font-weight:600;margin:1.4em 0 0.5em;
    font-family:'Space Grotesk',sans-serif;letter-spacing:-0.02em;
}
.report-body p{margin-bottom:0.85em}
.report-body ul,.report-body ol{padding-left:1.4em;margin-bottom:0.85em}
.report-body li{margin-bottom:0.3em}

.feedback-wrap{
    border-left:2px solid #ef4444;border-radius:0 8px 8px 0;
    background:rgba(239,68,68,0.04);padding:16px 20px;
}
.feedback-body{font-size:0.87rem;color:#6b7280;line-height:1.7}

div[data-testid="stTextArea"] textarea{
    background:#0c0c18!important;border:1px solid rgba(255,255,255,0.06)!important;
    color:#6b7280!important;border-radius:8px!important;
    font-family:'JetBrains Mono',monospace!important;font-size:0.78rem!important;
}

.stDownloadButton button{
    background:#08080f!important;border:1px solid rgba(52,211,153,0.2)!important;
    color:#34d399!important;border-radius:8px!important;
    font-size:0.83rem!important;font-weight:500!important;
}

.empty-state{
    text-align:center;padding:60px 24px;
    border:1px dashed rgba(52,211,153,0.1);border-radius:12px;margin-top:12px;
}
.empty-state h3{font-size:1rem;font-weight:500;color:#374151;margin-bottom:6px}
.empty-state p{font-size:0.83rem;color:#1f2937}
</style>

<div class="aura-nav">
  <div class="aura-logo">
    <div class="logo-mark">✦</div>
    Aura<span style="color:#6ee7b7">Research</span>
  </div>
  <div class="nav-pills">
    <span class="nav-pill">4-Agent Pipeline</span>
    <span class="nav-pill gray">Groq · Gemini · Cohere</span>
  </div>
</div>
""", unsafe_allow_html=True)

if "state" not in st.session_state:
    st.session_state.state = {"search_results":"","reader_results":"","report":"","feedback":"","logs":[]}
if "execution_times" not in st.session_state:
    st.session_state.execution_times = {}
if "pipeline_step" not in st.session_state:
    st.session_state.pipeline_step = 0
if "parsed_sources" not in st.session_state:
    st.session_state.parsed_sources = []
if "scraped_url" not in st.session_state:
    st.session_state.scraped_url = ""

def log_agent(name, msg):
    ts = time.strftime("%H:%M:%S")
    st.session_state.state["logs"].append(f"[{ts}] {name}: {msg}")

def parse_sources(raw):
    sources = []
    # Pattern 1: formatted "Title: ... URL: ... content: ..."
    blocks = re.split(r'\n(?=Title:)', raw.strip())
    for i, block in enumerate(blocks, 1):
        tm = re.search(r'Title:\s*(.+)', block)
        um = re.search(r'URL:\s*(https?://\S+)', block)
        sm = re.search(r'content:\s*(.+)', block, re.DOTALL)
        if um:
            sources.append({
                "num": i,
                "title": tm.group(1).strip() if tm else "Untitled",
                "url": um.group(1).strip().rstrip(')').rstrip("'").rstrip('"'),
                "snippet": sm.group(1).strip()[:220] if sm else ""
            })
    if sources:
        return sources
    # Pattern 2: fallback — extract all URLs from raw text with surrounding context
    url_blocks = re.findall(r"'url':\s*'(https?://[^']+)'.*?'title':\s*'([^']+)'.*?'content':\s*'([^']{0,300})'", raw, re.DOTALL)
    for i, (url, title, content) in enumerate(url_blocks, 1):
        sources.append({"num": i, "title": title.strip(), "url": url.strip(), "snippet": content.strip()[:220]})
    if sources:
        return sources
    # Pattern 3: bare URLs anywhere in text
    urls = re.findall(r'https?://[^\s\'"<>]+', raw)
    seen = set()
    for i, url in enumerate(urls, 1):
        url = url.rstrip('.,)')
        if url not in seen:
            seen.add(url)
            sources.append({"num": i, "title": url.split('/')[2], "url": url, "snippet": ""})
    return sources

def to_str(val):
    if isinstance(val, list):
        return " ".join(str(x.get('text', x) if isinstance(x, dict) else x) for x in val)
    return str(val) if val else ""

def extract_url(raw):
    raw = to_str(raw)
    m = re.search(r'(?:Relevant Extracts from|Content from) (https?://\S+):', raw)
    if m:
        return m.group(1)
    m2 = re.search(r"https?://[^\s'\"<>]+", raw)
    return m2.group(0).rstrip('.,)') if m2 else ""

def render_tracker(step):
    steps = [
        ("ti-search","Search"),("ti-browser","Reader"),
        ("ti-pencil","Writer"),("ti-eye","Critic")
    ]
    parts = []
    for i,(icon,label) in enumerate(steps,1):
        dc = "active" if step==i else ("done" if step>i else "")
        lc = dc
        text = '<i class="ti ti-check" style="font-size:12px"></i>' if step>i else str(i)
        parts.append(f"""
<div class="tr-step">
  <div class="tr-dot {dc}">{text}</div>
  <span class="tr-label {lc}"><i class="ti {icon}" style="font-size:13px;margin-right:3px"></i>{label}</span>
</div>""")
        if i < len(steps):
            parts.append('<div class="tr-connector"></div>')
    return '<div class="tracker">' + "".join(parts) + '</div>'

# ── HERO ──
if not st.session_state.state["report"]:
    st.markdown("""
<div class="hero-section">
  <div class="hero-grid-bg"></div>
  <div class="hero-eyebrow">
    <i class="ti ti-sparkles" style="font-size:13px"></i>
    Autonomous AI Research
  </div>
  <h1 class="hero-title">
    <span class="t-white">Research, </span><span class="t-green">intelligently<br>automated.</span>
  </h1>
  <p class="hero-sub">Four specialized AI agents collaborate to search, extract, synthesize, and verify — delivering rigorous research reports in minutes.</p>
  <div class="hero-stats">
    <div class="stat-item"><div class="stat-num">4</div><div class="stat-label">AI Agents</div></div>
    <div class="stat-div"></div>
    <div class="stat-item"><div class="stat-num">3</div><div class="stat-label">LLM Providers</div></div>
    <div class="stat-div"></div>
    <div class="stat-item"><div class="stat-num">∞</div><div class="stat-label">Topics</div></div>
  </div>
""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown('<div class="input-box"><div class="input-label"><i class="ti ti-target" style="font-size:13px"></i>Enter your research topic</div>', unsafe_allow_html=True)
        topic = st.text_input("", placeholder="e.g., Traditional RAG vs Agentic RAG", value="Traditional RAG vs Agentic RAG", label_visibility="collapsed")
        start_research = st.button("Run Autonomous Pipeline →", type="primary", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Architecture section
    st.markdown("""
<div class="arch-section">
  <div style="max-width:960px;margin:0 auto">
    <div class="section-label"><i class="ti ti-circuit-board" style="font-size:12px"></i> Pipeline Architecture</div>
    <div class="section-title">How Aura Research works</div>
    <div class="section-sub">Each agent is specialized, runs sequentially, and hands off enriched context to the next.</div>
    <div class="pipeline-arch">
      <div class="arch-node">
        <div class="arch-node-num">STEP 01</div>
        <div class="arch-node-icon"><i class="ti ti-world-search" style="font-size:18px"></i></div>
        <div class="arch-node-name">Search Agent</div>
        <div class="arch-node-model">groq / llama-3.3-70b</div>
        <div class="arch-node-desc">Runs 2 targeted Tavily web searches and returns ranked results with titles, URLs, and content snippets.</div>
      </div>
      <div class="arch-node">
        <div class="arch-node-num">STEP 02</div>
        <div class="arch-node-icon"><i class="ti ti-file-text" style="font-size:18px"></i></div>
        <div class="arch-node-name">Reader Agent</div>
        <div class="arch-node-model">gemini-2.5-flash</div>
        <div class="arch-node-desc">Selects the highest-relevance URL, scrapes full HTML content, and extracts semantic chunks via RAG vector search.</div>
      </div>
      <div class="arch-node">
        <div class="arch-node-num">STEP 03</div>
        <div class="arch-node-icon"><i class="ti ti-writing" style="font-size:18px"></i></div>
        <div class="arch-node-name">Writer Chain</div>
        <div class="arch-node-model">cohere / command-a</div>
        <div class="arch-node-desc">Synthesizes all gathered research into a structured report with introduction, key findings, conclusion, and sources.</div>
      </div>
      <div class="arch-node">
        <div class="arch-node-num">STEP 04</div>
        <div class="arch-node-icon"><i class="ti ti-checklist" style="font-size:18px"></i></div>
        <div class="arch-node-name">Critic Chain</div>
        <div class="arch-node-model">groq / llama-3.1-8b</div>
        <div class="arch-node-desc">Reviews the report for factual accuracy, structural quality, and citation completeness. Returns a score and actionable feedback.</div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

else:
    # results page top input
    st.markdown('<div style="max-width:880px;margin:0 auto;padding:32px 24px 0">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,4,1])
    with col2:
        topic = st.text_input("", placeholder="New research topic...", label_visibility="collapsed")
        start_research = st.button("Run New Research →", type="primary", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── PIPELINE EXECUTION ──
if start_research and topic:
    st.session_state.state = {"search_results":"","reader_results":"","report":"","feedback":"","logs":[]}
    st.session_state.parsed_sources = []
    st.session_state.scraped_url = ""
    st.session_state.execution_times = {}
    start_total = time.time()

    st.markdown('<div class="research-wrap">', unsafe_allow_html=True)
    tracker_ph = st.empty()
    tracker_ph.markdown(render_tracker(0), unsafe_allow_html=True)

    # STAGE 1 SEARCH
    st.session_state.pipeline_step = 1
    tracker_ph.markdown(render_tracker(1), unsafe_allow_html=True)
    t0 = time.time()
    s_ph = st.empty()
    s_ph.markdown("""<div class="agent-card"><div class="agent-card-head">
      <div class="agent-icon-wrap"><i class="ti ti-world-search"></i></div>
      <span class="agent-name">Search Agent</span><span class="agent-model-tag">llama-3.3-70b</span>
      <span class="agent-badge badge-run">Running</span></div>
      <div class="agent-body"><div class="agent-status-text">
        <i class="ti ti-loader" style="font-size:13px;margin-right:6px"></i>Querying Tavily search API…
      </div></div></div>""", unsafe_allow_html=True)

    log_agent("Search Agent", f"Searching for: '{topic}'")
    search_agent = build_search_agent()
    search_results = search_agent.invoke(
        {"messages":[("user",f"Search EXACTLY 2 times for recent reliable information about: {topic}")]},
        config={"recursion_limit":6}
    )
    # Extract tool outputs (web_search returns formatted text in ToolMessages)
    # The final agent message is prose summary - tool messages have the raw data
    tool_texts = []
    for msg in search_results['messages']:
        msg_type = getattr(msg, 'type', None)
        if msg_type == 'tool':
            c = msg.content
            tool_texts.append(c if isinstance(c, str) else str(c))
    raw_search = "\n\n".join(tool_texts) if tool_texts else (search_results['messages'][-1].content or "")
    st.session_state.state["search_results"] = raw_search or "No results."
    st.session_state.parsed_sources = parse_sources(raw_search)
    st.session_state.execution_times["Search Agent"] = round(time.time()-t0, 2)
    log_agent("Search Agent", f"Found {len(st.session_state.parsed_sources)} sources")

    srcs_html = ""
    for s in st.session_state.parsed_sources:
        srcs_html += f"""<div class="source-item">
          <span class="src-num">#{s['num']}</span>
          <div class="src-content">
            <div class="src-title">{s['title']}</div>
            <div class="src-url"><i class="ti ti-link" style="font-size:11px;flex-shrink:0"></i>{s['url']}</div>
            <div class="src-snippet">{s['snippet']}</div>
          </div></div>"""
    if not srcs_html:
        srcs_html = f'<div class="src-snippet">{raw_search[:400]}</div>'

    n = len(st.session_state.parsed_sources)
    s_ph.markdown(f"""<div class="agent-card"><div class="agent-card-head">
      <div class="agent-icon-wrap"><i class="ti ti-world-search"></i></div>
      <span class="agent-name">Search Agent</span><span class="agent-model-tag">llama-3.3-70b</span>
      <span class="agent-badge badge-ok"><i class="ti ti-check" style="font-size:11px"></i> {n} sources found</span>
    </div><div class="agent-body">{srcs_html}</div></div>""", unsafe_allow_html=True)

    # STAGE 2 READER
    st.session_state.pipeline_step = 2
    tracker_ph.markdown(render_tracker(2), unsafe_allow_html=True)
    t0 = time.time()
    r_ph = st.empty()
    r_ph.markdown("""<div class="agent-card"><div class="agent-card-head">
      <div class="agent-icon-wrap"><i class="ti ti-browser"></i></div>
      <span class="agent-name">Reader Agent</span><span class="agent-model-tag">gemini-2.5-flash</span>
      <span class="agent-badge badge-run">Scraping</span></div>
      <div class="agent-body"><div class="agent-status-text">
        <i class="ti ti-loader" style="font-size:13px;margin-right:6px"></i>Selecting best URL and extracting content with RAG…
      </div></div></div>""", unsafe_allow_html=True)

    log_agent("Reader Agent", "Scraping top source…")
    reader_agent = build_reader_agent()
    reader_results = reader_agent.invoke(
        {"messages":[("user",
            f"Scrape the single most relevant URL from these search results about '{topic}'.\n\n"
            f"Search Results:\n{st.session_state.state['search_results'][:400]}")]},
        config={"recursion_limit":4}
    )
    # Collect tool outputs from reader agent (same pattern as search agent)
    reader_tool_texts = []
    for msg in reader_results['messages']:
        if getattr(msg, 'type', None) == 'tool':
            c = msg.content
            reader_tool_texts.append(to_str(c))
    raw_reader_raw = reader_results['messages'][-1].content
    raw_reader = "\n\n".join(reader_tool_texts) if reader_tool_texts else to_str(raw_reader_raw)
    raw_reader = raw_reader or "No content."
    st.session_state.state["reader_results"] = raw_reader
    st.session_state.scraped_url = extract_url(raw_reader)
    st.session_state.execution_times["Reader Agent"] = round(time.time()-t0, 2)
    log_agent("Reader Agent", f"Scraped: {st.session_state.scraped_url or 'unknown'}")

    url_row = f'<div class="scrape-url-row"><i class="ti ti-link" style="font-size:11px"></i>{st.session_state.scraped_url}</div>' if st.session_state.scraped_url else ""
    preview = raw_reader[:500].replace("<","&lt;") + ("…" if len(raw_reader)>500 else "")
    r_ph.markdown(f"""<div class="agent-card"><div class="agent-card-head">
      <div class="agent-icon-wrap"><i class="ti ti-browser"></i></div>
      <span class="agent-name">Reader Agent</span><span class="agent-model-tag">gemini-2.5-flash</span>
      <span class="agent-badge badge-ok"><i class="ti ti-check" style="font-size:11px"></i> Content extracted</span>
    </div><div class="agent-body">
      <div class="scrape-preview">{url_row}<div class="scrape-text">{preview}</div></div>
    </div></div>""", unsafe_allow_html=True)

    # STAGE 3 WRITER
    st.session_state.pipeline_step = 3
    tracker_ph.markdown(render_tracker(3), unsafe_allow_html=True)
    t0 = time.time()
    w_ph = st.empty()
    w_ph.markdown("""<div class="agent-card"><div class="agent-card-head">
      <div class="agent-icon-wrap"><i class="ti ti-pencil"></i></div>
      <span class="agent-name">Writer Chain</span><span class="agent-model-tag">cohere / command-a</span>
      <span class="agent-badge badge-run">Writing</span></div>
      <div class="agent-body"><div class="agent-status-text">
        <i class="ti ti-loader" style="font-size:13px;margin-right:6px"></i>Synthesizing research into structured report…
      </div></div></div>""", unsafe_allow_html=True)

    log_agent("Writer Chain", "Composing report…")
    research_combined = (
        f"SEARCH RESULTS:\n{st.session_state.state['search_results']}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{st.session_state.state['reader_results']}"
    )
    writer_result = writer_chain.invoke({
        "topic": topic,
        "research": research_combined,
        "feedback": st.session_state.state.get("feedback","None")
    })
    st.session_state.state["report"] = writer_result or "Error generating report."
    st.session_state.execution_times["Writer Chain"] = round(time.time()-t0, 2)
    log_agent("Writer Chain", "Report draft complete.")

    rp = (writer_result or "")[:300] + "…"
    w_ph.markdown(f"""<div class="agent-card"><div class="agent-card-head">
      <div class="agent-icon-wrap"><i class="ti ti-pencil"></i></div>
      <span class="agent-name">Writer Chain</span><span class="agent-model-tag">cohere / command-a</span>
      <span class="agent-badge badge-ok"><i class="ti ti-check" style="font-size:11px"></i> Report drafted</span>
    </div><div class="agent-body">
      <div class="scrape-text">{rp}</div>
    </div></div>""", unsafe_allow_html=True)

    # STAGE 4 CRITIC
    st.session_state.pipeline_step = 4
    tracker_ph.markdown(render_tracker(4), unsafe_allow_html=True)
    t0 = time.time()
    c_ph = st.empty()
    c_ph.markdown("""<div class="agent-card"><div class="agent-card-head">
      <div class="agent-icon-wrap"><i class="ti ti-eye"></i></div>
      <span class="agent-name">Critic Chain</span><span class="agent-model-tag">llama-3.1-8b</span>
      <span class="agent-badge badge-run">Auditing</span></div>
      <div class="agent-body"><div class="agent-status-text">
        <i class="ti ti-loader" style="font-size:13px;margin-right:6px"></i>Auditing report quality, citations, and structure…
      </div></div></div>""", unsafe_allow_html=True)

    log_agent("Critic Chain", "Running quality audit…")
    feedback_result = critic_chain.invoke({"report": st.session_state.state["report"]})
    st.session_state.state["feedback"] = feedback_result or "No feedback."
    st.session_state.execution_times["Critic Chain"] = round(time.time()-t0, 2)
    log_agent("Critic Chain", "Audit complete.")

    sm = re.search(r'Score:\s*(\d+/\d+)', feedback_result or "")
    score_txt = sm.group(1) if sm else "—"
    fp = (feedback_result or "")[:350] + ("…" if len(feedback_result or "")>350 else "")
    c_ph.markdown(f"""<div class="agent-card"><div class="agent-card-head">
      <div class="agent-icon-wrap"><i class="ti ti-eye"></i></div>
      <span class="agent-name">Critic Chain</span><span class="agent-model-tag">llama-3.1-8b</span>
      <span class="agent-badge badge-ok"><i class="ti ti-check" style="font-size:11px"></i> Score: {score_txt}</span>
    </div><div class="agent-body">
      <div class="feedback-wrap"><div class="feedback-body">{fp}</div></div>
    </div></div>""", unsafe_allow_html=True)

    st.session_state.execution_times["Total"] = round(time.time()-start_total, 2)
    st.session_state.pipeline_step = 5
    tracker_ph.markdown(render_tracker(5), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.rerun()

# ── RESULTS ──
if st.session_state.state["report"] and not (start_research and topic):
    et = st.session_state.execution_times
    st.markdown('<div class="research-wrap">', unsafe_allow_html=True)
    st.markdown(render_tracker(5), unsafe_allow_html=True)

    st.markdown(f"""
    <div class="metrics-grid">
      <div class="metric-c">
        <div class="metric-lbl"><i class="ti ti-world-search" style="font-size:12px"></i>Search</div>
        <div class="metric-val">{et.get('Search Agent','—')}</div>
        <div class="metric-unit">seconds</div>
      </div>
      <div class="metric-c">
        <div class="metric-lbl"><i class="ti ti-browser" style="font-size:12px"></i>Reader</div>
        <div class="metric-val">{et.get('Reader Agent','—')}</div>
        <div class="metric-unit">seconds</div>
      </div>
      <div class="metric-c">
        <div class="metric-lbl"><i class="ti ti-pencil" style="font-size:12px"></i>Writer</div>
        <div class="metric-val">{et.get('Writer Chain','—')}</div>
        <div class="metric-unit">seconds</div>
      </div>
      <div class="metric-c">
        <div class="metric-lbl"><i class="ti ti-clock" style="font-size:12px"></i>Total</div>
        <div class="metric-val">{et.get('Total','—')}</div>
        <div class="metric-unit">seconds</div>
      </div>
    </div>""", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📝 Research Report", "🔎 Editorial Critique"])

    with tab1:
        st.markdown('<div class="report-body">', unsafe_allow_html=True)
        st.markdown(st.session_state.state["report"])
        st.markdown('</div>', unsafe_allow_html=True)
        topic_slug = (topic or "research").lower().replace(" ","_") if "topic" in dir() else "research"
        st.download_button(
            "⬇ Download Report (.md)",
            data=st.session_state.state["report"],
            file_name=f"{topic_slug}_report.md",
            mime="text/markdown"
        )

    with tab2:
        st.markdown('<div class="feedback-wrap"><div class="feedback-body">', unsafe_allow_html=True)
        st.markdown(st.session_state.state["feedback"])
        st.markdown('</div></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

elif not start_research and not st.session_state.state["report"]:
    pass