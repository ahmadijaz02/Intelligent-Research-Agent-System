import streamlit as st
import time
import json
import re
from datetime import datetime
from agents import (
    build_search_agent, build_reader_agent,
    build_writer_chain, build_critic_chain,
    MODEL_CATALOG, DEFAULT_MODELS, available_providers, PROVIDER_ENV_KEY,
)

st.set_page_config(
    page_title="Intelligent Research Agent",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────── STYLES ───────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
@import url('https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.11.0/dist/tabler-icons.min.css');

:root{
    --bg-0:#ffffff;
    --bg-1:#f8f8fc;
    --bg-2:#f1f1f8;
    --border:rgba(15,23,42,0.08);
    --border-hi:rgba(37,99,235,0.35);
    --text-0:#0f172a;
    --text-1:#334155;
    --text-2:#64748b;
    --text-3:#94a3b8;
    --accent:#2563eb;
    --accent-2:#3b82f6;
    --accent-3:#60a5fa;
    --accent-soft:#eff6ff;
    --accent-glow:rgba(37,99,235,0.2);
    --success:#10b981;
    --warn:#f59e0b;
    --err:#dc2626;
}

*{box-sizing:border-box}
html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"]{
    font-family:'Inter',sans-serif;
    background:var(--bg-0) !important;color:var(--text-0);min-height:100vh;
}
[data-testid="stAppViewContainer"]>.main{padding:0!important}
[data-testid="stMain"]>div:first-child{padding:0!important}
.block-container{padding:0!important;max-width:100%!important}
[data-testid="stDecoration"]{display:none}
[data-testid="stHeader"]{background:transparent}

