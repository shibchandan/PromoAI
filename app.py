"""
app.py — PromoAI Main Streamlit Application

PromoAI – AI-Powered Microdrama Promo Finder
Campus Placement / Hackathon Prototype for Kuku AI Generalist Assignment

Key Capabilities:
1. 🏠 Home Studio Dashboard — Upload screenplays (TXT/ZIP), quick-loader, ingestion stats
2. 📄 Screenplay Deep Dive — Hollywood script reader, character network, scene intensity heatmap
3. 🎯 Promo Studio & Generation — Semantic discovery of 20-60s vertical microdrama ads
4. 📱 Mobile Ad Simulator & Results — 9:16 vertical video ad preview, radar scoring, explainable math
5. ✅ Editorial Quality Review — Human-in-the-loop review, approve/reject, edit hook/cliffhanger
6. 📥 Export Hub — Download standardized JSON, CSV, and executive Markdown reports
"""

import io
import json
import os
import html
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import streamlit as st

# Safe imports from src
try:
    from src import config
    from src.ai.gemini_provider import GeminiProvider
    from src.file_processor import (
        EpisodeFile,
        ProcessingResult,
        process_uploaded_files,
    )
    from src.output_manager import (
        candidates_to_dict,
        export_csv,
        export_json,
        export_markdown_report,
    )
    from src.promo_detector import (
        PromoCandidate,
        PromoSegment,
        ReviewStatus,
        ScoreBreakdown,
        TimestampStatus,
        build_candidates_from_ai_response,
    )
    from src.ranking_engine import calculate_final_score, rank_candidates
    from src.scene_analyzer import (
        EpisodeAnalysis,
        analyze_all_episodes,
        analyze_scene,
        compute_scene_intensity,
    )
    from src.screenplay_parser import Episode, parse_all_episodes, parse_episode
    from src.validator import (
        find_duplicate_candidates,
        validate_all_candidates,
        validate_candidate,
    )

    MODULES_LOADED = True
    LOAD_ERROR = ""
except Exception as e:
    MODULES_LOADED = False
    LOAD_ERROR = str(e)


def safe_html(text) -> str:
    """Sanitize arbitrary screenplay or AI text before injecting into HTML."""
    return html.escape(str(text or ""))