/* SCROLLBAR */
::-webkit-scrollbar{width:10px;height:10px}
::-webkit-scrollbar-track{background:var(--bg-0)}
::-webkit-scrollbar-thumb{background:var(--bg-2);border-radius:5px}
::-webkit-scrollbar-thumb:hover{background:#cbd5e1}

/* SIDEBAR */
section[data-testid="stSidebar"]{
    background:#fafafd!important;
    border-right:1px solid var(--border)!important;
}
section[data-testid="stSidebar"] *{color:var(--text-1)}
.sb-brand{
    display:flex;align-items:center;gap:10px;padding:4px 0 18px;
    border-bottom:1px solid var(--border);margin-bottom:18px;
}
.sb-mark{
    width:34px;height:34px;border-radius:10px;
    background:linear-gradient(135deg,#2563eb,#60a5fa);
    display:flex;align-items:center;justify-content:center;
    color:#fff;font-weight:800;font-size:1rem;
    box-shadow:0 0 20px var(--accent-glow);
}
.sb-brand-txt{font-family:'Space Grotesk',sans-serif;font-size:1.05rem;font-weight:700;color:var(--text-0)}
.sb-brand-sub{font-size:0.68rem;color:var(--text-3);letter-spacing:0.1em;text-transform:uppercase;margin-top:1px}

.sb-sect-label{
    font-size:0.68rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;
    color:var(--text-3);margin:22px 0 10px;display:flex;align-items:center;gap:6px;
}
.hist-item{
    background:var(--bg-1);border:1px solid var(--border);
    border-radius:10px;padding:12px 14px;margin-bottom:8px;
    transition:all 0.15s;font-size:0.8rem;
}
.hist-item:hover{border-color:var(--border-hi);transform:translateX(2px)}
.hist-topic{color:var(--text-0);font-weight:500;line-height:1.4;margin-bottom:6px;
    overflow:hidden;text-overflow:ellipsis;display:-webkit-box;
    -webkit-line-clamp:2;-webkit-box-orient:vertical;
}
.hist-meta{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.hist-time{font-size:0.7rem;color:var(--text-3);font-family:'JetBrains Mono',monospace}
.hist-score{
    font-size:0.65rem;font-weight:700;padding:2px 7px;
    border-radius:4px;background:rgba(37,99,235,0.12);color:var(--accent-2);
    border:1px solid rgba(37,99,235,0.25);
}

/* NAV */
.aura-nav{
    display:flex;align-items:center;justify-content:space-between;
    padding:0 44px;height:68px;background:rgba(255,255,255,0.85);
    border-bottom:1px solid var(--border);
    position:sticky;top:0;z-index:100;backdrop-filter:blur(20px);
}
.aura-logo{
    display:flex;align-items:center;gap:12px;
}
.logo-mark{
    width:36px;height:36px;border-radius:10px;
    background:linear-gradient(135deg,#2563eb 0%,#60a5fa 100%);
    display:flex;align-items:center;justify-content:center;
    font-size:1rem;color:#fff;font-weight:800;
    box-shadow:0 0 24px var(--accent-glow);
}
.logo-txt{
    font-family:'Space Grotesk',sans-serif;
    font-size:1.15rem;font-weight:700;color:var(--text-0);letter-spacing:-0.02em;
}
.logo-txt span{color:var(--accent-2)}
.nav-right{display:flex;align-items:center;gap:10px}
.nav-pill{
    font-size:0.7rem;font-weight:600;letter-spacing:0.04em;
    padding:6px 12px;border-radius:999px;
    background:rgba(37,99,235,0.08);color:var(--accent-2);
    border:1px solid rgba(37,99,235,0.2);
    display:inline-flex;align-items:center;gap:6px;
}
.nav-pill.gray{background:var(--bg-1);color:var(--text-2);border-color:var(--border)}
.nav-dot{width:6px;height:6px;border-radius:50%;background:var(--success);
    box-shadow:0 0 8px var(--success);animation:dot-pulse 2s infinite;}
@keyframes dot-pulse{0%,100%{opacity:1}50%{opacity:0.4}}

/* HERO */
.hero-section{
    display:flex;flex-direction:column;align-items:center;justify-content:flex-start;
    padding:48px 24px 24px;
    background:
        radial-gradient(ellipse 800px 500px at 50% 20%, rgba(37,99,235,0.06) 0%, transparent 70%),
        var(--bg-0);
    position:relative;overflow:hidden;
}
.hero-grid-bg{display:none}
.hero-glow{display:none}

.hero-eyebrow{
    display:inline-flex;align-items:center;gap:7px;
    font-size:0.65rem;font-weight:600;letter-spacing:0.12em;text-transform:uppercase;
    color:var(--accent);padding:5px 12px;border-radius:999px;
    background:var(--accent-soft);border:1px solid rgba(37,99,235,0.18);
    margin-bottom:16px;z-index:2;position:relative;
}
.hero-eyebrow-dot{width:5px;height:5px;border-radius:50%;background:var(--accent);
    box-shadow:0 0 6px var(--accent-glow);}
.hero-title{
    font-family:'Space Grotesk',sans-serif;
    font-size:1.65rem;
    font-weight:700;letter-spacing:-0.025em;
    text-align:center;line-height:1.2;
    margin-bottom:8px;max-width:560px;z-index:2;position:relative;color:var(--text-0);
}
.hero-title .t-grad{
    background:linear-gradient(135deg,#2563eb 0%,#60a5fa 100%);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
    background-clip:text;
}
.hero-sub{
    font-size:0.88rem;color:var(--text-2);text-align:center;
    max-width:480px;line-height:1.55;margin-bottom:28px;z-index:2;position:relative;
    font-weight:400;
}

/* INPUT */
.input-label-row{
    display:flex;align-items:center;gap:7px;
    font-size:0.7rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;
    color:var(--accent);margin-bottom:10px;
}
div[data-testid="stTextInput"]{
    background:#ffffff;
    border:1px solid var(--border);border-radius:14px;
    padding:4px 6px;
    box-shadow:0 10px 40px -15px rgba(15,23,42,0.12),0 0 0 1px rgba(37,99,235,0.05);
    transition:all 0.2s;
}
div[data-testid="stTextInput"]:focus-within{
    border-color:var(--accent);
    box-shadow:0 10px 40px -15px rgba(37,99,235,0.25),0 0 0 3px rgba(37,99,235,0.1);
}
div[data-testid="stTextInput"]>div{background:transparent!important;border:none!important;box-shadow:none!important}
div[data-testid="stTextInput"] input{
    background:transparent!important;border:none!important;
    color:var(--text-0)!important;
    font-size:0.98rem!important;padding:13px 16px!important;width:100%!important;
    font-family:'Inter',sans-serif!important;font-weight:400!important;
}
div[data-testid="stTextInput"] input:focus{
    outline:none!important;box-shadow:none!important;
}
div[data-testid="stTextInput"] input::placeholder{color:var(--text-3)!important}

/* PRIMARY BUTTON */
div[data-testid="stButton"] button[kind="primary"]{
    background:linear-gradient(135deg,#2563eb 0%,#3b82f6 100%)!important;
    color:#fff!important;border:none!important;border-radius:12px!important;
    font-weight:600!important;font-size:0.95rem!important;padding:12px 22px!important;
    width:100%!important;cursor:pointer!important;
    transition:all 0.2s!important;letter-spacing:-0.01em!important;
    box-shadow:0 6px 20px -8px var(--accent-glow)!important;
    font-family:'Inter',sans-serif!important;
}
div[data-testid="stButton"] button[kind="primary"]:hover{
    transform:translateY(-2px)!important;
    box-shadow:0 16px 40px -10px var(--accent-glow),0 0 0 1px rgba(37,99,235,0.3) inset!important;
}
div[data-testid="stButton"] button[kind="primary"]:active{transform:translateY(0)!important}

/* EXAMPLE CARDS */
.examples-wrap{max-width:720px;margin:18px auto 0;z-index:2;position:relative}
.examples-label{
    font-size:0.65rem;color:var(--text-3);text-transform:uppercase;letter-spacing:0.12em;
    margin-bottom:10px;text-align:center;font-weight:600;
}
div[data-testid="stButton"] button[kind="secondary"]{
    background:#ffffff!important;
    border:1px solid var(--border)!important;
    color:var(--text-1)!important;border-radius:999px!important;
    font-size:0.78rem!important;font-weight:500!important;padding:8px 14px!important;
    transition:all 0.15s!important;text-align:center!important;
    line-height:1.3!important;min-height:unset!important;
    white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important;
}
div[data-testid="stButton"] button[kind="secondary"]:hover{
    background:var(--accent-soft)!important;color:var(--accent)!important;
    border-color:var(--border-hi)!important;
}

/* FEATURE STRIP */
.features-strip{
    display:grid;grid-template-columns:repeat(4,1fr);gap:14px;
    max-width:900px;margin:32px auto 40px;z-index:2;position:relative;
}
.feat{
    background:#ffffff;border:1px solid var(--border);
    border-radius:12px;padding:18px;backdrop-filter:blur(10px);
    transition:all 0.2s;
}
.feat:hover{border-color:var(--border-hi);transform:translateY(-2px)}
.feat-icon{
    width:36px;height:36px;border-radius:9px;
    background:rgba(37,99,235,0.1);border:1px solid rgba(37,99,235,0.2);
    display:flex;align-items:center;justify-content:center;
    color:var(--accent-2);font-size:16px;margin-bottom:10px;
}
.feat-title{font-size:0.85rem;font-weight:600;color:var(--text-0);margin-bottom:4px}
.feat-desc{font-size:0.75rem;color:var(--text-2);line-height:1.5}

/* RESEARCH WRAP */
.research-wrap{max-width:1000px;margin:0 auto;padding:40px 24px 80px;}

/* TRACKER */
.tracker{
    display:flex;align-items:center;background:var(--bg-1);
    border:1px solid var(--border);border-radius:14px;
    padding:18px 26px;margin-bottom:28px;
}
.tr-step{flex:1;display:flex;align-items:center;gap:10px}
.tr-connector{flex:1;height:2px;background:var(--border);margin:0 10px;border-radius:1px;position:relative;overflow:hidden}
.tr-connector.done{background:linear-gradient(90deg,var(--accent),var(--accent-2))}
.tr-dot{
    width:32px;height:32px;border-radius:50%;
    display:flex;align-items:center;justify-content:center;
    font-size:0.75rem;font-weight:700;flex-shrink:0;
    background:var(--bg-2);color:var(--text-3);
    border:1px solid var(--border);transition:all 0.3s;
}
.tr-dot.active{
    background:linear-gradient(135deg,var(--accent),var(--accent-2));color:#fff;border-color:var(--accent-2);
    box-shadow:0 0 20px var(--accent-glow);
    animation:pulse 1.5s ease-in-out infinite;
}
.tr-dot.done{background:rgba(37,99,235,0.15);color:var(--accent-2);border-color:rgba(37,99,235,0.4)}
.tr-dot.failed{background:rgba(239,68,68,0.12);color:var(--err);border-color:rgba(239,68,68,0.4)}
.tr-label{font-size:0.78rem;color:var(--text-3);font-weight:500;white-space:nowrap}
.tr-label.active{color:var(--accent-2);font-weight:600}
.tr-label.done{color:var(--text-1)}
.tr-label.failed{color:var(--err)}
@keyframes pulse{0%,100%{box-shadow:0 0 16px var(--accent-glow)}50%{box-shadow:0 0 32px var(--accent-glow)}}

/* AGENT CARDS */
.agent-card{
    background:var(--bg-1);border:1px solid var(--border);
    border-radius:14px;margin-bottom:14px;overflow:hidden;
    transition:all 0.2s;
}
.agent-card.running{border-color:rgba(251,191,36,0.3);box-shadow:0 0 20px rgba(251,191,36,0.08)}
.agent-card.ok{border-color:rgba(37,99,235,0.2)}
.agent-card.error{border-color:rgba(239,68,68,0.3)}
.agent-card-head{
    display:flex;align-items:center;gap:14px;padding:16px 22px;
    border-bottom:1px solid var(--border);
}
.agent-icon-wrap{
    width:38px;height:38px;border-radius:10px;
    background:rgba(37,99,235,0.1);border:1px solid rgba(37,99,235,0.2);
    display:flex;align-items:center;justify-content:center;font-size:16px;color:var(--accent-2);
}
.agent-name{font-size:0.95rem;font-weight:600;color:var(--text-0)}
.agent-model-tag{
    font-size:0.68rem;font-family:'JetBrains Mono',monospace;
    color:var(--accent-2);background:rgba(37,99,235,0.1);
    padding:3px 8px;border-radius:5px;margin-left:4px;
    border:1px solid rgba(37,99,235,0.15);
}
.agent-timer{
    font-size:0.72rem;font-family:'JetBrains Mono',monospace;
    color:var(--text-3);margin-left:8px;
}
.agent-badge{
    margin-left:auto;font-size:0.7rem;font-weight:700;
    padding:4px 11px;border-radius:999px;letter-spacing:0.04em;
    display:inline-flex;align-items:center;gap:5px;
}
.badge-run{background:rgba(251,191,36,0.12);color:var(--warn);border:1px solid rgba(251,191,36,0.25)}
.badge-ok{background:rgba(37,99,235,0.12);color:var(--accent-2);border:1px solid rgba(37,99,235,0.25)}
.badge-err{background:rgba(239,68,68,0.12);color:var(--err);border:1px solid rgba(239,68,68,0.3)}
.agent-body{padding:18px 22px}
.agent-status-text{font-size:0.85rem;color:var(--text-1);display:flex;align-items:center;gap:10px}

/* LIVE TIPS */
.tips-wrap{
    background:linear-gradient(135deg,rgba(37,99,235,0.05),rgba(96,165,250,0.08));
    border:1px solid rgba(37,99,235,0.18);
    border-left:3px solid var(--accent);border-radius:10px;
    padding:14px 18px;margin-top:12px;
    font-size:0.82rem;color:var(--text-1);line-height:1.6;
}
.tips-label{
    font-size:0.65rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;
    color:var(--accent-2);margin-bottom:6px;display:flex;align-items:center;gap:6px;
}

/* ERROR CARD */
.error-wrap{
    background:rgba(239,68,68,0.04);border:1px solid rgba(239,68,68,0.2);
    border-left:3px solid var(--err);border-radius:10px;
    padding:16px 20px;margin-top:8px;
}
.error-title{
    font-size:0.88rem;font-weight:600;color:var(--err);margin-bottom:8px;
    display:flex;align-items:center;gap:6px;
}
.error-msg{font-size:0.8rem;color:var(--text-1);line-height:1.6;font-family:'JetBrains Mono',monospace;word-break:break-word}
.error-hint{font-size:0.8rem;color:var(--text-2);margin-top:10px}

/* SOURCES */
.source-item{
    display:flex;gap:14px;align-items:flex-start;padding:14px 16px;
    background:var(--bg-2);border-radius:10px;margin-bottom:10px;
    border:1px solid var(--border);transition:all 0.15s;
}
.source-item:hover{border-color:var(--border-hi);transform:translateX(2px)}
.src-num{
    font-size:0.7rem;font-weight:700;font-family:'JetBrains Mono',monospace;
    color:var(--accent-2);background:rgba(37,99,235,0.12);padding:4px 9px;
    border-radius:6px;flex-shrink:0;margin-top:1px;
    border:1px solid rgba(37,99,235,0.2);
}
.src-content{flex:1;min-width:0}
.src-title{font-size:0.92rem;font-weight:600;color:var(--text-0);margin-bottom:5px}
.src-url{
    font-size:0.74rem;font-family:'JetBrains Mono',monospace;color:var(--accent-2);
    word-break:break-all;margin-bottom:8px;display:flex;align-items:center;gap:5px;
}
.src-url a{color:var(--accent-2);text-decoration:none}
.src-url a:hover{text-decoration:underline}
.src-snippet{font-size:0.82rem;color:var(--text-2);line-height:1.55}

/* SCRAPE PREVIEW */
.scrape-preview{
    background:var(--bg-2);border-radius:10px;padding:16px 18px;
    border:1px solid var(--border);
}
.scrape-url-row{
    display:flex;align-items:center;gap:6px;
    font-size:0.74rem;font-family:'JetBrains Mono',monospace;
    color:var(--accent-2);margin-bottom:12px;word-break:break-all;
}
.scrape-text{font-size:0.84rem;color:var(--text-1);line-height:1.65}

/* METRICS */
.metrics-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:32px;}
.metric-c{
    background:var(--bg-1);border:1px solid var(--border);
    border-radius:12px;padding:20px 22px;transition:all 0.2s;position:relative;overflow:hidden;
}
.metric-c::before{
    content:"";position:absolute;top:0;left:0;right:0;height:2px;
    background:linear-gradient(90deg,var(--accent),var(--accent-2));
    opacity:0;transition:opacity 0.2s;
}
.metric-c:hover{border-color:var(--border-hi);transform:translateY(-2px)}
.metric-c:hover::before{opacity:1}
.metric-lbl{
    font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;
    color:var(--text-3);margin-bottom:12px;display:flex;align-items:center;gap:7px;
}
.metric-val{
    font-family:'Space Grotesk',sans-serif;font-size:2rem;font-weight:700;
    color:var(--text-0);letter-spacing:-0.03em;line-height:1;
}
.metric-unit{font-size:0.72rem;color:var(--text-3);margin-top:6px}

/* SCORE BADGE */
.score-hero{
    display:flex;align-items:center;justify-content:space-between;
    background:linear-gradient(135deg,rgba(37,99,235,0.1),rgba(96,165,250,0.04));
    border:1px solid rgba(37,99,235,0.25);border-radius:14px;
    padding:22px 28px;margin-bottom:28px;
    box-shadow:0 0 30px -10px var(--accent-glow);
}
.score-left{display:flex;align-items:center;gap:18px}
.score-circle{
    width:72px;height:72px;border-radius:50%;
    background:linear-gradient(135deg,#2563eb,#60a5fa);
    display:flex;align-items:center;justify-content:center;
    font-family:'Space Grotesk',sans-serif;font-size:1.6rem;font-weight:700;
    color:#fff;box-shadow:0 0 30px var(--accent-glow);
    border:2px solid rgba(255,255,255,0.1);
}
.score-info{display:flex;flex-direction:column}
.score-title{font-size:1.05rem;font-weight:600;color:var(--text-0);margin-bottom:5px}
.score-sub{font-size:0.84rem;color:var(--text-2);line-height:1.5;max-width:500px}

/* TABS */
div[data-testid="stTabs"] [data-baseweb="tab-list"]{
    background:var(--bg-1)!important;border:1px solid var(--border)!important;
    border-radius:12px 12px 0 0!important;
    gap:0!important;padding:4px!important;
}
div[data-testid="stTabs"] [data-baseweb="tab"]{
    background:transparent!important;color:var(--text-2)!important;
    border-radius:8px!important;padding:12px 20px!important;
    font-size:0.86rem!important;font-weight:500!important;
    border:none!important;transition:all 0.15s!important;
}
div[data-testid="stTabs"] [data-baseweb="tab"]:hover{color:var(--text-0)!important}
div[data-testid="stTabs"] [aria-selected="true"][data-baseweb="tab"]{
    background:rgba(37,99,235,0.1)!important;
    color:var(--accent-2)!important;
}
div[data-testid="stTabs"] [data-baseweb="tab-highlight"]{display:none!important}
div[data-testid="stTabs"] [data-baseweb="tab-panel"]{
    background:var(--bg-1)!important;border-radius:0 0 12px 12px!important;
    border:1px solid var(--border)!important;border-top:none!important;
    padding:32px!important;
}

.report-body{font-size:0.95rem;color:var(--text-1);line-height:1.8}
.report-body h1,.report-body h2,.report-body h3{
    color:var(--text-0);font-weight:600;margin:1.5em 0 0.6em;
    font-family:'Space Grotesk',sans-serif;letter-spacing:-0.02em;
}
.report-body h1{font-size:1.75rem;padding-bottom:0.4em;border-bottom:1px solid var(--border)}
.report-body h2{font-size:1.3rem}
.report-body h3{font-size:1.1rem}
.report-body p{margin-bottom:0.95em}
.report-body ul,.report-body ol{padding-left:1.5em;margin-bottom:0.95em}
.report-body li{margin-bottom:0.4em}
.report-body a{color:var(--accent-2);text-decoration:none;border-bottom:1px dotted rgba(96,165,250,0.4)}
.report-body a:hover{border-bottom-style:solid}
.report-body code{background:var(--bg-2);padding:2px 6px;border-radius:4px;font-size:0.88em;color:var(--accent-3)}

.feedback-wrap{
    border-left:3px solid var(--err);border-radius:0 10px 10px 0;
    background:rgba(239,68,68,0.04);padding:18px 22px;
}
.feedback-body{font-size:0.9rem;color:var(--text-1);line-height:1.75}

.stDownloadButton button{
    background:var(--bg-1)!important;border:1px solid var(--border)!important;
    color:var(--accent-2)!important;border-radius:10px!important;
    font-size:0.85rem!important;font-weight:500!important;padding:12px 20px!important;
    transition:all 0.15s!important;
}
.stDownloadButton button:hover{
    background:rgba(37,99,235,0.1)!important;border-color:var(--border-hi)!important;
}

/* SPINNER */
.spinner{display:inline-block;width:12px;height:12px;border:2px solid rgba(251,191,36,0.25);
    border-top-color:var(--warn);border-radius:50%;animation:spin 0.8s linear infinite;}
@keyframes spin{to{transform:rotate(360deg)}}

/* RESULT HEADER */
.result-header{
    display:flex;align-items:center;justify-content:space-between;
    margin-bottom:24px;flex-wrap:wrap;gap:16px;
}
.result-topic{
    display:flex;align-items:center;gap:12px;
}
.result-topic-mark{
    width:40px;height:40px;border-radius:10px;
    background:rgba(37,99,235,0.12);border:1px solid rgba(37,99,235,0.25);
    display:flex;align-items:center;justify-content:center;color:var(--accent-2);font-size:17px;
}
.result-topic-txt{
    font-family:'Space Grotesk',sans-serif;font-size:1.25rem;font-weight:600;color:var(--text-0);
    letter-spacing:-0.02em;max-width:600px;
}

@media (max-width:768px){
    .features-strip{grid-template-columns:repeat(2,1fr)}
    .metrics-grid{grid-template-columns:repeat(2,1fr)}
    .aura-nav{padding:0 20px}
    .nav-right .nav-pill:not(:first-child){display:none}
}
</style>
""", unsafe_allow_html=True)

# ─────────── NAV ───────────
st.markdown("""
<div class="aura-nav">
  <div class="aura-logo">
    <div class="logo-mark">✦</div>
    <div>
      <div class="logo-txt">Intelligent<span> Research Agent</span></div>
    </div>
  </div>
  <div class="nav-right">
    <span class="nav-pill"><span class="nav-dot"></span>Live</span>
    <span class="nav-pill">4-Agent Pipeline</span>
    <span class="nav-pill gray">Groq · Gemini · Cohere · Tavily</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────── STATE ───────────
if "state" not in st.session_state:
    st.session_state.state = {"search_results":"","reader_results":"","report":"","feedback":""}
if "execution_times" not in st.session_state:
    st.session_state.execution_times = {}
if "parsed_sources" not in st.session_state:
    st.session_state.parsed_sources = []
if "scraped_url" not in st.session_state:
    st.session_state.scraped_url = ""
if "history" not in st.session_state:
    st.session_state.history = []
if "current_topic" not in st.session_state:
    st.session_state.current_topic = ""
if "preset_topic" not in st.session_state:
    st.session_state.preset_topic = ""
if "errors" not in st.session_state:
    st.session_state.errors = {}
if "model_picks" not in st.session_state:
    st.session_state.model_picks = {
        stage: {"provider": prov, "model": mdl}
        for stage, (prov, mdl) in DEFAULT_MODELS.items()
    }

# ─────────── HELPERS ───────────
EXAMPLES = [
    "Agentic RAG vs Traditional RAG",
    "Impact of quantum computing on cryptography",
    "Latest advances in multi-agent AI systems",
    "Edge AI vs cloud AI tradeoffs 2026",
    "Open-source vs proprietary LLMs comparison",
    "Trends in autonomous driving safety 2026",
]

TIPS = [
    "The Search Agent runs 2 parallel Tavily queries with different angles for broader coverage.",
    "The Reader Agent uses FAISS vector search to pull only the most relevant chunks — saving 40-60% tokens.",
    "The Writer synthesizes a structured report with introduction, key findings, conclusion, and sources.",
    "The Critic scores the report 0-10 across accuracy, structure, clarity, citations, and depth.",
    "If the critic score is <8/10, the Writer gets feedback and revises once before finalizing.",
    "All four agents share a TypedDict state through LangGraph — no shared memory, no race conditions.",
]

def parse_sources(raw):
    sources = []
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
    if sources: return sources
    url_blocks = re.findall(r"'url':\s*'(https?://[^']+)'.*?'title':\s*'([^']+)'.*?'content':\s*'([^']{0,300})'", raw, re.DOTALL)
    for i, (url, title, content) in enumerate(url_blocks, 1):
        sources.append({"num": i, "title": title.strip(), "url": url.strip(), "snippet": content.strip()[:220]})
    if sources: return sources
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
    if m: return m.group(1)
    m2 = re.search(r"https?://[^\s'\"<>]+", raw)
    return m2.group(0).rstrip('.,)') if m2 else ""

def classify_error(exc):
    msg = str(exc)
    if "503" in msg or "UNAVAILABLE" in msg.upper() or "overloaded" in msg.lower():
        return "overload", "The model provider is temporarily overloaded. This is usually transient — try again in a moment."
    if "429" in msg or "rate limit" in msg.lower() or "quota" in msg.lower():
        return "rate_limit", "Rate limit or quota exceeded. Wait a minute and retry, or check your API dashboard."
    if "401" in msg or "403" in msg or "api key" in msg.lower() or "unauthorized" in msg.lower():
        return "auth", "Authentication failed. Check that your API keys in `.env` are valid and have access."
    if "model" in msg.lower() and ("not found" in msg.lower() or "404" in msg):
        return "model", "The model identifier isn't available on your account. Pick a different model in `agents.py`."
    if "timeout" in msg.lower() or "timed out" in msg.lower():
        return "timeout", "The request timed out. The source site may be slow or blocking us."
    return "unknown", "An unexpected error occurred. Full details below."

def safe_invoke(fn, *, retries=2, backoff=3):
    last_exc = None
    for attempt in range(retries + 1):
        try:
            return fn(), None
        except Exception as e:
            last_exc = e
            kind, _ = classify_error(e)
            if kind in ("overload", "rate_limit", "timeout") and attempt < retries:
                time.sleep(backoff * (attempt + 1))
                continue
            return None, e
    return None, last_exc

def render_tracker(step, failed_at=None):
    steps = [
        ("ti-search","Search"),("ti-browser","Reader"),
        ("ti-pencil","Writer"),("ti-eye","Critic")
    ]
    parts = []
    for i,(icon,label) in enumerate(steps,1):
        if failed_at == i:
            dc = "failed"; text = '<i class="ti ti-x" style="font-size:13px"></i>'
        elif step == i:
            dc = "active"; text = str(i)
        elif step > i:
            dc = "done"; text = '<i class="ti ti-check" style="font-size:13px"></i>'
        else:
            dc = ""; text = str(i)
        parts.append(f"""<div class="tr-step">
          <div class="tr-dot {dc}">{text}</div>
          <span class="tr-label {dc}"><i class="ti {icon}" style="font-size:14px;margin-right:4px"></i>{label}</span>
        </div>""")
        if i < len(steps):
            conn_cls = "done" if step > i else ""
            parts.append(f'<div class="tr-connector {conn_cls}"></div>')
    return '<div class="tracker">' + "".join(parts) + '</div>'

def render_running_card(icon, name, model, status_text, elapsed=None, tip=None):
    tm = f'<span class="agent-timer">{elapsed:.1f}s</span>' if elapsed is not None else ""
    tip_html = f'<div class="tips-wrap"><div class="tips-label"><i class="ti ti-bulb" style="font-size:11px"></i>Did you know?</div>{tip}</div>' if tip else ""
    return f"""<div class="agent-card running"><div class="agent-card-head">
      <div class="agent-icon-wrap"><i class="ti {icon}"></i></div>
      <span class="agent-name">{name}</span><span class="agent-model-tag">{model}</span>{tm}
      <span class="agent-badge badge-run"><span class="spinner"></span>Running</span>
    </div><div class="agent-body">
      <div class="agent-status-text"><i class="ti ti-loader" style="font-size:14px"></i>{status_text}</div>
      {tip_html}
    </div></div>"""

def render_error_card(icon, name, model, exc):
    kind, hint = classify_error(exc)
    label = {"overload":"Model Overloaded","rate_limit":"Rate Limit Hit","auth":"Auth Failed","model":"Model Not Found","timeout":"Timeout","unknown":"Error"}[kind]
    return f"""<div class="agent-card error"><div class="agent-card-head">
      <div class="agent-icon-wrap" style="background:rgba(239,68,68,0.08);border-color:rgba(239,68,68,0.2);color:#ef4444"><i class="ti ti-alert-triangle"></i></div>
      <span class="agent-name">{name}</span><span class="agent-model-tag">{model}</span>
      <span class="agent-badge badge-err"><i class="ti ti-x" style="font-size:11px"></i>{label}</span>
    </div><div class="agent-body">
      <div class="error-wrap">
        <div class="error-title"><i class="ti ti-info-circle" style="font-size:13px"></i>What happened</div>
        <div class="error-msg">{str(exc)[:400]}</div>
        <div class="error-hint">💡 {hint}</div>
      </div>
    </div></div>"""

# ─────────── SIDEBAR ───────────
with st.sidebar:
    st.markdown("""<div class="sb-brand">
      <div class="sb-mark">✦</div>
      <div>
        <div class="sb-brand-txt">Intelligent Research</div>
        <div class="sb-brand-sub">Research Lab</div>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sb-sect-label"><i class="ti ti-history" style="font-size:12px"></i>Recent Research</div>', unsafe_allow_html=True)
    if not st.session_state.history:
        st.markdown('<div style="font-size:0.78rem;color:#64748b;padding:12px 14px;background:#f6f6fb;border:1px dashed rgba(15,23,42,0.1);border-radius:10px;line-height:1.5">No research runs yet. Run your first query to see history here.</div>', unsafe_allow_html=True)
    else:
        for i, h in enumerate(reversed(st.session_state.history[-10:])):
            score = f'<span class="hist-score">{h.get("score","—")}</span>' if h.get("score") else ""
            st.markdown(f"""<div class="hist-item">
              <div class="hist-topic">{h['topic']}</div>
              <div class="hist-meta">
                <span class="hist-time">{h['time']} · {h['duration']}s · {h['sources']} sources</span>
                {score}
              </div>
            </div>""", unsafe_allow_html=True)
        if st.button("Clear history", use_container_width=True):
            st.session_state.history = []
            st.rerun()

    st.markdown('<div class="sb-sect-label"><i class="ti ti-cpu" style="font-size:12px"></i>Models · per agent</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.72rem;color:#64748b;line-height:1.5;margin-bottom:10px">Switch providers any time. Requires the matching API key in <code style="background:#eef;padding:1px 4px;border-radius:3px">.env</code>.</div>', unsafe_allow_html=True)
    stage_labels = {"search":"Search","reader":"Reader","writer":"Writer","critic":"Critic"}
    providers = list(MODEL_CATALOG.keys())
    for stage, lbl in stage_labels.items():
        current = st.session_state.model_picks[stage]
        prov = st.selectbox(
            f"{lbl} provider", providers,
            index=providers.index(current["provider"]) if current["provider"] in providers else 0,
            key=f"prov_{stage}", label_visibility="visible",
        )
        models = MODEL_CATALOG[prov]
        mdl_idx = models.index(current["model"]) if current["model"] in models else 0
        mdl = st.selectbox(
            f"{lbl} model", models, index=mdl_idx,
            key=f"mdl_{stage}", label_visibility="collapsed",
        )
        st.session_state.model_picks[stage] = {"provider": prov, "model": mdl}

    st.markdown('<div class="sb-sect-label"><i class="ti ti-info-circle" style="font-size:12px"></i>How it works</div>', unsafe_allow_html=True)
    st.markdown("""<div style="font-size:0.78rem;color:#475569;line-height:1.7;padding:0 2px">
    Four specialized agents collaborate:<br>
    <b style="color:#2563eb">1. Search</b> — Tavily queries<br>
    <b style="color:#2563eb">2. Read</b> — FAISS extraction<br>
    <b style="color:#2563eb">3. Write</b> — Structured report<br>
    <b style="color:#2563eb">4. Critique</b> — Quality audit<br><br>
    Transient API errors retry automatically with exponential backoff.
    </div>""", unsafe_allow_html=True)

# ─────────── MAIN ───────────
has_report = bool(st.session_state.state.get("report"))

if not has_report:
    st.markdown("""
<div class="hero-section">
  <div class="hero-eyebrow">
    <span class="hero-eyebrow-dot"></span>
    Autonomous AI Research · LangGraph
  </div>
  <h1 class="hero-title">Research, <span class="t-grad">intelligently automated.</span></h1>
  <p class="hero-sub">Four specialized agents search, extract, synthesize, and verify — delivering well-cited reports in minutes.</p>
</div>
""", unsafe_allow_html=True)

    # Centered input + chips
    col1, col2, col3 = st.columns([1,2.6,1])
    with col2:
        st.markdown('<div class="input-label-row"><i class="ti ti-target" style="font-size:12px"></i>Your research topic</div>', unsafe_allow_html=True)
        if "topic_in" not in st.session_state:
            st.session_state.topic_in = "Traditional RAG vs Agentic RAG"
        topic = st.text_input("Research topic", placeholder="Ask anything — e.g., Agentic RAG vs Traditional RAG", label_visibility="collapsed", key="topic_in")
        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
        start_research = st.button("Run Autonomous Pipeline  →", type="primary", use_container_width=True)

        def _set_topic(val):
            st.session_state.topic_in = val
            st.session_state.preset_topic = val

        st.markdown('<div class="examples-wrap"><div class="examples-label">Try an example</div></div>', unsafe_allow_html=True)

        # Pill-row of examples (3 + 3)
        row1 = st.columns(3)
        row2 = st.columns(3)
        rows = [row1, row2]
        short = ["Agentic vs Traditional RAG", "Quantum computing on crypto",
                 "Multi-agent AI advances", "Edge AI vs Cloud AI 2026",
                 "Open-source vs proprietary LLMs", "Autonomous driving safety 2026"]
        full_map = dict(zip(short, EXAMPLES[:6]))
        for i, label in enumerate(short):
            with rows[i // 3][i % 3]:
                st.button(label, key=f"chip_{i}", use_container_width=True,
                          on_click=_set_topic, args=(full_map[label],))
else:
    st.markdown('<div style="max-width:1000px;margin:0 auto;padding:32px 24px 0">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,4,1])
    with col2:
        topic = st.text_input("New research topic", placeholder="Enter a new research topic to run again…", label_visibility="collapsed", key="topic_in_2")
        start_research = st.button("Run New Research  →", type="primary", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────── EXECUTION ───────────
if start_research and topic:
    st.session_state.state = {"search_results":"","reader_results":"","report":"","feedback":""}
    st.session_state.parsed_sources = []
    st.session_state.scraped_url = ""
    st.session_state.execution_times = {}
    st.session_state.errors = {}
    st.session_state.current_topic = topic
    st.session_state.preset_topic = ""
    start_total = time.time()

    st.markdown('<div class="research-wrap">', unsafe_allow_html=True)

    # Topic header
    st.markdown(f"""<div class="result-header">
      <div class="result-topic">
        <div class="result-topic-mark"><i class="ti ti-flask"></i></div>
        <div class="result-topic-txt">{topic}</div>
      </div>
    </div>""", unsafe_allow_html=True)

    tracker_ph = st.empty()
    tracker_ph.markdown(render_tracker(0), unsafe_allow_html=True)

    picks = st.session_state.model_picks

    # STAGE 1: SEARCH
    tracker_ph.markdown(render_tracker(1), unsafe_allow_html=True)
    t0 = time.time()
    s_ph = st.empty()
    search_model_tag = picks["search"]["model"]
    s_ph.markdown(render_running_card("ti-world-search", "Search Agent", search_model_tag,
        "Querying Tavily search API with 2 targeted queries…", tip=TIPS[0]), unsafe_allow_html=True)

    def _search():
        agent = build_search_agent(picks["search"]["provider"], picks["search"]["model"])
        return agent.invoke(
            {"messages":[("user", f"Search EXACTLY 2 times for recent reliable information about: {topic}")]},
            config={"recursion_limit": 6}
        )
    result, exc = safe_invoke(_search)
    st.session_state.execution_times["Search Agent"] = round(time.time()-t0, 2)

    if exc:
        s_ph.markdown(render_error_card("ti-world-search", "Search Agent", search_model_tag, exc), unsafe_allow_html=True)
        tracker_ph.markdown(render_tracker(1, failed_at=1), unsafe_allow_html=True)
        st.session_state.errors["Search Agent"] = str(exc)
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

    tool_texts = []
    for msg in result['messages']:
        if getattr(msg, 'type', None) == 'tool':
            tool_texts.append(msg.content if isinstance(msg.content, str) else str(msg.content))
    raw_search = "\n\n".join(tool_texts) if tool_texts else (result['messages'][-1].content or "")
    st.session_state.state["search_results"] = raw_search or "No results."
    st.session_state.parsed_sources = parse_sources(raw_search)

    srcs_html = ""
    for s in st.session_state.parsed_sources:
        srcs_html += f"""<div class="source-item">
          <span class="src-num">#{s['num']}</span>
          <div class="src-content">
            <div class="src-title">{s['title']}</div>
            <div class="src-url"><i class="ti ti-link" style="font-size:11px;flex-shrink:0"></i><a href="{s['url']}" target="_blank">{s['url']}</a></div>
            <div class="src-snippet">{s['snippet']}</div>
          </div></div>"""
    if not srcs_html:
        srcs_html = f'<div class="src-snippet">{raw_search[:400]}</div>'

    n = len(st.session_state.parsed_sources)
    elapsed = st.session_state.execution_times["Search Agent"]
    s_ph.markdown(f"""<div class="agent-card ok"><div class="agent-card-head">
      <div class="agent-icon-wrap"><i class="ti ti-world-search"></i></div>
      <span class="agent-name">Search Agent</span><span class="agent-model-tag">{search_model_tag}</span>
      <span class="agent-timer">{elapsed:.1f}s</span>
      <span class="agent-badge badge-ok"><i class="ti ti-check" style="font-size:11px"></i>{n} sources</span>
    </div><div class="agent-body">{srcs_html}</div></div>""", unsafe_allow_html=True)

    # STAGE 2: READER
    tracker_ph.markdown(render_tracker(2), unsafe_allow_html=True)
    t0 = time.time()
    r_ph = st.empty()
    reader_model_tag = picks["reader"]["model"]
    r_ph.markdown(render_running_card("ti-browser", "Reader Agent", reader_model_tag,
        "Selecting best URL and extracting content with FAISS RAG…", tip=TIPS[1]), unsafe_allow_html=True)

    def _read():
        agent = build_reader_agent(picks["reader"]["provider"], picks["reader"]["model"])
        return agent.invoke(
            {"messages":[("user",
                f"Scrape the single most relevant URL from these search results about '{topic}'.\n\n"
                f"Search Results:\n{st.session_state.state['search_results'][:400]}")]},
            config={"recursion_limit": 4}
        )
    result, exc = safe_invoke(_read)
    st.session_state.execution_times["Reader Agent"] = round(time.time()-t0, 2)

    if exc:
        r_ph.markdown(render_error_card("ti-browser", "Reader Agent", reader_model_tag, exc), unsafe_allow_html=True)
        tracker_ph.markdown(render_tracker(2, failed_at=2), unsafe_allow_html=True)
        st.session_state.errors["Reader Agent"] = str(exc)
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

    reader_tool_texts = []
    for msg in result['messages']:
        if getattr(msg, 'type', None) == 'tool':
            reader_tool_texts.append(to_str(msg.content))
    raw_reader = "\n\n".join(reader_tool_texts) if reader_tool_texts else to_str(result['messages'][-1].content)
    raw_reader = raw_reader or "No content."
    st.session_state.state["reader_results"] = raw_reader
    st.session_state.scraped_url = extract_url(raw_reader)

    url_row = f'<div class="scrape-url-row"><i class="ti ti-link" style="font-size:11px"></i><a href="{st.session_state.scraped_url}" target="_blank" style="color:#2563eb;text-decoration:none">{st.session_state.scraped_url}</a></div>' if st.session_state.scraped_url else ""
    preview = raw_reader[:500].replace("<","&lt;") + ("…" if len(raw_reader)>500 else "")
    elapsed = st.session_state.execution_times["Reader Agent"]
    r_ph.markdown(f"""<div class="agent-card ok"><div class="agent-card-head">
      <div class="agent-icon-wrap"><i class="ti ti-browser"></i></div>
      <span class="agent-name">Reader Agent</span><span class="agent-model-tag">{reader_model_tag}</span>
      <span class="agent-timer">{elapsed:.1f}s</span>
      <span class="agent-badge badge-ok"><i class="ti ti-check" style="font-size:11px"></i>Content extracted</span>
    </div><div class="agent-body">
      <div class="scrape-preview">{url_row}<div class="scrape-text">{preview}</div></div>
    </div></div>""", unsafe_allow_html=True)

    # STAGE 3: WRITER
    tracker_ph.markdown(render_tracker(3), unsafe_allow_html=True)
    t0 = time.time()
    w_ph = st.empty()
    writer_model_tag = picks["writer"]["model"]
    w_ph.markdown(render_running_card("ti-pencil", "Writer Chain", writer_model_tag,
        "Synthesizing research into structured report with citations…", tip=TIPS[2]), unsafe_allow_html=True)

    def _write():
        research_combined = (
            f"SEARCH RESULTS:\n{st.session_state.state['search_results']}\n\n"
            f"DETAILED SCRAPED CONTENT:\n{st.session_state.state['reader_results']}"
        )
        writer_chain = build_writer_chain(picks["writer"]["provider"], picks["writer"]["model"])
        return writer_chain.invoke({
            "topic": topic, "research": research_combined,
            "feedback": st.session_state.state.get("feedback","None")
        })
    writer_result, exc = safe_invoke(_write)
    st.session_state.execution_times["Writer Chain"] = round(time.time()-t0, 2)

    if exc:
        w_ph.markdown(render_error_card("ti-pencil", "Writer Chain", writer_model_tag, exc), unsafe_allow_html=True)
        tracker_ph.markdown(render_tracker(3, failed_at=3), unsafe_allow_html=True)
        st.session_state.errors["Writer Chain"] = str(exc)
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

    st.session_state.state["report"] = writer_result or "Error generating report."
    rp = (writer_result or "")[:300] + "…"
    elapsed = st.session_state.execution_times["Writer Chain"]
    w_ph.markdown(f"""<div class="agent-card ok"><div class="agent-card-head">
      <div class="agent-icon-wrap"><i class="ti ti-pencil"></i></div>
      <span class="agent-name">Writer Chain</span><span class="agent-model-tag">{writer_model_tag}</span>
      <span class="agent-timer">{elapsed:.1f}s</span>
      <span class="agent-badge badge-ok"><i class="ti ti-check" style="font-size:11px"></i>Report drafted</span>
    </div><div class="agent-body"><div class="scrape-text">{rp}</div></div></div>""", unsafe_allow_html=True)

    # STAGE 4: CRITIC
    tracker_ph.markdown(render_tracker(4), unsafe_allow_html=True)
    t0 = time.time()
    c_ph = st.empty()
    critic_model_tag = picks["critic"]["model"]
    c_ph.markdown(render_running_card("ti-eye", "Critic Chain", critic_model_tag,
        "Auditing report for accuracy, structure, and citations…", tip=TIPS[3]), unsafe_allow_html=True)

    def _crit():
        critic_chain = build_critic_chain(picks["critic"]["provider"], picks["critic"]["model"])
        return critic_chain.invoke({"report": st.session_state.state["report"]})
    feedback_result, exc = safe_invoke(_crit)
    st.session_state.execution_times["Critic Chain"] = round(time.time()-t0, 2)

    if exc:
        c_ph.markdown(render_error_card("ti-eye", "Critic Chain", critic_model_tag, exc), unsafe_allow_html=True)
        tracker_ph.markdown(render_tracker(4, failed_at=4), unsafe_allow_html=True)
        st.session_state.errors["Critic Chain"] = str(exc)
    else:
        st.session_state.state["feedback"] = feedback_result or "No feedback."
        sm = re.search(r'Score:\s*(\d+)/10', feedback_result or "")
        score_txt = f"{sm.group(1)}/10" if sm else "—"
        fp = (feedback_result or "")[:350] + ("…" if len(feedback_result or "")>350 else "")
        elapsed = st.session_state.execution_times["Critic Chain"]
        c_ph.markdown(f"""<div class="agent-card ok"><div class="agent-card-head">
          <div class="agent-icon-wrap"><i class="ti ti-eye"></i></div>
          <span class="agent-name">Critic Chain</span><span class="agent-model-tag">{critic_model_tag}</span>
          <span class="agent-timer">{elapsed:.1f}s</span>
          <span class="agent-badge badge-ok"><i class="ti ti-check" style="font-size:11px"></i>Score: {score_txt}</span>
        </div><div class="agent-body">
          <div class="feedback-wrap"><div class="feedback-body">{fp}</div></div>
        </div></div>""", unsafe_allow_html=True)

    st.session_state.execution_times["Total"] = round(time.time()-start_total, 2)
    tracker_ph.markdown(render_tracker(5), unsafe_allow_html=True)

    # Save history
    score_match = re.search(r'Score:\s*(\d+)/10', st.session_state.state.get("feedback",""))
    st.session_state.history.append({
        "topic": topic,
        "time": datetime.now().strftime("%H:%M"),
        "duration": st.session_state.execution_times["Total"],
        "sources": len(st.session_state.parsed_sources),
        "score": f"{score_match.group(1)}/10" if score_match else None,
    })

    st.markdown('</div>', unsafe_allow_html=True)
    st.rerun()

# ─────────── RESULTS ───────────
if st.session_state.state.get("report") and not (start_research and topic):
    et = st.session_state.execution_times
    st.markdown('<div class="research-wrap">', unsafe_allow_html=True)

    # Topic header
    st.markdown(f"""<div class="result-header">
      <div class="result-topic">
        <div class="result-topic-mark"><i class="ti ti-flask"></i></div>
        <div class="result-topic-txt">{st.session_state.current_topic}</div>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown(render_tracker(5), unsafe_allow_html=True)

    # Score hero
    score_match = re.search(r'Score:\s*(\d+)/10', st.session_state.state.get("feedback",""))
    if score_match:
        score = int(score_match.group(1))
        verdict_match = re.search(r'One Line Verdict:\s*(.+)', st.session_state.state.get("feedback",""))
        verdict = verdict_match.group(1).strip() if verdict_match else "Report completed."
        st.markdown(f"""<div class="score-hero">
          <div class="score-left">
            <div class="score-circle">{score}</div>
            <div class="score-info">
              <div class="score-title">Quality Score · {score}/10</div>
              <div class="score-sub">{verdict[:140]}</div>
            </div>
          </div>
          <div style="font-size:0.88rem;color:#64748b;display:flex;align-items:center;gap:5px">
            <i class="ti ti-clock" style="font-size:14px"></i>{et.get('Total','—')}s total
          </div>
        </div>""", unsafe_allow_html=True)

    # Metrics
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
        <div class="metric-lbl"><i class="ti ti-eye" style="font-size:12px"></i>Critic</div>
        <div class="metric-val">{et.get('Critic Chain','—')}</div>
        <div class="metric-unit">seconds</div>
      </div>
    </div>""", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📝 Research Report", "🔎 Editorial Critique", "📊 Sources & Debug"])

    topic_slug = (st.session_state.current_topic or "research").lower().replace(" ","_")[:40]
    export_payload = {
        "topic": st.session_state.current_topic,
        "generated_at": datetime.now().isoformat(),
        "report": st.session_state.state.get("report",""),
        "feedback": st.session_state.state.get("feedback",""),
        "sources": st.session_state.parsed_sources,
        "scraped_url": st.session_state.scraped_url,
        "execution_times": et,
    }

    with tab1:
        st.markdown('<div class="report-body">', unsafe_allow_html=True)
        st.markdown(st.session_state.state["report"])
        st.markdown('</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1,1,3])
        with c1:
            st.download_button("⬇ Markdown (.md)", data=st.session_state.state["report"],
                file_name=f"{topic_slug}_report.md", mime="text/markdown", use_container_width=True)
        with c2:
            st.download_button("⬇ JSON (.json)", data=json.dumps(export_payload, indent=2),
                file_name=f"{topic_slug}_report.json", mime="application/json", use_container_width=True)

    with tab2:
        if st.session_state.state.get("feedback"):
            st.markdown('<div class="feedback-wrap"><div class="feedback-body">', unsafe_allow_html=True)
            st.markdown(st.session_state.state["feedback"])
            st.markdown('</div></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#64748b;font-size:0.9rem">No critique available (critic stage may have failed).</div>', unsafe_allow_html=True)

    with tab3:
        if st.session_state.parsed_sources:
            srcs_html = ""
            for s in st.session_state.parsed_sources:
                srcs_html += f"""<div class="source-item">
                  <span class="src-num">#{s['num']}</span>
                  <div class="src-content">
                    <div class="src-title">{s['title']}</div>
                    <div class="src-url"><i class="ti ti-link" style="font-size:11px"></i><a href="{s['url']}" target="_blank">{s['url']}</a></div>
                    <div class="src-snippet">{s['snippet']}</div>
                  </div></div>"""
            st.markdown(srcs_html, unsafe_allow_html=True)
        if st.session_state.errors:
            st.markdown('<div style="margin-top:24px"><div class="sb-sect-label">Errors</div></div>', unsafe_allow_html=True)
            for k, v in st.session_state.errors.items():
                st.markdown(f'<div class="error-wrap"><div class="error-title">{k}</div><div class="error-msg">{v[:300]}</div></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