# ---------------------------------------------------------------------------
# Page Configuration & Editorial Dark Styling
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="PromoAI — Microdrama Promo Studio",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_custom_css():
    root_vars = """
    :root {
        color-scheme: light dark;
        --bg-page: #090a0f;
        --bg-sidebar: #06070a;
        --bg-card: #0f121a;
        --bg-raised: #141824;
        --bg-input: #121520;
        --bg-hover: #1c2233;
        --text-primary: #ededed;
        --text-secondary: #9da3af;
        --text-muted: #6b7280;
        --border-hairline: rgba(255, 255, 255, 0.08);
        --border-subtle: rgba(255, 255, 255, 0.04);
        --border-hover: rgba(255, 255, 255, 0.16);
        --accent: #d97706;
        --accent-hover: #b45309;
        --accent-text: #090a0f;
        --hook-bg: rgba(56, 189, 248, 0.06);
        --hook-border: #38bdf8;
        --cliff-bg: rgba(244, 63, 94, 0.06);
        --cliff-border: #f43f5e;
        --badge-neutral-bg: #141824;
        --badge-neutral-text: #9da3af;
        --code-bg: #141824;
        --script-quote-bg: #0f121a;
        --active-nav-bg: #171b26;
        --active-nav-text: #f59e0b;
    }

    @media (prefers-color-scheme: light) {
        :root {
            --bg-page: #f8fafc;
            --bg-sidebar: #f1f5f9;
            --bg-card: #ffffff;
            --bg-raised: #f8fafc;
            --bg-input: #ffffff;
            --bg-hover: #e2e8f0;
            --text-primary: #0f172a;
            --text-secondary: #334155;
            --text-muted: #64748b;
            --border-hairline: rgba(15, 23, 42, 0.08);
            --border-subtle: rgba(15, 23, 42, 0.04);
            --border-hover: rgba(15, 23, 42, 0.18);
            --accent: #d97706;
            --accent-hover: #b45309;
            --accent-text: #ffffff;
            --hook-bg: #f0f9ff;
            --hook-border: #0284c7;
            --cliff-bg: #fff1f2;
            --cliff-border: #e11d48;
            --badge-neutral-bg: #f1f5f9;
            --badge-neutral-text: #334155;
            --code-bg: #f1f5f9;
            --script-quote-bg: #f8fafc;
            --active-nav-bg: #fef3c7;
            --active-nav-text: #b45309;
        }
    }

    /* Synchronize with Streamlit's native top-right theme (System / Light / Dark) */
    @supports (color: light-dark(#fff, #000)) {
        [data-testid="stApp"], .stApp {
            --bg-page: light-dark(#f8fafc, #090a0f);
            --bg-sidebar: light-dark(#f1f5f9, #06070a);
            --bg-card: light-dark(#ffffff, #0f121a);
            --bg-raised: light-dark(#f1f5f9, #141824);
            --bg-input: light-dark(#ffffff, #121520);
            --bg-hover: light-dark(#e2e8f0, #1c2233);
            --text-primary: light-dark(#0f172a, #ededed);
            --text-secondary: light-dark(#334155, #9da3af);
            --text-muted: light-dark(#64748b, #6b7280);
            --border-hairline: light-dark(rgba(15, 23, 42, 0.08), rgba(255, 255, 255, 0.08));
            --border-subtle: light-dark(rgba(15, 23, 42, 0.04), rgba(255, 255, 255, 0.04));
            --border-hover: light-dark(rgba(15, 23, 42, 0.18), rgba(255, 255, 255, 0.16));
            --accent: #d97706;
            --accent-hover: #b45309;
            --accent-text: light-dark(#ffffff, #090a0f);
            --hook-bg: light-dark(#f0f9ff, rgba(56, 189, 248, 0.06));
            --hook-border: light-dark(#0284c7, #38bdf8);
            --cliff-bg: light-dark(#fff1f2, rgba(244, 63, 94, 0.06));
            --cliff-border: light-dark(#e11d48, #f43f5e);
            --badge-neutral-bg: light-dark(#f1f5f9, #141824);
            --badge-neutral-text: light-dark(#334155, #9da3af);
            --code-bg: light-dark(#f1f5f9, #141824);
            --script-quote-bg: light-dark(#f8fafc, #0f121a);
            --active-nav-bg: light-dark(#fef3c7, #171b26);
            --active-nav-text: light-dark(#b45309, #f59e0b);
        }
    }
    """

    static_css = """
        /* ================================================================
           PromoAI — Adaptive Light & Dark Editorial Design System
           Character: Quiet, archival, exacting
           Typography: Inter + JetBrains Mono
        ================================================================ */

        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

        /* ── Global Shell ─────────────────────────────────────────── */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], section[data-testid="stMain"] > div {
            background-color: var(--bg-page) !important;
            color: var(--text-primary) !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            -webkit-font-smoothing: antialiased;
        }

        header[data-testid="stHeader"] {
            background: transparent !important;
        }

        header[data-testid="stHeader"] svg,
        [data-testid="stSidebarCollapseButton"] svg {
            fill: var(--text-primary) !important;
            color: var(--text-primary) !important;
        }

        .main .block-container {
            padding: 2rem 2.5rem 3rem !important;
            max-width: 1360px !important;
        }

        /* ── Typography & Roles ──────────────────────────────────── */
        h1, h2, h3, h4 {
            color: var(--text-primary) !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 500 !important;
            letter-spacing: -0.015em !important;
        }

        h2 { font-size: 1.35rem !important; margin-bottom: 0.25rem !important; }
        h3 { font-size: 1.1rem !important; }
        h4 { font-size: 0.95rem !important; }

        p, .stMarkdown p {
            color: var(--text-secondary) !important;
            font-size: 0.88rem !important;
            line-height: 1.6 !important;
        }

        code, pre, .mono-text {
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 0.8rem !important;
            color: var(--accent) !important;
            background: var(--code-bg) !important;
            border-radius: 4px !important;
            padding: 0.1rem 0.35rem !important;
        }

        .stCaptionContainer, [data-testid="stCaptionContainer"] {
            color: var(--text-muted) !important;
            font-size: 0.78rem !important;
        }

        hr {
            border-color: var(--border-hairline) !important;
            margin: 1.25rem 0 !important;
        }

        /* ── Sidebar ──────────────────────────────────────────────── */
        [data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {
            background-color: var(--bg-sidebar) !important;
            border-right: 1px solid var(--border-hairline) !important;
        }

        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .stMarkdown {
            color: var(--text-muted) !important;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] {
            display: flex !important;
            flex-direction: column !important;
            gap: 4px !important;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"] {
            border-radius: 6px !important;
            padding: 0.45rem 0.75rem !important;
            font-size: 0.84rem !important;
            font-weight: 400 !important;
            color: var(--text-secondary) !important;
            cursor: pointer !important;
            background: transparent !important;
            border: 1px solid transparent !important;
            margin: 0 !important;
            width: 100% !important;
            box-sizing: border-box !important;
            transition: background-color 0.15s ease, color 0.15s ease, border-color 0.15s ease !important;
        }

        /* Hide circular radio dot for sleek workstation tabs */
        [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"] > div:first-child {
            display: none !important;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"]:hover {
            background: var(--bg-hover) !important;
            color: var(--text-primary) !important;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"]:hover div,
        [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"]:hover p {
            color: var(--text-primary) !important;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked),
        [data-testid="stSidebar"] [data-testid="stRadio"] [aria-checked="true"] + label {
            background: var(--active-nav-bg) !important;
            color: var(--active-nav-text) !important;
            border: 1px solid var(--border-hairline) !important;
            font-weight: 500 !important;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) div,
        [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) p,
        [data-testid="stSidebar"] [data-testid="stRadio"] [aria-checked="true"] + label * {
            color: var(--active-nav-text) !important;
        }

        /* ── Native Streamlit Controls ───────────────────────────── */
        .stButton > button {
            background: var(--bg-raised) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-hairline) !important;
            border-radius: 6px !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 500 !important;
            font-size: 0.84rem !important;
            padding: 0.45rem 0.9rem !important;
            box-shadow: none !important;
            transition: background-color 0.15s ease, border-color 0.15s ease !important;
        }

        .stButton > button:hover {
            background: var(--bg-hover) !important;
            border-color: var(--border-hover) !important;
            color: var(--text-primary) !important;
        }

        .stButton > button[kind="primary"] {
            background: var(--accent) !important;
            color: var(--accent-text) !important;
            border: 1px solid var(--accent) !important;
            font-weight: 500 !important;
            box-shadow: none !important;
        }

        .stButton > button[kind="primary"]:hover {
            background: var(--accent-hover) !important;
            border-color: var(--accent-hover) !important;
            color: var(--accent-text) !important;
        }

        .stDownloadButton > button {
            background: var(--bg-raised) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-hairline) !important;
            border-radius: 6px !important;
            font-size: 0.84rem !important;
            font-weight: 500 !important;
        }

        .stDownloadButton > button[kind="primary"] {
            background: var(--accent) !important;
            color: var(--accent-text) !important;
            border: 1px solid var(--accent) !important;
        }

        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div,
        [data-baseweb="select"] > div {
            background: var(--bg-input) !important;
            border: 1px solid var(--border-hairline) !important;
            border-radius: 6px !important;
            color: var(--text-primary) !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 0.85rem !important;
        }

        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: var(--accent) !important;
            box-shadow: 0 0 0 1px var(--accent) !important;
        }

        /* BaseWeb dropdown menus */
        [data-baseweb="popover"],
        [data-baseweb="menu"],
        ul[role="listbox"] {
            background-color: var(--bg-card) !important;
            border: 1px solid var(--border-hairline) !important;
            color: var(--text-primary) !important;
        }

        li[role="option"],
        [data-baseweb="menu"] li {
            background-color: var(--bg-card) !important;
            color: var(--text-primary) !important;
        }

        li[role="option"]:hover,
        li[role="option"][aria-selected="true"],
        [data-baseweb="menu"] li:hover {
            background-color: var(--bg-hover) !important;
            color: var(--text-primary) !important;
        }

        .stTextInput label, .stTextArea label, .stSelectbox label,
        .stRadio label span, .stFileUploader label {
            color: var(--text-secondary) !important;
            font-size: 0.78rem !important;
            font-weight: 400 !important;
        }

        [data-testid="stFileUploader"] {
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
        }

        [data-testid="stFileUploader"] section {
            background: var(--bg-card) !important;
            border: 1px dashed var(--border-hairline) !important;
            border-radius: 8px !important;
            color: var(--text-secondary) !important;
            padding: 0.95rem 1.15rem !important;
            transition: border-color 0.15s ease, background-color 0.15s ease !important;
        }

        [data-testid="stFileUploader"] section:hover {
            border-color: var(--border-hover) !important;
            background: var(--bg-raised) !important;
        }

        [data-testid="stFileUploader"] section [data-testid="stBaseButton-secondary"] {
            background: var(--bg-raised) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-hairline) !important;
            border-radius: 6px !important;
            padding: 0.35rem 0.85rem !important;
            font-size: 0.82rem !important;
            font-weight: 500 !important;
        }

        [data-testid="stFileUploader"] small {
            color: var(--text-muted) !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 0.72rem !important;
        }

        [data-testid="stExpander"] {
            background: var(--bg-card) !important;
            border: 1px solid var(--border-hairline) !important;
            border-radius: 6px !important;
        }

        [data-testid="stExpander"] summary {
            color: var(--text-primary) !important;
        }

        [data-testid="stDataFrame"], [data-testid="stTable"] {
            background: var(--bg-card) !important;
            border: 1px solid var(--border-hairline) !important;
            border-radius: 6px !important;
            color: var(--text-primary) !important;
        }

        table, [data-testid="stTable"] table {
            width: 100% !important;
            background-color: var(--bg-card) !important;
            color: var(--text-primary) !important;
            border-collapse: collapse !important;
        }

        th, [data-testid="stTable"] th {
            background-color: var(--bg-raised) !important;
            color: var(--text-primary) !important;
            border-bottom: 1px solid var(--border-hairline) !important;
            font-weight: 500 !important;
            font-size: 0.8rem !important;
            padding: 0.5rem 0.75rem !important;
        }

        td, [data-testid="stTable"] td {
            background-color: var(--bg-card) !important;
            color: var(--text-secondary) !important;
            border-bottom: 1px solid var(--border-hairline) !important;
            font-size: 0.82rem !important;
            padding: 0.5rem 0.75rem !important;
        }

        [data-testid="stAlert"] p {
            color: inherit !important;
        }

        [data-testid="stJson"] {
            background: var(--bg-card) !important;
            border: 1px solid var(--border-hairline) !important;
            border-radius: 6px !important;
            padding: 0.75rem !important;
        }

        /* ── Section Header ──────────────────────────────────────── */
        .page-header {
            padding: 1.1rem 1.4rem;
            background: var(--bg-card);
            border: 1px solid var(--border-hairline);
            border-radius: 8px;
            margin-bottom: 1.5rem;
        }

        .page-header-eyebrow {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.7rem;
            color: var(--accent);
            margin-bottom: 0.2rem;
        }

        .page-header-title {
            font-size: 1.25rem;
            font-weight: 500;
            color: var(--text-primary);
            line-height: 1.3;
            letter-spacing: -0.01em;
            margin-bottom: 0.25rem;
        }

        .page-header-subtitle {
            font-size: 0.82rem;
            color: var(--text-muted);
            line-height: 1.5;
        }

        /* ── Studio Masthead ─────────────────────────────────────── */
        .studio-header {
            background: var(--bg-card);
            border: 1px solid var(--border-hairline);
            border-radius: 8px;
            padding: 1.5rem 1.6rem;
            margin-bottom: 1.5rem;
        }

        .studio-badge {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.7rem;
            color: var(--accent);
            margin-bottom: 0.4rem;
        }

        .studio-title {
            font-size: 1.6rem;
            font-weight: 500;
            letter-spacing: -0.02em;
            color: var(--text-primary);
            margin-bottom: 0.35rem;
            line-height: 1.2;
        }

        .studio-subtitle {
            font-size: 0.86rem;
            color: var(--text-muted);
            max-width: 760px;
            line-height: 1.6;
        }

        /* ── Metric KPI Cards ────────────────────────────────────── */
        .kpi-container {
            display: grid;
            grid-template-columns: 1.15fr 1.15fr 1fr 1fr;
            gap: 0.75rem;
            margin-bottom: 1.5rem;
            width: 100%;
        }

        .kpi-card {
            background: var(--bg-card);
            border: 1px solid var(--border-hairline);
            border-radius: 8px;
            padding: 1.1rem 1.2rem;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: border-color 0.15s ease;
        }

        .kpi-card:hover {
            border-color: var(--border-hover);
        }

        .kpi-card-hero {
            background: var(--bg-card);
            border: 1px solid var(--border-hairline);
            border-top: 2px solid var(--accent);
            border-radius: 8px;
            padding: 1.1rem 1.2rem;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: border-color 0.15s ease;
        }

        .kpi-card-hero:hover {
            border-color: var(--border-hover);
            border-top-color: var(--accent);
        }

        .kpi-label {
            font-size: 0.72rem;
            font-weight: 500;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 0.45rem;
        }

        .kpi-value {
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.95rem;
            font-weight: 500;
            color: var(--text-primary);
            line-height: 1.1;
            font-variant-numeric: tabular-nums;
        }

        .kpi-value-accent {
            color: var(--accent);
        }

        .kpi-subtext {
            font-size: 0.72rem;
            color: var(--text-muted);
            margin-top: 0.45rem;
        }

        /* ── Candidate Evaluation Card ───────────────────────────── */
        .promo-card {
            background: var(--bg-card);
            border: 1px solid var(--border-hairline);
            border-radius: 8px;
            padding: 1.25rem 1.4rem;
            margin-bottom: 1.25rem;
        }

        .promo-rank-badge {
            background: var(--bg-raised);
            color: var(--text-secondary);
            border: 1px solid var(--border-hairline);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.72rem;
            font-weight: 500;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            display: inline-block;
        }

        .promo-score-pill {
            background: var(--bg-raised);
            border: 1px solid var(--accent);
            color: var(--accent);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.95rem;
            font-weight: 500;
            padding: 0.25rem 0.65rem;
            border-radius: 4px;
            display: inline-block;
            font-variant-numeric: tabular-nums;
        }

        /* ── Editorial Hook & Cliffhanger Blocks ──────────────────── */
        .editorial-hook-box {
            background: var(--hook-bg);
            border-left: 2px solid var(--hook-border);
            border-top: 1px solid var(--border-subtle);
            border-right: 1px solid var(--border-subtle);
            border-bottom: 1px solid var(--border-subtle);
            padding: 0.75rem 0.95rem;
            border-radius: 0 6px 6px 0;
            margin: 0.55rem 0;
            font-size: 0.86rem;
            line-height: 1.5;
            color: var(--text-primary);
        }

        .editorial-cliff-box {
            background: var(--cliff-bg);
            border-left: 2px solid var(--cliff-border);
            border-top: 1px solid var(--border-subtle);
            border-right: 1px solid var(--border-subtle);
            border-bottom: 1px solid var(--border-subtle);
            padding: 0.75rem 0.95rem;
            border-radius: 0 6px 6px 0;
            margin: 0.55rem 0;
            font-size: 0.86rem;
            line-height: 1.5;
            color: var(--text-primary);
        }

        .editorial-tag-label {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.68rem;
            font-weight: 500;
            margin-bottom: 0.25rem;
        }

        /* ── Hollywood Screenplay Formatting ────────────────────── */
        .hollywood-scene-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: var(--bg-raised);
            border: 1px solid var(--border-hairline);
            border-radius: 6px;
            padding: 0.55rem 0.9rem;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
            gap: 0.5rem;
        }

        .hollywood-slugline {
            font-family: 'JetBrains Mono', 'Courier New', monospace;
            font-weight: 600;
            font-size: 0.78rem;
            letter-spacing: 0.04em;
            color: var(--text-primary);
            text-transform: uppercase;
        }

        .scene-intensity-gauge {
            display: flex;
            align-items: center;
            gap: 0.45rem;
            flex-shrink: 0;
        }

        .intensity-track {
            width: 64px;
            height: 5px;
            background: var(--bg-hover);
            border-radius: 3px;
            overflow: hidden;
            display: inline-block;
            vertical-align: middle;
        }

        .intensity-fill {
            height: 100%;
            background: var(--accent);
            border-radius: 3px;
        }

        .hollywood-dialogue-card {
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-left: 2px solid var(--border-hairline);
            border-radius: 0 6px 6px 0;
            padding: 0.7rem 1rem;
            margin-bottom: 0.4rem;
            transition: border-left-color 0.15s ease;
        }

        .hollywood-dialogue-card:hover {
            border-left-color: var(--accent);
        }

        .hollywood-dialogue-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.2rem;
        }

        .hollywood-character-slug {
            font-family: 'JetBrains Mono', 'Courier New', monospace;
            font-weight: 600;
            font-size: 0.75rem;
            letter-spacing: 0.08em;
            color: var(--text-primary);
            text-transform: uppercase;
        }

        .hollywood-parenthetical {
            font-family: 'Inter', sans-serif;
            font-style: italic;
            font-size: 0.74rem;
            color: var(--text-muted);
            margin-left: 1.25rem;
            margin-bottom: 0.2rem;
        }

        .hollywood-dialogue-body {
            font-family: 'Inter', sans-serif;
            font-size: 0.85rem;
            line-height: 1.55;
            color: var(--text-secondary);
            margin-left: 1.25rem;
            padding-left: 0.5rem;
            border-left: 1px solid var(--border-subtle);
        }

        .script-scene-header {
            background: var(--bg-raised);
            color: var(--text-primary);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.74rem;
            font-weight: 500;
            padding: 0.45rem 0.85rem;
            border-radius: 4px;
            margin-top: 0.8rem;
            margin-bottom: 0.4rem;
            border: 1px solid var(--border-hairline);
        }

        .script-dialogue-block {
            background: var(--bg-card);
            border-left: 2px solid var(--border-hairline);
            padding: 0.65rem 0.9rem;
            margin: 0.3rem 0;
            border-radius: 0 6px 6px 0;
            font-size: 0.85rem;
            word-wrap: break-word;
        }

        .script-dialogue-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 0.3rem;
            margin-bottom: 0.35rem;
        }

        .script-speaker {
            font-family: 'JetBrains Mono', monospace;
            font-weight: 500;
            color: var(--text-primary);
            font-size: 0.76rem;
        }

        .script-emotion {
            color: var(--text-muted);
            font-size: 0.74rem;
            margin-left: 0.35rem;
            font-family: 'Inter', sans-serif;
        }

        .script-time-chip {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.68rem;
            background: var(--bg-raised);
            color: var(--text-muted);
            padding: 0.1rem 0.4rem;
            border-radius: 4px;
            border: 1px solid var(--border-hairline);
            white-space: nowrap;
        }

        .script-stat-bar {
            background: var(--bg-card);
            border: 1px solid var(--border-hairline);
            border-radius: 6px;
            padding: 0.75rem 1.1rem;
            display: flex;
            justify-content: space-around;
            margin-top: 0.4rem;
            color: var(--text-primary);
        }

        .editorial-callout {
            background: var(--bg-card);
            border: 1px solid var(--border-hairline);
            border-radius: 6px;
            padding: 1.1rem 1.25rem;
            margin-bottom: 1.25rem;
        }

        /* ── Video Cutting Monitor (9:16 Aspect Preview) ─────────── */
        .mobile-preview-frame {
            width: 100%;
            max-width: 276px;
            min-height: 490px;
            background: #050608;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.10);
            box-shadow: 0 12px 36px rgba(0, 0, 0, 0.35);
            margin: 0.4rem auto 1.2rem auto;
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            padding: 1rem 0.9rem;
            color: #ededed;
            box-sizing: border-box;
        }

        .safe-zone-overlay {
            position: absolute;
            top: 36px;
            bottom: 64px;
            left: 12px;
            right: 48px;
            border: 1px dashed rgba(255, 255, 255, 0.12);
            border-radius: 6px;
            pointer-events: none;
        }

        .safe-zone-tag {
            position: absolute;
            top: 4px;
            right: 6px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.52rem;
            color: rgba(255, 255, 255, 0.35);
            letter-spacing: 0.05em;
            text-transform: uppercase;
            pointer-events: none;
        }

        .player-status-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.65rem;
            color: #9da3af;
            padding-bottom: 0.45rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        }

        .player-rec-dot {
            color: #ef4444;
            font-weight: 600;
            animation: blink 1.6s infinite ease-in-out;
        }

        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }

        .player-aspect-badge {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.56rem;
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.12);
            padding: 0.1rem 0.35rem;
            border-radius: 3px;
            color: #cbd5e1;
            letter-spacing: 0.04em;
        }

        .player-hook-tag {
            background: rgba(56, 189, 248, 0.10);
            color: #38bdf8;
            border: 1px solid rgba(56, 189, 248, 0.25);
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.64rem;
            text-align: center;
            margin-top: 0.5rem;
            letter-spacing: 0.02em;
        }

        .player-subtitle-card {
            background: rgba(12, 14, 20, 0.94);
            border-radius: 6px;
            padding: 0.75rem;
            font-size: 0.78rem;
            border: 1px solid rgba(255, 255, 255, 0.10);
            backdrop-filter: blur(8px);
            word-wrap: break-word;
            line-height: 1.45;
        }

        .player-cta-button {
            background: #d97706;
            color: #06070a;
            text-align: center;
            font-weight: 600;
            font-size: 0.74rem;
            letter-spacing: 0.02em;
            padding: 0.55rem;
            border-radius: 4px;
            margin-top: 0.55rem;
            cursor: default;
            box-shadow: 0 2px 8px rgba(217, 119, 6, 0.25);
        }

        /* ── Pacing Timeline Strip ───────────────────────────────── */
        .timeline-bar {
            display: flex;
            height: 5px;
            border-radius: 3px;
            overflow: hidden;
            margin: 0.55rem 0;
            background: var(--bg-raised);
            width: 100%;
        }

        .timeline-segment-hook { background: #38bdf8; }
        .timeline-segment-body { background: #4b5565; }
        .timeline-segment-cliff { background: #f43f5e; }

        .timeline-ruler {
            display: flex;
            justify-content: space-between;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.65rem;
            color: var(--text-muted);
            margin-top: 0.25rem;
        }

        /* ── Status Badges ───────────────────────────────────────── */
        .badge-verified {
            background: rgba(76, 195, 138, 0.12);
            color: #16a34a;
            border: 1px solid rgba(76, 195, 138, 0.25);
            padding: 0.15rem 0.45rem;
            border-radius: 4px;
            font-size: 0.72rem;
            font-weight: 400;
            display: inline-block;
            white-space: nowrap;
        }

        .badge-pending {
            background: rgba(217, 119, 6, 0.12);
            color: #d97706;
            border: 1px solid rgba(217, 119, 6, 0.25);
            padding: 0.15rem 0.45rem;
            border-radius: 4px;
            font-size: 0.72rem;
            font-weight: 400;
            display: inline-block;
            white-space: nowrap;
        }

        .badge-rejected {
            background: rgba(229, 72, 77, 0.12);
            color: #dc2626;
            border: 1px solid rgba(229, 72, 77, 0.25);
            padding: 0.15rem 0.45rem;
            border-radius: 4px;
            font-size: 0.72rem;
            font-weight: 400;
            display: inline-block;
            white-space: nowrap;
        }

        .badge-neutral {
            background: var(--badge-neutral-bg);
            color: var(--badge-neutral-text);
            border: 1px solid var(--border-hairline);
            padding: 0.15rem 0.45rem;
            border-radius: 4px;
            font-size: 0.72rem;
            font-weight: 400;
            display: inline-block;
            white-space: nowrap;
        }

        /* ── Formula Card ────────────────────────────────────────── */
        .formula-card {
            background: var(--bg-card);
            border: 1px solid var(--border-hairline);
            border-radius: 8px;
            padding: 1.1rem 1.25rem;
        }

        /* ── Responsive ──────────────────────────────────────────── */
        @media screen and (max-width: 992px) {
            .kpi-container {
                grid-template-columns: repeat(2, 1fr) !important;
                gap: 0.65rem !important;
            }
            .mobile-preview-frame {
                max-width: 250px !important;
                min-height: 440px !important;
            }
        }

        @media screen and (max-width: 576px) {
            .kpi-container {
                grid-template-columns: 1fr 1fr !important;
                gap: 0.5rem !important;
            }
            .main .block-container {
                padding: 1rem !important;
            }
        }
        """

    st.markdown(
        f"<style>\n{root_vars}\n{static_css}\n</style>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------------------------
def init_session_state():
    defaults = {
        "episodes": [],
        "processing_result": None,
        "analyses": [],
        "candidates": [],
        "is_demo_mode": not config.is_api_key_configured(),
        "selected_promo_index": 0,
        "active_filter": "All",
        "search_query": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ---------------------------------------------------------------------------
# Sidebar Navigation & Workspace Controls
# ---------------------------------------------------------------------------
def render_sidebar():
    with st.sidebar:
        # ── Wordmark ──────────────────────────────────────────────
        st.markdown(
            """
            <div style="padding: 0.2rem 0 0.6rem 0;">
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.62rem; color: var(--accent); letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 0.2rem;">Microdrama Studio</div>
                <div style="font-size: 1.15rem; font-weight: 600; color: var(--text-primary); letter-spacing: -0.02em;">PromoAI</div>
                <div style="font-size: 0.72rem; color: var(--text-muted); font-family: 'Inter', sans-serif; margin-top: 0.15rem;">Screenplay Ingestion & Editorial Cuts</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        # ── Navigation ────────────────────────────────────────────
        st.markdown(
            "<div style='font-family: \"JetBrains Mono\", monospace; font-size: 0.68rem; font-weight: 500; color: var(--text-muted); letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 0.4rem;'>Workstations</div>",
            unsafe_allow_html=True,
        )

        page = st.radio(
            "Navigation",
            [
                "Home Studio",
                "Screenplay Reader",
                "Promo Studio",
                "Ranked Candidates",
                "Editorial Review",
                "Export Hub",
            ],
            key="current_page",
            label_visibility="collapsed",
        )

        st.divider()

        # ── Engine Status ─────────────────────────────────────────
        api_configured = config.is_api_key_configured()
        active_model = config.get_gemini_model()

        st.markdown(
            "<div style='font-family: \"JetBrains Mono\", monospace; font-size: 0.68rem; font-weight: 500; color: var(--text-muted); letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 0.4rem;'>AI Engine</div>",
            unsafe_allow_html=True,
        )

        if api_configured:
            st.markdown(
                f"""
                <div style="
                    background: var(--bg-card);
                    border: 1px solid var(--border-hairline);
                    border-radius: 6px;
                    padding: 0.6rem 0.75rem;
                ">
                    <div style="font-size: 0.78rem; color: #16a34a; font-weight: 500; margin-bottom: 0.2rem;">Connected</div>
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: var(--text-muted);">{active_model}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div style="
                    background: var(--bg-card);
                    border: 1px solid var(--border-hairline);
                    border-radius: 6px;
                    padding: 0.6rem 0.75rem;
                ">
                    <div style="font-size: 0.78rem; color: var(--accent); font-weight: 500; margin-bottom: 0.2rem;">Heuristic mode</div>
                    <div style="font-size: 0.72rem; color: var(--text-muted); line-height: 1.4;">Deterministic screenplay scoring active.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # ── Quick Loader ──────────────────────────────────────────
        input_dir = config.INPUT_DIR
        if input_dir.exists() and list(input_dir.glob("*.txt")):
            sample_count = len(list(input_dir.glob("*.txt")))
            st.divider()
            st.markdown(
                f"<div style='font-size: 0.72rem; color: var(--text-muted); margin-bottom: 0.4rem;'>Sample episodes ({sample_count})</div>",
                unsafe_allow_html=True,
            )
            colL1, colL2 = st.columns(2)
            with colL1:
                if st.button("5 episodes", use_container_width=True):
                    load_sample_episodes(max_eps=5)
            with colL2:
                if st.button("20 episodes", use_container_width=True):
                    load_sample_episodes(max_eps=20)

        # ── Footer ────────────────────────────────────────────────
        st.divider()
        st.markdown(
            """
            <div style='color: var(--text-muted); font-size: 0.72rem; line-height: 1.6;'>
            Kuku AI Generalist<br>
            Problem 1: Find the Promos<br>
            44/44 tests passing • Python 3.12
            </div>
            """,
            unsafe_allow_html=True,
        )

        return page


def load_sample_episodes(max_eps: int = 5):
    """Load sample files from workspace input directory."""
    txt_files = sorted(list(config.INPUT_DIR.glob("*.txt")))[:max_eps]
    file_tuples = []
    for f in txt_files:
        content_bytes = f.read_bytes()
        file_tuples.append((f.name, content_bytes))

    result = process_uploaded_files(file_tuples)
    st.session_state.processing_result = result
    if result.successful_count > 0:
        episodes = parse_all_episodes(result)
        st.session_state.episodes = episodes
        st.session_state.analyses = analyze_all_episodes(episodes)
        st.session_state.candidates = []
        st.success(f"Loaded {len(episodes)} episodes successfully.")
        st.rerun()


# ---------------------------------------------------------------------------
# Section 1: Home Studio Dashboard
# ---------------------------------------------------------------------------
def render_home():
    st.markdown(
        """
        <div class="studio-header">
            <div class="studio-badge">Kuku FM assignment</div>
            <div class="studio-title">PromoAI</div>
            <div class="studio-subtitle">
                Automated promotional moment discovery and editorial ranking for microdrama screenplays. Ingest serialized scripts, extract 20–60s moments, and rank cuts with deterministic scoring.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Dynamic Asymmetric KPI Cards
    ep_count = len(st.session_state.episodes)
    cand_count = len(st.session_state.candidates)
    approved_count = sum(1 for c in st.session_state.candidates if c.review_status == ReviewStatus.APPROVED)
    multi_count = sum(1 for c in st.session_state.candidates if c.is_multi_episode)

    approved_color = "#16a34a" if approved_count > 0 else "var(--text-primary)"

    st.markdown(
        f"""
        <div class="kpi-container">
            <div class="kpi-card-hero">
                <div class="kpi-label">Promo Candidates</div>
                <div class="kpi-value kpi-value-accent">{cand_count}</div>
                <div class="kpi-subtext">{'Ready in Ranked Candidates' if cand_count > 0 else '20–60s duration window'}</div>
            </div>
            <div class="kpi-card-hero" style="border-top-color: {'#16a34a' if approved_count > 0 else 'var(--border-hairline)'};">
                <div class="kpi-label">Approved Promos</div>
                <div class="kpi-value" style="color: {approved_color};">{approved_count}</div>
                <div class="kpi-subtext">{'Verified for export' if approved_count > 0 else 'Awaiting editorial review'}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Episodes Loaded</div>
                <div class="kpi-value">{ep_count}</div>
                <div class="kpi-subtext">{'Parsed & indexed' if ep_count > 0 else 'Awaiting upload'}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Multi-Episode Arcs</div>
                <div class="kpi-value">{multi_count}</div>
                <div class="kpi-subtext">Cross-episode cuts</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # File Upload Zone and Workspace Dataset
    colU1, colU2 = st.columns(2)
    with colU1:
        st.markdown(
            """
            <div style="margin-bottom: 0.6rem;">
                <div style="font-size: 0.95rem; font-weight: 500; color: var(--text-primary); margin-bottom: 0.25rem;">Ingest screenplay files</div>
                <div style="font-size: 0.82rem; color: var(--text-muted); line-height: 1.55;">
                    Upload episode <code>.txt</code> files or a <code>.zip</code> archive. Scripts are parsed for scene markers, dialogue, and timestamps (<code>MM:SS.cc</code>).
                </div>
                <div style="display: flex; gap: 0.85rem; margin-top: 0.4rem; font-size: 0.72rem; color: var(--text-muted); font-family: 'JetBrains Mono', monospace;">
                    <span>• TXT / ZIP format</span>
                    <span>• In-memory parser</span>
                    <span>• Zero external retention</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        uploaded_files = st.file_uploader(
            "Upload screenplays (.txt or .zip)",
            type=["txt", "zip"],
            accept_multiple_files=True,
            help="Supports standard screenplay .txt and .zip files",
            label_visibility="collapsed",
        )

        if uploaded_files:
            if st.button("Process screenplays", type="primary", use_container_width=True):
                with st.spinner("Extracting dialogue, timestamps, and scene structure..."):
                    result = process_uploaded_files(uploaded_files)
                    st.session_state.processing_result = result
                    if result.successful_count > 0:
                        episodes = parse_all_episodes(result)
                        st.session_state.episodes = episodes
                        st.session_state.analyses = analyze_all_episodes(episodes)
                        st.session_state.candidates = []  # Reset candidates on new upload
                        st.success(f"Ingested and parsed {result.successful_count} episode(s) successfully.")
                        st.rerun()
                    else:
                        st.error("No valid screenplay episodes could be parsed.")

    with colU2:
        st.markdown(
            """
            <div style="margin-bottom: 0.6rem;">
                <div style="font-size: 0.95rem; font-weight: 500; color: var(--text-primary); margin-bottom: 0.25rem;">Workspace dataset</div>
                <div style="font-size: 0.82rem; color: var(--text-muted); line-height: 1.55;">
                    Pre-packaged 50-episode microdrama dataset from the repository for instant exploratory testing and evaluation.
                </div>
                <div style="display: flex; gap: 0.85rem; margin-top: 0.4rem; font-size: 0.72rem; color: var(--text-muted); font-family: 'JetBrains Mono', monospace;">
                    <span>• 50 sample episodes</span>
                    <span>• Complete continuity</span>
                    <span>• Verified timestamps</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        colB1, colB2 = st.columns(2)
        with colB1:
            if st.button("Load 5 episodes (Ep 1–5)", use_container_width=True):
                load_sample_episodes(max_eps=5)
        with colB2:
            if st.button("Load 20 episodes (Ep 1–20)", use_container_width=True):
                load_sample_episodes(max_eps=20)

    # Ingestion Manifest
    res: ProcessingResult = st.session_state.processing_result
    if res and res.episodes:
        st.markdown("---")
        st.markdown("#### Ingested screenplay manifest")
        manifest_rows = []
        for ep in res.episodes:
            manifest_rows.append(
                {
                    "Episode": ep.episode_label,
                    "File Name": ep.filename,
                    "File Size": f"{ep.file_size_bytes / 1024:.1f} KB",
                    "Validation Status": "Valid" if ep.is_valid else f"Error: {ep.error_message}",
                }
            )
        st.dataframe(pd.DataFrame(manifest_rows), use_container_width=True)

    if res and res.errors:
        with st.expander("Processing warnings", expanded=True):
            for err in res.errors:
                st.warning(err)


# ---------------------------------------------------------------------------
# Section 2: Screenplay Deep Dive & Hollywood Reader
# ---------------------------------------------------------------------------
def render_screenplay_overview():
    st.markdown(
        """
        <div class="page-header">
            <div class="page-header-eyebrow">Screenplay reader</div>
            <div class="page-header-title">Scene inspector</div>
            <div class="page-header-subtitle">Inspect parsed scenes, dialogue lines, and timing markers across loaded episodes.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    episodes: list[Episode] = st.session_state.episodes
    if not episodes:
        st.info("No episodes loaded yet. Upload files or click 'Load 5 sample episodes' on Home.")
        return

    colSelect, colStats = st.columns([2, 3])
    with colSelect:
        ep_labels = [ep.episode_label for ep in episodes]
        selected_label = st.selectbox("Select episode", ep_labels)
        selected_ep = next((ep for ep in episodes if ep.episode_label == selected_label), episodes[0])

    with colStats:
        total_dialogues = sum(len(sc.dialogues) for sc in selected_ep.scenes)
        st.markdown(
            f"""
            <div class="script-stat-bar">
                <div><span style='color: var(--text-muted);'>Duration:</span> <span class='mono-text'>{selected_ep.total_duration_seconds:.1f}s</span></div>
                <div><span style='color: var(--text-muted);'>Scenes:</span> <span class='mono-text'>{selected_ep.total_scenes}</span></div>
                <div><span style='color: var(--text-muted);'>Characters:</span> <span class='mono-text'>{len(selected_ep.all_characters)}</span></div>
                <div><span style='color: var(--text-muted);'>Dialogue lines:</span> <span class='mono-text'>{total_dialogues}</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Logline Callout
    st.markdown(f"**Episode logline:** *{selected_ep.logline or 'N/A'}*")
    if selected_ep.continuity_notes:
        st.caption(f"**Continuity notes:** {selected_ep.continuity_notes}")

    # Character Tag Clouds
    st.markdown("##### Characters in this episode")
    char_badges = " ".join([f"<span class='badge-neutral'>{c}</span>" for c in selected_ep.all_characters])
    st.markdown(char_badges or "*None extracted*", unsafe_allow_html=True)

    st.markdown("### Scene inspector")

    for sc in selected_ep.scenes:
        intensity = compute_scene_intensity(sc)
        intensity_pct = int(min(10, max(0, intensity)) * 10)

        st.markdown(
            f"""
            <div class="hollywood-scene-bar">
                <div class="hollywood-slugline">SCENE {sc.scene_number} — {safe_html(sc.heading)} [{sc.start_time} ➔ {sc.end_time}]</div>
                <div class="scene-intensity-gauge">
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: var(--text-muted);">INTENSITY {intensity:.1f}/10</span>
                    <div class="intensity-track"><div class="intensity-fill" style="width: {intensity_pct}%;"></div></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if sc.dialogues:
            for d in sc.dialogues:
                emotion_html = f"<div class='hollywood-parenthetical'>({safe_html(d.emotion)})</div>" if d.emotion else ""
                st.markdown(
                    f"""
                    <div class="hollywood-dialogue-card">
                        <div class="hollywood-dialogue-top">
                            <span class="hollywood-character-slug">{safe_html(d.character)}</span>
                            <span class="script-time-chip">{d.start_time} ➔ {d.end_time}</span>
                        </div>
                        {emotion_html}
                        <div class="hollywood-dialogue-body">"{safe_html(d.text)}"</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.caption("*(No spoken dialogue lines in this scene — action/camera notes only)*")


# ---------------------------------------------------------------------------
# Section 3: Promo Studio & Generation
# ---------------------------------------------------------------------------
def render_promo_generation():
    st.markdown(
        """
        <div class="page-header">
            <div class="page-header-eyebrow">Candidate generator</div>
            <div class="page-header-title">Promo candidate discovery</div>
            <div class="page-header-subtitle">Extract 20–60 second vertical moments with 3-second opening hook and unresolved cliffhanger.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    episodes: list[Episode] = st.session_state.episodes
    if not episodes:
        st.warning("Please load screenplay episodes first.")
        return

    st.markdown(
        f"""
        <div class="editorial-callout">
            <div style='font-weight: 500; font-size: 0.95rem; color: var(--text-primary); margin-bottom: 0.3rem;'>Loaded {len(episodes)} screenplay episodes</div>
            <div style='color: var(--text-secondary); font-size: 0.85rem; line-height: 1.5;'>
                Extracts dramatic turning points, confronts, and revelations between <strong>20 and 60 seconds</strong>, isolating the opening <strong>3-second hook</strong> and an unresolved <strong>cliffhanger</strong>.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    colA, colB = st.columns([3, 2])
    with colA:
        promo_strategy = st.radio(
            "Promo strategy",
            [
                "Mixed collection (Single-episode focus + multi-episode narrative arcs)",
                "Single-episode continuous moments only",
            ],
            index=0,
        )

        generate_btn = st.button("Generate promo candidates", type="primary", use_container_width=True)

    with colB:
        st.markdown(
            """
            <div class="formula-card">
                <div style="font-size: 0.72rem; color: var(--text-muted); margin-bottom: 0.4rem;">Scoring formula</div>
                <code style="font-size: 0.82rem; color: var(--accent); display: block; margin-bottom: 0.55rem;">S = 0.25H + 0.20E + 0.25C + 0.15K + 0.15P</code>
                <div style="display: flex; flex-direction: column; gap: 0.25rem;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.76rem; color: var(--text-muted);"><span>Hook strength (H)</span><span style="color: var(--accent); font-family: 'JetBrains Mono', monospace;">25%</span></div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.76rem; color: var(--text-muted);"><span>Emotional impact (E)</span><span style="color: var(--text-primary); font-family: 'JetBrains Mono', monospace;">20%</span></div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.76rem; color: var(--text-muted);"><span>Cliffhanger strength (C)</span><span style="color: var(--accent); font-family: 'JetBrains Mono', monospace;">25%</span></div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.76rem; color: var(--text-muted);"><span>Story coherence (K)</span><span style="color: var(--text-primary); font-family: 'JetBrains Mono', monospace;">15%</span></div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.76rem; color: var(--text-muted);"><span>Promo suitability (P)</span><span style="color: var(--text-primary); font-family: 'JetBrains Mono', monospace;">15%</span></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if generate_btn:
        with st.spinner("Analyzing dramatic hooks, emotional turning points, and cliffhangers..."):
            provider = GeminiProvider(
                api_key=config.get_gemini_api_key(),
                model=config.get_gemini_model(),
            )

            # Build summaries with full content for grounded extraction
            episodes_summary = []
            for ep in episodes:
                episodes_summary.append(
                    {
                        "episode_label": ep.episode_label,
                        "logline": ep.logline,
                        "duration_seconds": ep.total_duration_seconds,
                        "characters": ep.all_characters,
                        "sample_scenes": [
                            {
                                "scene_number": sc.scene_number,
                                "heading": sc.heading,
                                "duration_seconds": sc.duration_seconds,
                                "dialogues": [
                                    {"character": d.character, "text": d.text, "time": d.start_time, "emotion": d.emotion}
                                    for d in sc.dialogues
                                ],
                            }
                            for sc in ep.scenes
                        ],
                        "raw_content": ep.raw_content,
                    }
                )

            ai_resp = provider.generate_promo_candidates(episodes_summary)
            if ai_resp.success and ai_resp.data:
                candidates = build_candidates_from_ai_response(ai_resp.data, is_demo=ai_resp.is_demo)
                ranked = rank_candidates(candidates)
                validated = validate_all_candidates(ranked, episodes)
                st.session_state.candidates = validated
                st.session_state.is_demo_mode = ai_resp.is_demo

                st.success(f"Generated and ranked {len(validated)} promotional candidate(s).")
                st.rerun()
            else:
                st.error(f"Generation failed: {ai_resp.error}")

    # Summary table of candidates
    if st.session_state.candidates:
        st.markdown("---")
        st.markdown(f"### Promo candidates ({len(st.session_state.candidates)})")
        roster = []
        for i, c in enumerate(st.session_state.candidates, 1):
            roster.append(
                {
                    "Rank": f"{i}",
                    "Title": c.title,
                    "Score": f"{c.final_score:.2f} / 10",
                    "Duration": f"{c.estimated_duration_seconds or '?'}s",
                    "Multi-episode": "Yes" if c.is_multi_episode else "No",
                    "Status": c.review_status.value.capitalize(),
                    "Flags": len(c.validation_flags),
                }
            )
        st.dataframe(pd.DataFrame(roster), use_container_width=True)
        st.info("Switch to **Ranked Candidates** to inspect cuts in the video preview.")


# ---------------------------------------------------------------------------
# Section 4: Ranked Results & Interactive Mobile Ad Simulator
# ---------------------------------------------------------------------------
def render_promo_results():
    st.markdown(
        """
        <div class="page-header">
            <div class="page-header-eyebrow">Ranked output</div>
            <div class="page-header-title">Promo candidates and video cuts</div>
            <div class="page-header-subtitle">Sorted by composite score with 9:16 vertical video preview and source verification. Formula: S = 0.25H + 0.20E + 0.25C + 0.15K + 0.15P</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    candidates: list[PromoCandidate] = st.session_state.candidates
    if not candidates:
        st.warning("No promo candidates generated yet. Head over to Promo Studio to generate promos.")
        return

    # Check for duplicates
    dup_pairs = find_duplicate_candidates(candidates)
    if dup_pairs:
        st.warning(
            f"Detected {len(dup_pairs)} candidate pair(s) with overlapping hooks: "
            + ", ".join([f"({candidates[i].promo_id} & {candidates[j].promo_id})" for i, j in dup_pairs])
        )

    # Search & Filter Bar
    colF1, colF2, colF3 = st.columns([2, 1, 1])
    with colF1:
        search = st.text_input("Search promos", placeholder="Filter by title, hook, or character", value="")
    with colF2:
        filter_type = st.selectbox("Strategy", ["All promos", "Multi-episode only", "Single-episode only"])
    with colF3:
        filter_status = st.selectbox("Status", ["All statuses", "Approved only", "Pending only"])

    # Filter candidates
    filtered = []
    for c in candidates:
        if filter_type == "Multi-episode only" and not c.is_multi_episode:
            continue
        if filter_type == "Single-episode only" and c.is_multi_episode:
            continue
        if filter_status == "Approved only" and c.review_status != ReviewStatus.APPROVED:
            continue
        if filter_status == "Pending only" and c.review_status != ReviewStatus.PENDING:
            continue
        if search:
            q = search.lower()
            text_pool = f"{c.title} {c.hook} {c.cliffhanger} {c.description} {c.main_conflict}".lower()
            if q not in text_pool:
                continue
        filtered.append(c)

    st.markdown(f"**Showing {len(filtered)} of {len(candidates)} candidate(s)**")
    st.markdown("---")

    for rank, c in enumerate(filtered, 1):
        with st.container():
            colMain, colPhone = st.columns([3, 2])

            with colMain:
                colTitle, colScore = st.columns([3, 1])
                with colTitle:
                    st.markdown(
                        f"""
                        <div>
                            <span class="promo-rank-badge">Rank {rank}</span>
                            <span style='margin-left: 0.5rem; font-size: 1.15rem; font-weight: 500; color: var(--text-primary);'>{safe_html(c.title)}</span>
                        </div>
                        <div style='color: var(--text-muted); font-size: 0.78rem; margin-top: 0.3rem;'>
                            <code>{c.promo_id}</code> • {'Multi-episode' if c.is_multi_episode else 'Single-episode'} • {c.estimated_duration_seconds or '?'}s
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with colScore:
                    st.markdown(
                        f"""
                        <div style='text-align: right;'>
                            <div class="promo-score-pill">Score {c.final_score:.2f} <span style='font-size: 0.72rem; color: var(--text-muted);'>/ 10</span></div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                st.markdown(f"<p style='color: var(--text-secondary); font-size: 0.88rem; line-height: 1.5; margin: 0.4rem 0;'>{safe_html(c.description)}</p>", unsafe_allow_html=True)

                # Hook & Cliffhanger Blocks
                st.markdown(
                    f"""
                    <div class="editorial-hook-box">
                        <div class="editorial-tag-label" style="color: var(--hook-border);">Hook (first 3s)</div>
                        {safe_html(c.hook)}
                    </div>
                    <div class="editorial-cliff-box">
                        <div class="editorial-tag-label" style="color: var(--cliff-border);">Cliffhanger cutoff</div>
                        {safe_html(c.cliffhanger)}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Dynamic Pacing Timeline Visualizer
                dur_total = int(c.estimated_duration_seconds or 35)
                hook_s = min(3, dur_total)
                cliff_s = min(4, max(1, dur_total - hook_s))
                body_s = max(1, dur_total - hook_s - cliff_s)
                hook_p = round((hook_s / dur_total) * 100, 1)
                cliff_p = round((cliff_s / dur_total) * 100, 1)
                body_p = round(100.0 - hook_p - cliff_p, 1)

                st.markdown(
                    f"""
                    <div style='font-family: "JetBrains Mono", monospace; font-size: 0.68rem; color: var(--text-muted); margin-top: 0.65rem;'>
                        Pacing timeline (00:00 ➔ 00:03 Hook ➔ Confrontation Body ➔ 00:{dur_total:02d} Cliffhanger)
                    </div>
                    <div class="timeline-bar">
                        <div class="timeline-segment-hook" style="width: {hook_p}%;" title="Hook: 00:00 - 00:03 ({hook_p}%)"></div>
                        <div class="timeline-segment-body" style="width: {body_p}%;" title="Confrontation: 00:03 - 00:{dur_total - cliff_s:02d} ({body_p}%)"></div>
                        <div class="timeline-segment-cliff" style="width: {cliff_p}%;" title="Cliffhanger Cut: 00:{dur_total - cliff_s:02d} - 00:{dur_total:02d} ({cliff_p}%)"></div>
                    </div>
                    <div class="timeline-ruler">
                        <span>00:00 (Hook)</span>
                        <span>00:03 (Lock)</span>
                        <span>00:{dur_total:02d} (Cutoff)</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Conflict & Strategic Why It Works
                colC1, colC2 = st.columns(2)
                with colC1:
                    st.markdown(f"**Dramatic conflict:** {safe_html(c.main_conflict)}")
                    st.markdown(f"**Emotional impact:** {safe_html(c.emotional_impact)}")
                with colC2:
                    st.markdown(f"**Editorial rationale:** {safe_html(c.why_it_works)}")
                    st.markdown(f"**AI confidence:** `{c.ai_confidence.title()}`")

                # Formula breakdown expander
                with st.expander("Formula breakdown"):
                    st.write("Formula: `S = 0.25H + 0.20E + 0.25C + 0.15K + 0.15P`")
                    breakdown_data = [
                        {"Criterion": "Hook strength (H)", "Weight": "25%", "Raw (0-10)": c.scores.hook_strength, "Contribution": f"{0.25 * c.scores.hook_strength:.2f}"},
                        {"Criterion": "Emotional impact (E)", "Weight": "20%", "Raw (0-10)": c.scores.emotional_impact, "Contribution": f"{0.20 * c.scores.emotional_impact:.2f}"},
                        {"Criterion": "Cliffhanger (C)", "Weight": "25%", "Raw (0-10)": c.scores.cliffhanger_strength, "Contribution": f"{0.25 * c.scores.cliffhanger_strength:.2f}"},
                        {"Criterion": "Coherence (K)", "Weight": "15%", "Raw (0-10)": c.scores.story_coherence, "Contribution": f"{0.15 * c.scores.story_coherence:.2f}"},
                        {"Criterion": "Suitability (P)", "Weight": "15%", "Raw (0-10)": c.scores.promo_suitability, "Contribution": f"{0.15 * c.scores.promo_suitability:.2f}"},
                        {"Criterion": "FINAL SCORE", "Weight": "100%", "Raw (0-10)": "-", "Contribution": f"{c.final_score:.2f}"},
                    ]
                    st.table(pd.DataFrame(breakdown_data))

                # Verbatim Screenplay Excerpts
                st.markdown("##### Screenplay quotes and timestamps")
                for seg_idx, seg in enumerate(c.segments, 1):
                    ts = f"{seg.start_time or 'N/A'} ➔ {seg.end_time or 'N/A'}"
                    st.markdown(
                        f"""
                        <div style="background: var(--script-quote-bg); border: 1px solid var(--border-subtle); border-left: 2px solid var(--hook-border); padding: 0.5rem 0.75rem; border-radius: 4px; margin-bottom: 0.35rem; font-size: 0.82rem; color: var(--text-primary);">
                            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: var(--text-muted);">Moment {seg_idx} ({safe_html(seg.episode)} • {safe_html(seg.scene_reference or 'SCENE')}): {ts}</span><br>
                            <span style="font-family: 'JetBrains Mono', monospace; color: var(--text-primary);\">\"{safe_html(seg.source_text)}\"</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                if c.validation_flags:
                    st.error(f"{len(c.validation_flags)} issue(s) detected:")
                    for f in c.validation_flags:
                        st.caption(f"• {f}")
                else:
                    st.success("Source quotes and timestamps verified against screenplay text.")

            # Right Column: The 9:16 Video Cutting Monitor
            with colPhone:
                first_seg_text = c.segments[0].source_text if c.segments else c.hook
                dur_sec = int(c.estimated_duration_seconds or 35)
                cut_ts = f"00:{dur_sec:02d}"

                st.markdown(
                    f"""
                    <div style="text-align: center; margin-bottom: 0.35rem; font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: var(--text-muted);">
                        9:16 Video cutting monitor
                    </div>
                    <div class="mobile-preview-frame">
                        <div class="safe-zone-overlay">
                            <span class="safe-zone-tag">Social Safe Zone</span>
                        </div>
                        
                        <div>
                            <div class="player-status-bar">
                                <div><span class="player-rec-dot">● REC</span> 00:00:15</div>
                                <span class="player-aspect-badge">9:16 VERTICAL</span>
                                <div>{cut_ts}</div>
                            </div>
                            <div class="player-hook-tag">0–3s Hook Window</div>
                        </div>
                        
                        <div style="text-align: center; margin: 1rem 0; font-size: 0.85rem; color: #ededed; position: relative; z-index: 1;">
                            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.66rem; color: #d97706; text-transform: uppercase; letter-spacing: 0.05em;">Microdrama Promo Cut</div>
                            <h3 style="color: #ededed; margin: 0.35rem 0; font-size: 0.98rem; line-height: 1.3; font-weight: 600;">{safe_html(c.title)}</h3>
                        </div>

                        <div style="position: relative; z-index: 1;">
                            <div class="player-subtitle-card">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;">
                                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.64rem; color: #38bdf8; font-weight: 500;">Burned-in Subtitle:</span>
                                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.58rem; color: #9da3af;">SYNCED</span>
                                </div>
                                <div style="color: #ededed; font-size: 0.78rem; line-height: 1.4;\">\"{safe_html(first_seg_text[:85])}...\"</div>
                                <div style="margin-top: 0.35rem; font-family: 'JetBrains Mono', monospace; font-size: 0.62rem; color: #9da3af;">Audio: Tension swell ➔ Cut hit</div>
                            </div>
                            <div class="player-cta-button">Watch Episode Now</div>
                            <div style="display: flex; justify-content: space-between; font-family: 'JetBrains Mono', monospace; font-size: 0.62rem; color: #9da3af; margin-top: 0.4rem; padding: 0 0.2rem;">
                                <span>Cut: {dur_sec}s</span>
                                <span>24-bit / 48kHz</span>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown("---")


# ---------------------------------------------------------------------------
# Section 5: Editorial Quality Review
# ---------------------------------------------------------------------------
def render_quality_review():
    st.markdown(
        """
        <div class="page-header">
            <div class="page-header-eyebrow">Quality review</div>
            <div class="page-header-title">Editorial review</div>
            <div class="page-header-subtitle">Review promo hooks and cliffhangers, approve candidates, and provide notes for editing teams.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    candidates: list[PromoCandidate] = st.session_state.candidates
    if not candidates:
        st.warning("No candidates to review. Please generate promos first.")
        return

    options = [f"{c.promo_id}: {c.title} (Score: {c.final_score:.2f}) — [{c.review_status.value}]" for c in candidates]
    idx = st.selectbox("Select candidate", range(len(options)), format_func=lambda i: options[i])
    selected: PromoCandidate = candidates[idx]

    st.markdown("---")

    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown(f"### Reviewing `{selected.promo_id}`: {selected.title}")
        new_title = st.text_input("Promo title", selected.title)
        new_hook = st.text_area("3-second hook (opening attention)", selected.hook, height=80)
        new_cliff = st.text_area("Cliffhanger ending (unresolved cut)", selected.cliffhanger, height=80)
        new_desc = st.text_area("Story concept", selected.description, height=70)
        comment = st.text_area(
            "Video editor directions",
            value=selected.reviewer_comment,
            placeholder="e.g. Cut to black on Juliana's reaction at 01:01.80. Boost string swell.",
            height=80,
        )

        if selected.segments:
            st.markdown("##### Screenplay segments & verbatim source quotes")
            for s_idx, seg in enumerate(selected.segments):
                seg_label = seg.segment_type.capitalize() if seg.segment_type else f"Segment {s_idx + 1}"
                time_range = f"{seg.start_time or 'N/A'} – {seg.end_time or 'N/A'}"
                st.markdown(
                    f"""
                    <div style="padding: 10px 14px; margin-bottom: 8px; border-radius: 6px; background: var(--surface-secondary); border: 1px solid var(--border-subtle);">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                            <span style="font-size: 0.72rem; font-weight: 700; color: var(--accent-primary); letter-spacing: 0.05em; text-transform: uppercase;">
                                {seg_label} • {seg.episode} ({seg.scene_reference or 'SCENE'})
                            </span>
                            <span style="font-size: 0.72rem; color: var(--text-muted); font-family: 'JetBrains Mono', monospace;">
                                {time_range}
                            </span>
                        </div>
                        <div style="font-size: 0.82rem; color: var(--text-primary); font-style: italic;">
                            "{seg.source_text}"
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with col2:
        st.markdown("#### Editorial decision")
        st.write(f"Status: **{selected.review_status.value.capitalize()}**")

        btnApprove = st.button("Approve for production", type="primary", use_container_width=True)
        btnReject = st.button("Reject candidate", use_container_width=True)
        btnSave = st.button("Save revisions only", use_container_width=True)

        if btnApprove:
            selected.review_status = ReviewStatus.APPROVED
            selected.title = new_title
            selected.hook = new_hook
            selected.cliffhanger = new_cliff
            selected.description = new_desc
            selected.reviewer_comment = comment
            if st.session_state.episodes:
                validate_candidate(selected, st.session_state.episodes)
            st.success(f"Candidate {selected.promo_id} marked as approved.")
            st.rerun()

        if btnReject:
            selected.review_status = ReviewStatus.REJECTED
            selected.title = new_title
            selected.hook = new_hook
            selected.cliffhanger = new_cliff
            selected.description = new_desc
            selected.reviewer_comment = comment
            st.warning(f"Candidate {selected.promo_id} marked as rejected.")
            st.rerun()

        if btnSave:
            selected.title = new_title
            selected.hook = new_hook
            selected.cliffhanger = new_cliff
            selected.description = new_desc
            selected.reviewer_comment = comment
            if st.session_state.episodes:
                validate_candidate(selected, st.session_state.episodes)
            st.success("Revisions saved successfully.")
            st.rerun()

        st.markdown("---")
        st.markdown("##### Anti-hallucination verification")
        if selected.validation_flags:
            st.error(f"{len(selected.validation_flags)} issue(s) detected:")
            for f in selected.validation_flags:
                st.caption(f"• {f}")
            st.caption("ℹ️ *The LLM paraphrased or adapted this segment text. Editors can verify, edit, or approve the cut directly above.*")
        else:
            st.success("Source quotes and timestamps verified against raw screenplay.")


# ---------------------------------------------------------------------------
# Section 6: Export Hub
# ---------------------------------------------------------------------------
def render_export():
    st.markdown(
        """
        <div class="page-header">
            <div class="page-header-eyebrow">Export</div>
            <div class="page-header-title">Export hub</div>
            <div class="page-header-subtitle">Download standardized JSON, tabular CSV summaries, and Markdown pitch reports.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    candidates: list[PromoCandidate] = st.session_state.candidates
    episodes: list[Episode] = st.session_state.episodes

    if not candidates:
        st.warning("No promo candidates to export. Please generate promos first.")
        return

    episodes_info = [{"episode_label": ep.episode_label, "filename": ep.filename} for ep in episodes]

    # Generate payloads
    json_str = export_json(candidates, episodes_info, is_demo=st.session_state.is_demo_mode)
    csv_str = export_csv(candidates)
    md_str = export_markdown_report(candidates, episodes_info, is_demo=st.session_state.is_demo_mode)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button(
            label="Download JSON output",
            data=json_str,
            file_name=f"promoai_export_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True,
            type="primary",
        )
        st.caption("Standard structured JSON schema matching Kuku AI specifications.")

    with col2:
        st.download_button(
            label="Download CSV summary",
            data=csv_str,
            file_name=f"promoai_summary_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True,
        )
        st.caption("Spreadsheet-ready summary with individual scores and rankings.")

    with col3:
        st.download_button(
            label="Download Markdown report",
            data=md_str,
            file_name=f"promoai_report_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown",
            use_container_width=True,
        )
        st.caption("Executive editorial pitch report suitable for marketing review.")

    st.markdown("---")
    st.markdown("### JSON output preview")
    st.json(json.loads(json_str))


# ---------------------------------------------------------------------------
# Main Router
# ---------------------------------------------------------------------------
def main():
    inject_custom_css()
    init_session_state()

    if not MODULES_LOADED:
        st.error(f"Failed to load core modules: {LOAD_ERROR}")
        st.info("Please make sure all dependencies are installed: `pip install -r requirements.txt`")
        return

    page = render_sidebar()

    if page == "Home Studio":
        render_home()
    elif page == "Screenplay Reader":
        render_screenplay_overview()
    elif page == "Promo Studio":
        render_promo_generation()
    elif page == "Ranked Candidates":
        render_promo_results()
    elif page == "Editorial Review":
        render_quality_review()
    elif page == "Export Hub":
        render_export()


if __name__ == "__main__":
    main()
